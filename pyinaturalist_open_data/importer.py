"""Functions for downloading and loading inaturalist open data into a database"""
# TODO: Check local and remote timestamps to only download if a new version is available
import csv
import os
from io import FileIO
from os.path import basename, dirname, exists, expanduser, join
from tarfile import TarFile
from time import time

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from rich import print
from sqlalchemy import create_engine, insert
from sqlalchemy.exc import OperationalError

from .constants import BUCKET_NAME, DATA_DIR, DEFAULT_DB_URI, METADATA_DL_PATH, METADATA_KEY
from .models import Base, Observation, Photo, Taxon, User
from .progress import get_download_progress, get_progress

MODEL_CSV_FILES = {
    Observation: 'observations.csv',
    Photo: 'photos.csv',
    Taxon: 'taxa.csv',
    User: 'observers.csv',
}


class FlatTarFile(TarFile):
    """Extracts all archive contents to a flat base directory, ignoring archive subdirectories"""

    def extract(self, member, path="", **kwargs):
        if member.isfile():
            member.name = basename(member.name)
            super().extract(member, path, **kwargs)


class ProgressIO(FileIO):
    """File object wrapper that updates read progress"""

    def __init__(self, path, *args, **kwargs):
        self._total_size = os.path.getsize(path)
        self.progress, self.task = get_download_progress(self._total_size, 'Extracting')
        super().__init__(path, *args, **kwargs)

    def read(self, size):
        self.progress.update(self.task, advance=size)
        return super().read(size)


def download_metadata(download_path: str = METADATA_DL_PATH):
    """Download and extract metadata archive

    Args:
        download_path: Optional file path to download to
    """
    download_path = expanduser(download_path)
    os.makedirs(dirname(download_path), exist_ok=True)

    # Download combined package with authentication disabled
    if exists(download_path):
        print(f'File already exists: {download_path}')
    else:
        print(f'Downloading to: {download_path}')
        download_file(BUCKET_NAME, METADATA_KEY, download_path)

    # Extract files
    progress_file = ProgressIO(download_path)
    with FlatTarFile.open(fileobj=progress_file) as archive, progress_file.progress:
        archive.extractall(path=dirname(download_path))


def download_file(bucket_name: str, key: str, download_path: str):
    """Download a file from S3, with progress bar"""
    # Get file size for progress bar
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    response = s3.head_object(Bucket=bucket_name, Key=key)
    file_size = response['ContentLength']

    # Download file with a callback to periodically update progress
    progress, task = get_download_progress(file_size)
    with progress:
        s3.download_file(
            Bucket=bucket_name,
            Key=key,
            Filename=download_path,
            Callback=lambda n_bytes: progress.update(task, advance=n_bytes),
        )


def load_all(db_uri: str = DEFAULT_DB_URI):
    """Load contents of CSV files into a database. This is just here for convenience since it works
    with all supported DB dialects. DB-specific bulk inserts are faster, if available.
    """
    # Create tables, if they don't already exist
    engine = create_engine(db_uri, echo=True)
    print('Creating tables')
    Base.metadata.create_all(engine)

    for model in [Observation, Photo, Taxon, User]:
        try:
            load_table(engine, model)
        except OperationalError as e:
            print(e)


def load_table(engine, model):
    """Load CSV contents into a table, with progress bar"""
    csv_path = join(DATA_DIR, MODEL_CSV_FILES[model])
    print(f'Loading data from {csv_path}')

    num_lines = sum(1 for _ in open(csv_path)) - 1
    progress, task = get_progress(num_lines, f'Loading {model} data...')
    with progress, open(csv_path) as csv_file:
        reader = csv.reader(csv_file, delimiter='\t')
        next(reader)  # Skip header

        for chunk in read_chunks(reader, progress, task):
            engine.execute(insert(model), [map_columns(model, row) for row in chunk])


def read_chunks(reader, progress, task, chunksize=2000):
    """Read a CSV file in chunks"""
    chunk = []
    for i, line in enumerate(reader):
        if i % chunksize == 0 and i > 0:
            yield chunk
            del chunk[:]
            progress.update(task, advance=1)
        chunk.append(line)
    yield chunk


def map_columns(model, row):
    """Get a column mapping from model properties to row indices. Model properties are already in
    the same order as the CSV columns, but since we're using the (faster) lower-level
    ``engine.execute``, we need an explicit mapping.
    """
    return {col.name: row[i] for i, col in enumerate(model.__mapper__.columns)}


if __name__ == '__main__':
    start = time()
    download_metadata()
    load_all()
    print(f'Finished in {time() - start:.2f} seconds')
