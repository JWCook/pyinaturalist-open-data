from dataclasses import dataclass

from sqlalchemy import Boolean, Column, Integer, String

from pyinaturalist_open_data.models import Base, sa_field


@Base.mapped
@dataclass
class Taxon:
    __tablename__ = 'taxon'
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = sa_field(Column(Integer, primary_key=True), init=False)
    ancestry: str = sa_field(String, default=None)
    rank: str = sa_field(String, default=None)
    rank_level: str = sa_field(String, default=None)
    name: str = sa_field(String, default=None)
    active: bool = sa_field(Boolean, default=None)

    def ancestors(self):
        return self.ancestry.split('\\')
