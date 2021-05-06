from dataclasses import dataclass

from sqlalchemy import Integer, String

from .base import Base, sa_field


@Base.mapped
@dataclass
class User:
    __tablename__ = 'user'
    __sa_dataclass_metadata_key__ = 'sa'

    id: int = sa_field(Integer, init=False, primary_key=True, index=True)
    login: str = sa_field(String, default=None, index=True)
    name: str = sa_field(String, default=None)
