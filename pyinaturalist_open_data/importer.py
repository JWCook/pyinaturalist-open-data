import csv
import logging

# TODO: Check local and remote timestamps to only download if a new version is available
# TODO: Progress bar callback
# TODO: Read CSVs in chunks
import os
import tarfile
from os.path import dirname, exists, expanduser, join

import boto3
from botocore.handlers import disable_signing
from sqlalchemy import create_engine, insert
from sqlalchemy.exc import OperationalError

from pyinaturalist_open_data.constants import (
    BUCKET_NAME,
    DATA_DIR,
    DEFAULT_DB_URI,
    METADATA_DL_PATH,
    METADATA_KEY,
)
from pyinaturalist_open_data.models import Base, Observation, Photo, Taxon, User

MODEL_CSV_FILES = {
    Observation: 'observations.csv',
    Photo: 'photos.csv',
    Taxon: 'taxa.csv',
    User: 'observers.csv',
}

logging.basicConfig(level='WARN')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def download_metadata(download_path: str = METADATA_DL_PATH):
    """Download and extract metadata archive

    Args:
        download_path: Optional file path to download to
    """
    download_path = expanduser(download_path)
    os.makedirs(dirname(download_path), exist_ok=True)

    # Download combined package with authentication disabled
    if exists(download_path):
        logger.info(f'File already exists: {download_path}')
    else:
        logger.info(f'Downloading to: {download_path}')
        resource = boto3.resource('s3')
        resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
        bucket = resource.Bucket(BUCKET_NAME)
        bucket.download_file(METADATA_KEY, download_path)

    # Extract CSVs
    logger.info('Extracting contents')
    tar = tarfile.open(download_path, 'r:gz')
    tar.extractall(path=dirname(download_path))
    tar.close()


def load_all(db_uri: str = DEFAULT_DB_URI):
    """Load contents of CSV files into a database. This is just here for convenience since it works
    with all supported DB dialects. DB-specific bulk inserts are faster, if available.
    """
    # Create tables, if they don't already exist
    engine = create_engine(db_uri, echo=True)
    Base.metadata.create_all(engine)

    for model in [Observation, Photo, Taxon, User]:
        try:
            load_table(engine, model)
        except OperationalError as e:
            logger.exception(e)


def load_table(engine, model):
    csv_path = join(DATA_DIR, MODEL_CSV_FILES[model])
    logger.info(f'Loading data from {csv_path}')

    with open(csv_path, 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        next(csv_reader)  # Skip header
        engine.execute(insert(model), [map_columns(model, row) for row in csv_reader])


def map_columns(model, row):
    """Get a column mapping from model properties to row indices. Model properties are already in
    the same order as the CSV columns, but since we're using the (faster) lower-level
    ``engine.execute``, we need an explicit mapping.
    """
    return {col.name: row[i] for i, col in enumerate(model.__mapper__.columns)}


if __name__ == '__main__':
    download_metadata()
    load_all()
