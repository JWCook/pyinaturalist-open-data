from logging import basicConfig, getLogger

import click
from click_help_colors import HelpColorsGroup

from .constants import DATA_DIR, DEFAULT_DB_URI
from .database import MODEL_NAMES, create_tables, load_all
from .download import download_metadata

TABLES = ['observation', 'photo', 'taxon', 'user']
VERBOSITY_LOG_LEVELS = {0: 'ERROR', 1: 'WARN', 2: 'INFO', 3: 'DEBUG'}

download_dir_option = click.option(
    '-d', '--download-dir', default=DATA_DIR, help='Alternate path for downloads'
)
init_option = click.option(
    '-i',
    '--init',
    is_flag=True,
    help="Just initialize the database with tables + indexes without loading data",
)
tables_option = click.option(
    '-t',
    '--tables',
    type=click.Choice(MODEL_NAMES.keys(), case_sensitive=False),
    multiple=True,
    help='Load only these specific tables',
)
uri_option = click.option(
    '-u', '--uri', default=DEFAULT_DB_URI, help='Alternate database URI to connect to'
)


@click.group(cls=HelpColorsGroup, help_headers_color='blue', help_options_color='cyan')
@click.option('-v', '--verbose', count=True, help='Show more detailed output')
@click.pass_context
def pynat(ctx, verbose):
    """Commands for working with inaturalist open data"""
    ctx.ensure_object(dict)
    verbose = min(verbose, 3)
    ctx.obj['verbose'] = verbose

    # Configure logging based on verbosity level
    basicConfig(level=VERBOSITY_LOG_LEVELS[verbose])
    if verbose == 1:
        getLogger('pyinaturalist_open_data').setLevel('INFO')


@pynat.command()
@download_dir_option
@uri_option
@click.pass_context
def load(ctx, download_dir, uri):
    """Download and load all data into a database. By default, this will create/update a SQLite
    database. Reuses local data if already exists and is up to date.
    """
    download_metadata(download_dir, verbose=ctx.obj['verbose'])
    load_all(download_dir=download_dir, uri=uri, verbose=ctx.obj['verbose'])


@pynat.command(short_help='Download latest archive, if an update is available')
@download_dir_option
@click.pass_context
def dl(ctx, download_dir):
    """Download and extract all files in the inaturalist open data archive.
    Reuses local data if it exists and is up to date.
    """
    download_metadata(download_dir, verbose=ctx.obj['verbose'])


@pynat.command()
@download_dir_option
@init_option
@tables_option
@uri_option
@click.pass_context
def db(ctx, download_dir, init, tables, uri):
    """Load contents of CSV files into a database. Also creates tables and indexes, if they don't
    already exist.
    """
    if init:
        create_tables(uri=uri)
    else:
        load_all(download_dir=download_dir, tables=tables, uri=uri, verbose=ctx.obj['verbose'])


if __name__ == '__main__':
    pynat()
