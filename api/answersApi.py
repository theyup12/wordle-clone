import logging.config
import sqlite3
import contextlib
from fastapi import FastAPI, Depends, Response, HTTPException, status, Request
from pydantic import BaseModel, BaseSettings
from enum import Enum


class Settings(BaseSettings):
    database: str
    database2: str
    logging_config: str

    class Config:
        env_file = ".env"


# base model for answers


class Answer(BaseModel):
    word: str


# connect to the answers database


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database2)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()
logging.config.fileConfig(settings.logging_config)


# get the list of words from the answers.db(from wordle script)


@app.get("/answers/")
def list_answers(db: sqlite3.Connection = Depends(get_db)):
    answers = db.execute("SELECT * FROM answers")
    return {"answers": answers.fetchall()}


# colors to check if the letter in the right spot or not


# class Color(Enum):
#     Correct = "Green"
#     WrongSpot = "Yellow"
#     Wrong = 'Gray'
# counting numbers for game


# check if the answer valid and if all color green then move on and go the next game.


@app.get("/validate-answer")
def validate_guess(answer_guess: str, game_id: int, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("SELECT words FROM answers WHERE id = ? LIMIT 1", [game_id])
    answer = cur.fetchone()[0]
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="answer not found"
        )
    correct_answer = str(answer)
    correct = []
    present = []
    map = dict()
    for i in answer:
        if i in map:
            map[i] += 1
        else:
            map[i] = 1
    # compare the guess word with answer
    for i, ch in enumerate(answer_guess):
        if ch == correct_answer[i]:
            correct.append(ch)
        elif ch in map:
            if map[ch] > 0:
                map[ch] -= 1
                present.append(ch)
    return {"correct": correct, "present": present}


# update the answer


@app.put("/games/{game_id}")
def change_answers(game_id: int, new_answer: Answer, response: Response, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("SELECT * FROM answers WHERE id = ? LIMIT 1", [game_id])
    answers = cur.fetchall()
    if not answers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="word not found"
        )
    else:
        # update the answers with given word and id
        db.execute(
            """
            UPDATE answers
            SET words = ?
            WHERE id = ?;
            """,
            [new_answer.word, game_id]
        )
        db.commit()
    return {"Changed Answer": new_answer.word}


# check for specific game


@app.get("/answers/{id}")
def check_changes(id: int, response: Response, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("SELECT * FROM answers WHERE id = ? LIMIT 1", [id])
    answer = cur.fetchall()
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="answer not found"
        )
    return {"answer": answer}
