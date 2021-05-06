from logging import basicConfig

import click

from pyinaturalist_open_data.constants import DEFAULT_DB_URI, METADATA_DL_PATH

from .database import load_all
from .download import download_metadata


@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Show additional information')
def inat(verbose):
    if verbose:
        basicConfig(level='INFO')


@inat.command()
@click.option(
    '-d', '--download-path', default=METADATA_DL_PATH, help='Alternate download path for archive'
)
def dl(download_path):
    """Download stuff"""
    download_metadata(download_path)


@inat.command()
@click.option('-u', '--uri', default=DEFAULT_DB_URI, help='Database URI')
def load(uri):
    """Load contents of CSV files into a database"""
    load_all(uri)


if __name__ == '__main__':
    inat()
