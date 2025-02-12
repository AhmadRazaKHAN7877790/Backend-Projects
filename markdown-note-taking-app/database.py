"""
database.py
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv(".env.local")

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Provides a SQLAlchemy database session.

    Yields:
        Session: An instance of SQLAlchemy's database session.

    Notes:
        The session is automatically closed when the request ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
