from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from pyinaturalist_open_data.models import Base, sa_field


@Base.mapped
@dataclass
class Observation:
    __tablename__ = 'observation'
    __sa_dataclass_metadata_key__ = 'sa'

    uuid: str = sa_field(String, init=False, primary_key=True, index=True)
    user_id: int = sa_field(ForeignKey('user.id'), default=None, index=True)
    latitude: float = sa_field(Float, default=None)
    longitude: float = sa_field(Float, default=None)
    positional_accuracy: int = sa_field(Integer, default=None)
    taxon_id: int = sa_field(ForeignKey('taxon.id'), default=None, index=True)
    quality_grade: str = sa_field(String, default=None, index=True)
    observed_on: datetime = sa_field(DateTime, default=None, index=True)

    user = relationship('User', back_populates='observations')
    taxon = relationship('Taxon', back_populates='observations')
