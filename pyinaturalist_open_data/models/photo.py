from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from pyinaturalist_open_data.models import Base, sa_field


@Base.mapped
@dataclass
class Photo:
    __tablename__ = 'photo'
    __sa_dataclass_metadata_key__ = 'sa'

    uuid: str = sa_field(Column(String, primary_key=True), init=False)
    photo_id: int = sa_field(Integer, default=None)
    observation_uuid: str = sa_field(String, default=None)
    observer_id: int = sa_field(Integer, default=None)
    extension: str = sa_field(String, default=None)
    license: str = sa_field(String, default=None)
    width: int = sa_field(Integer, default=None)
    height: int = sa_field(Integer, default=None)
    position: int = sa_field(Integer, default=None)
