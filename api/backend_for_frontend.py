# we don't need traefik
# we can use the port name
# api = 5000, answersApi = 5100, trackApi = 5200, currentStateApi = 5300

import json
import httpx
import uuid
from fastapi import FastAPI, Depends, Response, HTTPException, status, Request
from datetime import datetime
app = FastAPI()


@app.post("/game/new", status_code=status.HTTP_201_CREATED)
def new_game(username: str):
    with httpx.Client() as client:
        params = {"username": username}
        r = client.get('http://127.0.0.1:5200/user-data', params=params)
        curr = {"status": "new"}
        curr.update(dict(r.json()))
        d = datetime.now()
        time = f"{d.year}{d.month}{d.day}"
        curr["game_id"] = int(time)
        params = {"user_id": curr.get("user_uuid"), "game_id": curr.get("game_id")}
        r = client.post('http://127.0.0.1:5300/start-new-game', params=params)
    return r.json()


# @app.post("/game/{game_id}")
# def create_game(user_id: uuid, guess: str):
#     return {"status": "empty"}
