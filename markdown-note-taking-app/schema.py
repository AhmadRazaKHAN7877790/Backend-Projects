"""
schema.py
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel


class ErrorDetails(BaseModel):
    """Details of the detected error"""

    error: str
    suggestions: str


class GrammerCheckResponse(BaseModel):
    """Response model for the check_grammar_endpoint"""

    filename: List[str]
    errors: List[ErrorDetails]


class UserBase(BaseModel):
    """Base model for User"""

    username: str
    email: str


class UserCreate(UserBase):
    """Create model for User"""

    pass


class UserResponse(UserBase):
    """Response model for User"""

    userid: int
    created_at: datetime

    class Config:
        """Config class for UserResponse"""

        from_attributes = True


class FileBase(BaseModel):
    """Base model for File"""

    filename: str
    content: str
    userid: int


class FileCreate(FileBase):
    """Create model for File"""

    pass


class FileResponse(BaseModel):
    """Response model for File"""

    fileid: int
    filename: str


class User(UserBase):
    """User model"""

    userid: int
    created_at: datetime
