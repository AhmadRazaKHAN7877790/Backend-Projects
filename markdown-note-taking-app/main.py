"""
main.py
"""

import markdown
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Form
from sqlalchemy.orm import Session
import schema
import utility_functions
from database import get_db


app = FastAPI()


@app.post("/check_grammer/", response_model=schema.GrammerCheckResponse)
async def check_grammar_endpoint(
    file: UploadFile = File(...),
) -> schema.GrammerCheckResponse:
    """
    Checks grammar of the given note and returns a list of detected errors.
    """

    # Validate file type
    if not file.filename.endswith(".md"):
        raise HTTPException(
            status_code=400, detail="Only Markdown (.md) files are allowed."
        )

    # Read file content
    content = await file.read()
    formatted_errors = utility_functions.process_markdown_file(content)

    return schema.GrammerCheckResponse(
        filename=[file.filename], errors=formatted_errors
    )


@app.post("/save_note/")
async def save_note(
    username: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),  # Ensure db session is passed correctly
) -> schema.FileResponse:
    """
    Saves the given note to the database.
    """
    # Validate file type
    if not file.filename.endswith(".md"):
        raise HTTPException(
            status_code=400, detail="Only Markdown (.md) files are allowed."
        )

    # Read file content safely
    try:
        content = await file.read()
        markdown_text = content.decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to read the file.") from exc

    try:
        # Begin transaction manually
        db.begin()

        # Ensure user exists
        user_data = schema.UserBase(username=username, email=email)
        user = utility_functions.create_user(db, user_data)

        # Insert file into the database
        file_base = schema.FileBase(
            filename=file.filename, content=markdown_text, userid=user.userid
        )
        db_file = utility_functions.create_file(db, file_base)

        # Commit changes manually
        db.commit()

        return schema.FileResponse(
            fileid=db_file.fileid,
            filename=db_file.filename,
        )

    except Exception as e:
        db.rollback()  # Ensure rollback in case of failure
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/saved_notes/")
def get_saved_notes(email: str, db: Session = Depends(get_db)) -> list[str]:
    """Get all saved notes for a user."""
    files = utility_functions.get_file_names_by_user_email(db, email)
    return files


@app.get("/render_note{fileid}/")
def render_note(fileid: int, db: Session = Depends(get_db)) -> str:
    """Return HTML representation of the note."""
    file = utility_functions.get_file_by_id(db, fileid)
    if not file:
        raise HTTPException(status_code=404, detail="File not found.")
    html_content = markdown.markdown(file.content)
    return html_content
