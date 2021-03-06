# pyinaturalist-open-data

[![Build status](https://github.com/JWCook/pyinaturalist-open-data/workflows/Build/badge.svg)](https://github.com/JWCook/pyinaturalist-open-data/actions)
[![PyPI](https://img.shields.io/pypi/v/pyinaturalist-open-data?color=blue)](https://pypi.org/project/pyinaturalist-open-data)
[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/pyinaturalist-open-data)](https://pypi.org/project/pyinaturalist-open-data)
[![PyPI - Format](https://img.shields.io/pypi/format/pyinaturalist-open-data?color=blue)](https://pypi.org/project/pyinaturalist-open-data)

**Notice:** This library has been merged into [pyinaturalist-convert](https://github.com/pyinat/pyinaturalist-convert).


**pyinaturalist-open-data** is a python library and CLI tool for working with
[inaturalist-open-data](https://github.com/inaturalist/inaturalist-open-data).
Its goal is to make it easy to import and use this dataset in a python application backed by
[any SQLAlchemy-compatible database engine](https://docs.sqlalchemy.org/en/14/core/engines.html#supported-databases)
(SQLite by default), or simply for local data exploration.

See the CLI in action here or on [asciinema](https://asciinema.org/a/412516):
[![asciicast](docs/pynat-demo.gif)](https://asciinema.org/a/412516)

## Installation
Install with pip:
```
pip install pyinaturalist-open-data
```

Or for local development:
```bash
git clone https://github.com/JWCook/pyinaturalist-open-data.git
cd pyinaturalist-open-data
pip install poetry && poetry install
```

## Usage

This package provides the command `pynat`. See `--help` for commands and options:
```
Usage: pynat [OPTIONS] COMMAND [ARGS]...

  Commands for working with inaturalist open data

Options:
  -v, --verbose  Show more detailed output
  --help         Show this message and exit.

Commands:
  db    Load contents of CSV files into a database
  dl    Download and extract inaturalist open data archive
  init  Just create tables (if they don't already exist) without populating...
  load  Download and load all data into a database.
```

### Run everything
The simplest command is `load`, which runs all steps:
1. Download and extract the dataset
2. Create database tables and indices
3. Load the data into the database

Options:
```
Usage: pynat load [OPTIONS]

Options:
  -d, --download-dir TEXT  Alternate path for downloads
  -u, --uri TEXT           Alternate database URI to connect to
  --help                   Show this message and exit.
```

By default, this will create a new SQLite database. Alternatively, you can provide a URI for
[any supported database](https://docs.sqlalchemy.org/en/14/core/engines.html#supported-databases).

### Run individual steps
Other commands are available if you only one to run one of those steps at a time.

`dl` command:
```
Usage: pynat dl [OPTIONS]

  Download and extract all files in the inaturalist open data archive

Options:
  -d, --download-dir TEXT  Alternate path for downloads
  --help                   Show this message and exit
```

**Note:** Both `dl` and `load` will reuse local data if already exists and is up to date.

`db` command:
```
Usage: pynat db [OPTIONS]

  Load contents of CSV files into a database. Also creates tables and
  indexes, if they don't already exist.

Options:
  -d, --download-dir TEXT         Alternate path for downloads
  -i, --init                      Just initialize the database with tables
                                  + indexes without loading data
  -t, --tables [observation|photo|taxon|user]
                                  Load only these specific tables
  -u, --uri TEXT                  Alternate database URI to connect to

  --help                          Show this message and exit.
```

**Note:** This can take a long time to run. Depending on the database type, you will likely get
better performance with database-specific bulk loading tools (for example, `psql` with [COPY](https://www.postgresql.org/docs/13/sql-copy.html) for PostgreSQL)

### Python package
To use as a python package instead of a CLI tool:
```python
from pyinaturalist_open_data import download_metadata, load_all

download_metadata()
load_all()
```
