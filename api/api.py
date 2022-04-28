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


class Guess(BaseModel):
    word: str
# connect database with word_list.sql


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db
# use for debug the code


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI(
    servers=[
        {"url": "/api/v2", "description": "Production environment"},
        {"url": "/api/v3", "description": "Production environment"}
    ],
    root_path="/api/v1"
    # root_path_in_servers=False

)
logging.config.fileConfig(settings.logging_config)
# getting all the word from the word_list database and display

@app.get("/app")
def read_main(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}


@app.get("/list-words/")
def list_words(db: sqlite3.Connection = Depends(get_db)):
    words = db.execute("SELECT * FROM words")
    return{"List words": words.fetchall()}
# check if the guess word is five-letters word


@app.get("/validate-guess/{guess}")
def validate_guess(guess: str):
    if (len(guess) != 5):
        return {"validGuess": False}
    return {"validGuess": True}
# adding possible guess into the word_list.db, and check if the word exists and valid five-letter


@app.post("/add-guess/")
def add_guess(guess: Guess,  response: Response, db: sqlite3.Connection = Depends(get_db)):
    res = dict(guess)
    valid_guess = dict(validate_guess(guess.word))
    valid = valid_guess["validGuess"]
    cur = db.execute("SELECT EXISTS(SELECT * FROM words WHERE word = ? LIMIT 1)", [guess.word])
    exist = int(cur.fetchone()[0])
    # check if the guess valid and exist
    if valid and not exist:
        try:
            # add word into the list_word database
            add_word = db.execute("""INSERT INTO words(word) VALUES(?)""", [res["word"]])
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"type": type(error).__name__, "msg": str(error)}
            )
        res["id"] = add_word.lastrowid
        # return the id and the word
        return res
    return {"status": "word already exists or invalid guess"}
# delete the guess word from the word_list.db, and check if the word exists


@app.delete("/delete-guess/")
def delete_guess(guess: Guess,  response: Response, db: sqlite3.Connection = Depends(get_db)):
    # insert into dict first
    res = dict(guess)
    # check if the word exists
    cur = db.execute("SELECT EXISTS(SELECT * FROM words WHERE word = ? LIMIT 1)", [guess.word])
    exist = int(cur.fetchone()[0])
    if exist:
        try:
            # delete the word from the database
            delete_word = db.execute("""DELETE FROM words WHERE word = ? LIMIT 1""", [guess.word])
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"type": type(error).__name__, "msg": str(error)}
            )
        res["id"] = delete_word.lastrowid
        return res
    return {"status": "word not found"}
