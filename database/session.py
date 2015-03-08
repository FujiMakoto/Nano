"""
session.py: Database session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, MemoryBase


# noinspection PyPep8Naming
def DbSession():
    """
    Create and return a new database session
    """
    # Bind the engine to the metadata of the Base class
    engine = create_engine("sqlite:///database/nano.db")
    Base.metadata.bind = engine

    session = sessionmaker(bind=engine)
    session = session()
    return session


# noinspection PyPep8Naming
def MemorySession():
    """
    Create and return a new in-memory SQLite database session
    """
    engine = create_engine("sqlite:///:memory:")
    MemoryBase.metadata.bind = engine
    MemoryBase.metadata.create_all(engine)

    session = sessionmaker(bind=engine)
    session = session()
    return session