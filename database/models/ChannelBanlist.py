"""
ChannelBanlist.py: SQLAlchemy Channel Banlist Model
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


class ChannelBanlist(Base):
    __tablename__ = 'channel_banlists'

    id = Column(Integer, primary_key=True)
    channel_id = Column(ForeignKey('channels.id'), nullable=False)
    nick = Column(String(50))
    hostmask = Column(String(500), nullable=False)
    reason = Column(String(255))
    banned_by_user_id = Column(ForeignKey('users.id'))
    ban_length = Column(Integer)
    expires = Column(DateTime)

    banned_by_user = relationship('User')
    channel = relationship('Channel')