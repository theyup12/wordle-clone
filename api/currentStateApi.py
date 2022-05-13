import json
import logging.config
import sqlite3
import contextlib
import redis
from uuid import UUID
from fastapi import FastAPI, Depends, Response, HTTPException, status, Request
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    stats_database: str
    stats_database_s1: str
    stats_database_s2: str
    stats_database_s3: str
    user_database: str
    logging_config: str

    class Config:
        env_file = ".env"


def get_db():
    with contextlib.closing(sqlite3.connect(settings.user_database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()
db = redis.Redis(host="localhost", port=6379)


@app.post("/start-new-game", status_code=status.HTTP_201_CREATED)
def start_game(user_id: UUID, game_id: int, response: Response):
    # insert into the redis database first, key would be current user and game, init the list and counter
    # db.flushall()
    con = sqlite3.connect('./var/user.db')
    cursor = con.cursor()
    try:
        result = cursor.execute("SELECT user_id FROM users WHERE user_uuid = ?", [user_id.bytes_le]).fetchone()
    except:
        con.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid user")

    if int(result[0]) % 3 == 0:
        con = sqlite3.connect('./var/stats_s1.db')
    elif int(result[0]) % 3 == 1:
        con = sqlite3.connect('./var/stats_s2.db')
    else:
        con = sqlite3.connect('./var/stats_s3.db')
    cursor = con.cursor()
    try:
        game = cursor.execute("SELECT * FROM games WHERE user_uuid = ? and game_id = ?",
                              [user_id.bytes_le, game_id]).fetchall()
        if len(game) != 0:
            con.close()
            raise HTTPException
    except:
        con.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="already played")

    delim: str = ":"
    cur_id = f"{user_id}{delim}{game_id}"
    guess_list = f"{cur_id}{delim}guessList"
    count = f"{cur_id}{delim}counter"
    if not db.exists(guess_list) or not db.exists(count):
        db.lpush(guess_list, "", "", "", "", "", "")
        db.set(count, 0)

    cur = db.lrange(guess_list, 0, -1)
    cur_count = db.get(count)
    return {"current_id": cur_id, "list": cur, "counter": cur_count}


@app.put("/update-game/{current_game}")
def update_game(user_id: UUID, game_id: int, guess_word: str):
    delim: str = ":"
    cur_id = f"{user_id}{delim}{game_id}"
    guess_list = f"{cur_id}{delim}guessList"
    count = f"{cur_id}{delim}counter"
    if not db.exists(guess_list) or not db.exists(count):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND"
        )
    num = int(db.get(count).decode())
    if num < 6:
        db.lset(guess_list, num, guess_word)
        db.incr(count)
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="reach the limit"
        )
    cur = db.lrange(guess_list, 0, -1)
    cur_count = db.get(count)
    return {"current_id": cur_id, "list": cur, "counter": cur_count}


@app.get("/get-state-game/")
def get_state_game(user_id: UUID, game_id: int):
    delim: str = ":"
    cur_id = f"{user_id}{delim}{game_id}"
    guess_list = f"{cur_id}{delim}guessList"
    count = f"{cur_id}{delim}counter"
    if not db.exists(guess_list) or not db.exists(count):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND"
        )
    cur = db.lrange(guess_list, 0, -1)
    cur_count = db.get(count)
    return {"current_id": cur_id, "guess-list": cur, "guess-numbers": cur_count}
