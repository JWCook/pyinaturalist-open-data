"""Functions for loading inaturalist open data into a database"""
import csv
from os.path import join
from time import time

from rich import print
from sqlalchemy import create_engine, insert
from sqlalchemy.exc import OperationalError

from .constants import DATA_DIR, DEFAULT_DB_URI
from .models import Base, Observation, Photo, Taxon, User
from .progress import get_progress

MODEL_CSV_FILES = {
    Observation: 'observations.csv',
    Photo: 'photos.csv',
    Taxon: 'taxa.csv',
    User: 'observers.csv',
}


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
    load_all()
    print(f'Finished in {time() - start:.2f} seconds')
