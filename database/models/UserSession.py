"""
UserSession.py: SQLAlchemy User Session Model (In-Memory)
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import relationship
from .base import MemoryBase

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"

metadata = MemoryBase.metadata


class UserSession(MemoryBase):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    network_id = Column(Integer, nullable=False)
    hostmask = Column(String(500), nullable=False)
    expires = Column(DateTime)