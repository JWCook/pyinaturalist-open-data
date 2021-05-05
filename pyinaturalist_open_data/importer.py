import tarfile
from logging import basicConfig, getLogger
from os import makedirs
from os.path import dirname, exists, expanduser

import boto3
from botocore.handlers import disable_signing

from pyinaturalist_open_data.constants import BUCKET_NAME, METADATA_DL_PATH, METADATA_KEY

logger = getLogger(__name__)
basicConfig(level='WARN')
logger.setLevel('INFO')


# TODO: Check local and remote timestamps to only download if a new version is available
def download_metadata(download_path: str = None):
    """Download and extract metadata archive

    Args:
        download_path: Optional file path to download to
    """
    download_path = expanduser(download_path or METADATA_DL_PATH)
    makedirs(dirname(download_path), exist_ok=True)

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


if __name__ == '__main__':
    download_metadata()
