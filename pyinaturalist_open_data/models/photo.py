from dataclasses import dataclass

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, synonym

from . import Base, sa_field


@Base.mapped
@dataclass
class Photo:
    __tablename__ = 'photo'
    __sa_dataclass_metadata_key__ = 'sa'

    uuid: str = sa_field(String, init=False, primary_key=True, index=True)
    photo_id: int = sa_field(Integer, default=None)
    observation_uuid: str = sa_field(
        ForeignKey('observation.uuid'), default=None, primary_key=True, index=True
    )
    user_id: int = sa_field(ForeignKey('user.id'), default=None, index=True)
    extension: str = sa_field(String, default=None)
    license: str = sa_field(String, default=None)
    width: int = sa_field(Integer, default=None)
    height: int = sa_field(Integer, default=None)
    position: int = sa_field(Integer, default=None)

    observation = relationship('Observation', back_populates='photos')
    user = relationship('User', back_populates='photos')

    # Aliases for columns as provided in the CSV file
    photo_uuid = synonym('observation_uuid')
    observer_id = synonym('user_id')
