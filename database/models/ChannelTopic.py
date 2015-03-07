"""
ChannelTopic.py: SQLAlchemy Channel Topic Model
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


class ChannelTopic(Base):
    __tablename__ = 'channel_topics'

    id = Column(Integer, primary_key=True)
    channel_id = Column(ForeignKey('channels.id'), nullable=False)
    message = Column(String(1000), nullable=False)
    enabled = Column(Boolean)
    priority = Column(SmallInteger)
    expires = Column(DateTime)

    channel = relationship('Channel')