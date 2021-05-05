from dataclasses import field

from sqlalchemy import Column
from sqlalchemy.orm import registry

Base = registry()

# Table names should be singular
TABLE_RENAMES = {
    'observers': 'user',
    'observations': 'observation',
    'taxa': 'taxon',
    'photos': 'photo',
}


def sa_field(col_type, index: bool = False, primary_key: bool = False, **kwargs):
    """Get a dataclass field with SQLAlchemy column metadata"""
    column = Column(col_type, index=index, primary_key=primary_key)
    return field(**kwargs, metadata={"sa": column})
