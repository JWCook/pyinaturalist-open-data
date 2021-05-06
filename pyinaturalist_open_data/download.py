"""Functions for downloading and extracting inaturalist open data"""
# TODO: Check local and remote timestamps to only download if a new version is available
import os
from io import FileIO
from os.path import basename, exists, expanduser, getsize, join
from tarfile import TarFile
from time import time

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from rich import print

from .constants import ARCHIVE_NAME, BUCKET_NAME, DATA_DIR, METADATA_KEY
from .progress import get_download_progress


class FlatTarFile(TarFile):
    """Extracts all archive contents to a flat base directory, ignoring archive subdirectories"""

    def extract(self, member, path="", **kwargs):
        if member.isfile():
            member.name = basename(member.name)
            super().extract(member, path, **kwargs)


class ProgressIO(FileIO):
    """File object wrapper that updates read progress"""

    def __init__(self, path, *args, **kwargs):
        self._total_size = getsize(path)
        self.progress, self.task = get_download_progress(self._total_size, 'Extracting')
        super().__init__(path, *args, **kwargs)

    def read(self, size):
        self.progress.update(self.task, advance=size)
        return super().read(size)


def download_metadata(download_dir: str = DATA_DIR, verbose: int = 0):
    """Download and extract metadata archive

    Args:
        download_path: Optional file path to download to
    """
    download_dir = expanduser(download_dir)
    os.makedirs(download_dir, exist_ok=True)
    download_file = join(download_dir, ARCHIVE_NAME)

    # Download combined package with authentication disabled
    if exists(download_file):
        print(f'File already exists: {download_file}')
    else:
        print(f'Downloading to: {download_file}')
        s3_download(BUCKET_NAME, METADATA_KEY, download_file)

    # Extract files
    progress_file = ProgressIO(download_file)
    with FlatTarFile.open(fileobj=progress_file) as archive, progress_file.progress:
        archive.extractall(path=download_dir)


def s3_download(bucket_name: str, key: str, download_file: str):
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
            Filename=download_file,
            Callback=lambda n_bytes: progress.update(task, advance=n_bytes),
        )


if __name__ == '__main__':
    start = time()
    download_metadata()
    print(f'Finished in {time() - start:.2f} seconds')
