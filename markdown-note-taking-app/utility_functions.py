"""
utility_functions.py
"""

from typing import List, Optional
import markdown
import html2text
from sqlalchemy import text
from sqlalchemy.orm import Session
from schema import UserCreate, User, FileCreate, FileResponse, ErrorDetails
from check_grammer import check_grammar


def process_markdown_file(content: bytes) -> List[ErrorDetails]:
    """Converts Markdown to text and checks grammar."""

    markdown_text = content.decode("utf-8")

    # Convert Markdown to plain text
    html_text = markdown.markdown(markdown_text)
    plain_text = html2text.html2text(html_text)

    # Run grammar check
    errors = check_grammar(plain_text)

    # Ensur response format is valid
    return [
        {
            "error": error.get("error", ""),
            "suggestions": ", ".join(error.get("suggestions", [])),
        }
        for error in errors
    ]


def create_user(db: Session, user: UserCreate) -> User:
    """Create a user only if they do not exist (atomic operation)."""

    query = text(
        """
        INSERT INTO users (username, email)
        VALUES (:username, :email)
        ON CONFLICT (email) DO NOTHING
        RETURNING userid, username, email, created_at;
        """
    )

    result = db.execute(query, {"username": user.username, "email": user.email})
    db.commit()

    # If the insert didn't happen (user already exists), fetch existing user
    user_data = result.fetchone()
    if not user_data:
        query = text(
            "SELECT userid, username, email, created_at FROM users WHERE email = :email;"
        )
        result = db.execute(query, {"email": user.email})
        user_data = result.fetchone()
    return User(
        userid=user_data[0],
        username=user_data[1],
        email=user_data[2],
        created_at=user_data[3],
    )


def get_user_by_id(db: Session, userid: int):
    """Query to get User by ID"""
    query = text("SELECT * FROM users WHERE userid = :userid;")
    result = db.execute(query, {"userid": userid})
    return result.fetchone()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Query to get User by email"""
    query = text("SELECT * FROM users WHERE email = :email;")
    result = db.execute(query, {"email": email}).fetchone()
    return (
        User(
            userid=result[0], username=result[1], email=result[2], created_at=result[3]
        )
        if result
        else None
    )


def create_file(db: Session, file: FileCreate) -> Optional[FileResponse]:
    """Query to create a file"""
    query = text(
        """
        INSERT INTO files (userid, filename, content) 
        VALUES (:userid, :filename, :content) 
        RETURNING fileid, userid, filename, content, created_at;
    """
    )
    result = db.execute(
        query,
        {"userid": file.userid, "filename": file.filename, "content": file.content},
    )
    db.commit()
    file_data = result.fetchone()
    return (
        FileResponse(fileid=file_data[0], filename=file_data[1]) if file_data else None
    )


def get_user_files(db: Session, userid: int) -> List[FileResponse]:
    """Query to get all files for a user"""
    query = text("SELECT * FROM files WHERE userid = :userid;")
    result = db.execute(query, {"userid": userid}).fetchall()
    return [FileResponse(fileid=row[0], filename=row[1]) for row in result]


def get_file_names_by_user_email(db: Session, email: str) -> List[str]:
    """Get list of all files for a user by email"""
    query = text(
        """
        SELECT filename
        FROM files
        WHERE userid = (SELECT userid FROM users WHERE email = :email)
        """
    )

    result = db.execute(query, {"email": email})
    return [row[0] for row in result.fetchall()]


def get_file_by_id(db: Session, fileid: int) -> Optional[FileResponse]:
    """Get file by ID"""
    query = text("SELECT * FROM files WHERE fileid = :fileid;")
    result = db.execute(query, {"fileid": fileid}).fetchone()
    return FileResponse(fileid=result[0], filename=result[1]) if result else None
