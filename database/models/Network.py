"""
Network.py: SQLAlchemy Network Model
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .base import Base

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"

metadata = Base.metadata


class Network(Base):
    __tablename__ = 'networks'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(SmallInteger)
    server_password = Column(String(255))
    nick = Column(String(50))
    user_password = Column(String(255))
    has_services = Column(Boolean)
    autojoin = Column(Boolean)