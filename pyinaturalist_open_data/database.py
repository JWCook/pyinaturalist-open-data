"""Functions for loading inaturalist open data into a database"""
import csv
from logging import getLogger
from os.path import join
from time import time

from dateutil.parser import parse as parse_date
from rich import print
from sqlalchemy import create_engine, delete, insert
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import Boolean, DateTime

from .constants import DATA_DIR, DEFAULT_DB_URI
from .models import Base, Observation, Photo, Taxon, User
from .progress import get_progress

MODEL_CSV_FILES = {
    Observation: 'observations.csv',
    Photo: 'photos.csv',
    Taxon: 'taxa.csv',
    User: 'observers.csv',
}

logger = getLogger(__name__)


def create_tables(engine):
    """Create tables + indexes based on models, if they don't already exist"""
    Base.metadata.create_all(engine)


def load_all(db_uri: str = DEFAULT_DB_URI, download_dir: str = DATA_DIR, verbose: int = 0):
    """Load contents of CSV files into a database. This is just here for convenience since it works
    with all supported DB dialects. DB-specific bulk inserts are faster, if available.
    """
    print('[cyan]Creating tables')
    session = Session(bind=create_engine(db_uri, echo=verbose == 3))
    create_tables(session.get_bind())
    print(f'[cyan]Loading data from [magenta]{DATA_DIR}/*.csv[cyan]...')

    for model in [User, Taxon, Observation, Photo]:
        try:
            start = time()
            load_table(session, model, download_dir)
            if verbose:
                print(f'Finished in {time() - start:.2f} seconds')
        except OperationalError as e:
            print(e)


def load_table(session, model, download_dir):
    """Load CSV contents into a table, with progress bar"""
    csv_path = join(download_dir, MODEL_CSV_FILES[model])
    progress, task = get_progress(0, f'Loading [magenta]{model.__name__}[/magenta] records')

    # Clear table and insert everything; faster than checking if individual rows exist
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
