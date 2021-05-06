from logging import basicConfig, getLogger

import click

from .constants import DEFAULT_DB_URI, METADATA_DL_PATH
from .database import load_all
from .download import download_metadata


VERBOSITY_LOG_LEVELS = {
    0: 'ERROR',
    1: 'WARN',
    2: 'INFO',
    3: 'DEBUG'
}

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
@click.option(
    '-d', '--download-path', default=METADATA_DL_PATH, help='Alternate download path for archive'
)
@click.pass_context
def dl(ctx, download_path):
    """Download stuff"""
    download_metadata(download_path)


@inat.command()
@click.option('-u', '--uri', default=DEFAULT_DB_URI, help='Database URI')
@click.pass_context
def load(ctx, uri):
    """Load contents of CSV files into a database"""
    load_all(uri, verbose=ctx.obj['verbose'])


if __name__ == '__main__':
    inat()
