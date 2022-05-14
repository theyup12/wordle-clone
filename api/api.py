import logging.config
import sqlite3
import contextlib
from fastapi import FastAPI, Depends, Response, HTTPException, status, Request
from pydantic import BaseModel, BaseSettings

# connect database setting from .env file


class Settings(BaseSettings):
    database: str
    database2: str
    logging_config: str

    class Config:
        env_file = ".env"

# Base model for getting guess word

# connect database with word_list.sql


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db
# use for debug the code


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()
logging.config.fileConfig(settings.logging_config)
# getting all the word from the word_list database and display


@app.get("/list-words/")
def list_words(db: sqlite3.Connection = Depends(get_db)):
    words = db.execute("SELECT * FROM words")
    return{"List words": words.fetchall()}
# check if the guess word is five-letters word


@app.get("/validate-guess/{guess}")
def validate_guess(guess: str, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("SELECT word FROM words WHERE word = ?", [guess])
    curr = cur.fetchall()
    if not curr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="word not found"
        )
    return {"word": curr[0][0]}
# adding possible guess into the word_list.db, and check if the word exists and valid five-letter


@app.post("/add-guess/")
def add_guess(guess: str,  response: Response, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("SELECT word FROM words WHERE word = ?", [guess])
    exist = cur.fetchall()
    # check if the guess valid and exist
    if not exist and len(guess) == 5:
        try:
            # add word into the list_word database
            db.execute("""INSERT INTO words(word) VALUES(?)""", [guess])
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"type": type(error).__name__, "msg": str(error)}
            )
        return {"added_guess": guess}
    return {"status": "word already exists or invalid guess"}
# delete the guess word from the word_list.db, and check if the word exists


@app.delete("/delete-guess/")
def delete_guess(guess: str,  response: Response, db: sqlite3.Connection = Depends(get_db)):
    # check if the word exists
    cur = db.execute("SELECT word FROM words WHERE word = ?", [guess])
    exist = cur.fetchall()
    if exist:
        try:
            # delete the word from the database
            delete_word = db.execute("""DELETE FROM words WHERE word = ?""", [guess])
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"type": type(error).__name__, "msg": str(error)}
            )
        return {"Deleted_guess": guess}
    return {"status": "word not found"}
