"""
models.py
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    User table schema
    """

    __tablename__ = "users"

    userid = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    files = relationship("File", back_populates="user", cascade="all, delete")


class File(Base):
    """
    File table schema
    """
    __tablename__ = "files"

    fileid = Column(Integer, primary_key=True, index=True)
    userId = Column(
        Integer, ForeignKey("users.userid", ondelete="CASCADE"), nullable=False
    )
    filename = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="files")
