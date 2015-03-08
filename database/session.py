"""
session.py: Database session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base, MemoryBase

# Load our primary database engine
db_engine = create_engine("sqlite:///database/nano.db")
db_session_factory = sessionmaker(bind=db_engine)
db_session = scoped_session(db_session_factory)

# Load our in-memory database engine for session storage
mem_engine = create_engine("sqlite:///:memory:")
mem_session_factory = sessionmaker(bind=mem_engine)
mem_session = scoped_session(mem_session_factory)


# noinspection PyPep8Naming
def DbSession():
    """
    Create and return a new database session
    """
    Base.metadata.bind = db_engine
    return db_session


# noinspection PyPep8Naming
def MemorySession():
    """
    Create and return a new in-memory SQLite database session
    """
    MemoryBase.metadata.bind = mem_engine
    MemoryBase.metadata.create_all(mem_engine)
    return mem_session