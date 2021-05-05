from dataclasses import field

from sqlalchemy import Column
from sqlalchemy.orm import registry

Base = registry()


def sa_field(col_type, **kwargs):
    """Get a dataclass field with SQLAlchemy column metadata"""
    col = col_type if isinstance(col_type, Column) else Column(col_type)
    return field(**kwargs, metadata={"sa": col})
