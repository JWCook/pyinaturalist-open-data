from logging import basicConfig, getLogger

import click

from .constants import DATA_DIR, DEFAULT_DB_URI, METADATA_DL_PATH
from .database import load_all
from .download import download_metadata


VERBOSITY_LOG_LEVELS = {
    0: 'ERROR',
    1: 'WARN',
    2: 'INFO',
    3: 'DEBUG'
}

download_dir_option = click.option(
    '-d', '--download-dir', default=DATA_DIR, help='Alternate path for downloads'
)

@click.group()
@click.option('-v', '--verbose', count=True, help='Show more detailed output')
@click.pass_context
def inat(ctx, verbose):
    ctx.ensure_object(dict)
    verbose = min(verbose, 3)
    ctx.obj['verbose'] = verbose

    # Configure logging based on verbosity level
    basicConfig(level=VERBOSITY_LOG_LEVELS[verbose])
    if verbose == 1:
        getLogger('pyinaturalist_open_data').setLevel('INFO')


@inat.command()
@download_dir_option
@click.pass_context
def dl(ctx, download_dir):
    """Download and extract inaturalist open data archive"""
    download_metadata(download_dir, verbose=ctx.obj['verbose'])


@inat.command()
@download_dir_option
@click.option('-u', '--uri', default=DEFAULT_DB_URI, help='Alternate database URI to connect to')
@click.pass_context
def load(ctx, download_dir, uri):
    """Load contents of CSV files into a database"""
    load_all(uri, download_dir=download_dir, verbose=ctx.obj['verbose'])


if __name__ == '__main__':
    inat()
