"""
ChannelStaff.py: SQLAlchemy Channel Staff Model
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


class ChannelStaff(Base):
    __tablename__ = 'channel_staff'

    id = Column(Integer, primary_key=True)
    channel_id = Column(ForeignKey('channels.id'), nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    access_level = Column(SmallInteger)

    channel = relationship('Channel')
    user = relationship('User')