from dataclasses import dataclass
from typing import List

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base, sa_field


@Base.mapped
@dataclass
class Taxon:
    __tablename__ = 'taxon'
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = sa_field(Integer, init=False, primary_key=True, index=True)
    ancestry: str = sa_field(String, default=None)
    rank_level: str = sa_field(String, default=None)
    rank: str = sa_field(String, default=None)
    name: str = sa_field(String, default=None, index=True)
    active: bool = sa_field(Boolean, default=None)

    @hybrid_property
    def ancestors(self) -> List[str]:
        return self.ancestry.split('\\')
