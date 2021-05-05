from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from pyinaturalist_open_data.models import Base, sa_field


@Base.mapped
@dataclass
class Observation:
    __tablename__ = 'observation'
    __sa_dataclass_metadata_key__ = 'sa'

    uuid: str = sa_field(Column(String, primary_key=True), init=False)
    user_id: int = sa_field(Integer, default=None)
    latitude: float = sa_field(Float, default=None)
    longitude: float = sa_field(Float, default=None)
    positional_accuracy: int = sa_field(Integer, default=None)
    taxon_id: int = sa_field(Integer, default=None)
    quality_grade: str = sa_field(String, default=None)
    observed_on: datetime = sa_field(DateTime, default=None)
