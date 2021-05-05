from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from pyinaturalist_open_data.models import Base, sa_field


@Base.mapped
@dataclass
class User:
    __tablename__ = 'user'
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = sa_field(Column(Integer, primary_key=True), init=False)
    login: str = sa_field(String, default=None)
    name: str = sa_field(String, default=None)
