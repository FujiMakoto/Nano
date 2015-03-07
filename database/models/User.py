"""
User.py: SQLAlchemy User Model
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


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    nick = Column(String(50), nullable=False)
    password = Column(String(60), nullable=False)
    is_admin = Column(Boolean)