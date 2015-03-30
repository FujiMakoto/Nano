"""
ChannelStaff.py: SQLAlchemy Channel Staff Model
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .base import Base

metadata = Base.metadata


class IgnoreList(Base):
    __tablename__ = 'ignore_list'

    id = Column(Integer, primary_key=True)
    source = Column(String(255))
    mask = Column(String(50))
