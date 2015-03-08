"""
Channel.py: SQLAlchemy Channel Model
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


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    network_id = Column(ForeignKey('networks.id'), nullable=False)
    channel_password = Column(String(255))
    name = Column(String(50))
    xop_level = Column(SmallInteger)
    manage_topic = Column(Boolean)
    topic_separator = Column(String(10))
    topic_mode = Column(String(20))
    topic_max = Column(SmallInteger)
    log = Column(Boolean)
    autojoin = Column(Boolean)

    network = relationship('Network')