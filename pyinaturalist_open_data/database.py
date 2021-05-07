"""Functions for loading inaturalist open data into a database"""
import csv
from logging import getLogger
from pathlib import Path
from time import time
from typing import List

from dateutil.parser import parse as parse_date
from rich import print
from sqlalchemy import create_engine, delete, insert
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import Boolean, DateTime

from .constants import DATA_DIR, DEFAULT_DB_URI, PathOrStr
from .models import Base, Observation, Photo, Taxon, User
from .progress import get_progress

MODEL_CSV_FILES = {
    Observation: 'observations.csv',
    Photo: 'photos.csv',
    Taxon: 'taxa.csv',
    User: 'observers.csv',
}
MODEL_NAMES = {
    'observation': Observation,
    'photo': Photo,
    'taxon': Taxon,
    'user': User,
}

logger = getLogger(__name__)


def create_tables(engine=None, uri: str = DEFAULT_DB_URI):
    """Create tables + indexes based on models, if they don't already exist

    Args:
        engine: A SQLAlchemy engine to connect with
        uri: Alternate database URI to connect to
    """
    print('[cyan]Creating tables')
    engine = engine or create_engine(uri)
    Base.metadata.create_all(engine)
    print('[cyan]Done')


def load_all(
    download_dir: PathOrStr = DATA_DIR,
    tables: List[str] = None,
    uri: str = DEFAULT_DB_URI,
    verbose: int = 0,
):
    """Load contents of CSV files into a database. This is just here for convenience since it works
    with all supported DB dialects. DB-specific bulk inserts are faster, if available.

    Args:
        download_dir: Alternate path for downloads
        tables: Specific table(s) to load instead of all
        uri: Alternate database URI to connect to
        verbose: Show additional output
    """
    session = Session(bind=create_engine(uri, echo=verbose == 3))
    create_tables(session.get_bind())
    print(f'[cyan]Loading data from [magenta]{DATA_DIR}/*.csv[cyan]...')

    if tables:
        models = [MODEL_NAMES[table] for table in tables]
    else:
        models = [User, Taxon, Observation, Photo]

    for model in models:
        try:
            start = time()
            load_table(session, model, Path(download_dir))
            if verbose:
                print(f'Finished in {time() - start:.2f} seconds')
        except OperationalError as e:
            print(e)

    print(f'[cyan]Finished populating database at[/cyan] {uri}')


def load_table(session, model, download_dir: Path):
    """Load CSV contents into a table, with progress bar"""
    csv_path = download_dir / MODEL_CSV_FILES[model]
    progress, task = get_progress(0, f'Loading [magenta]{model.__name__}[/magenta] records')

    # Clear the table and insert everything; faster than checking if individual rows exist
    session.execute(delete(model))
    with progress, open(csv_path) as csv_file:
        num_lines = sum(1 for _ in open(csv_path)) - 1
        progress.update(task, total=num_lines)
        reader = csv.reader(csv_file, delimiter='\t')
        next(reader)  # Skip headers

        for chunk in read_chunks(reader, progress, task):
            session.execute(insert(model), [map_columns(model, row) for row in chunk])
        session.commit()


def read_chunks(reader, progress, task, chunksize=20000):
    """Read a CSV file in chunks"""
    chunk = []
    for i, line in enumerate(reader):
        if i % chunksize == 0 and i > 0:
            yield chunk
            chunk = []
            progress.update(task, advance=chunksize)
        chunk.append(line)
    progress.update(task, advance=i % chunksize + 1)
    yield chunk


def map_columns(model, row):
    """Get a column mapping from model properties to CSV columns. These are already in the same
    order, but since we're using a lower-level bulk insert, this must be explicit.
    """

    return {col.name: convert_types(col, row[i]) for i, col in enumerate(model.__mapper__.columns)}


def convert_types(col, value):
    """Do any type conversions that the database can't do automatically"""
    if isinstance(col.type, DateTime):
        value = parse_date(value) if value else None
    elif isinstance(col.type, Boolean):
        value = str(value).lower() == 'true'
    # Replace empty strings and whitespace with None
    elif not (value and str(value).strip()):
        value = None
    return value


if __name__ == '__main__':
    start = time()
    load_all()
    print(f'Finished in {time() - start:.2f} seconds')
