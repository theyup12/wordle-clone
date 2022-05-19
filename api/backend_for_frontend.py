# we don't need traefik
# we can use the port name
# api = 5000, answersApi = 5100, trackApi = 5200, currentStateApi = 5300

import asyncio
import httpx
from uuid import UUID
from fastapi import FastAPI, status
from datetime import datetime
import random
import redis
app = FastAPI()
db = redis.Redis(host="localhost", port=6379)


@app.post("/game/new", status_code=status.HTTP_201_CREATED)
def new_game(username: str):
    with httpx.Client() as client:

        params = {"username": username}
        r = client.get('http://127.0.0.1:5200/user-data', params=params)
        curr = {"status": "new"}
        curr.update(dict(r.json()))
        exist = True
        while exist:
            game_id = random.randint(1, 2309)
            curr["game_id"] = int(game_id)
            params = {"user_id": curr.get("user_uuid"), "game_id": curr.get("game_id")}
            r = client.post('http://127.0.0.1:5300/start-new-game', params=params)
            if r.status_code == httpx.codes.CREATED:
                data = dict(r.json())
                exist = False
        if int(data["counter"]) > 0:
            curr["status"] = "In-progress"
            curr.update(data)
            counter = int(curr.pop("counter"))
            curr["remaining"] = 6 - counter
            params = {"answer_guess": curr.get("list")[counter - 1], "game_id": curr.get("game_id")}
            r = client.get('http://127.0.0.1:5100/validate-answer', params=params)
            # if r.status_code != httpx.codes.OK:
            #     return r.raise_for_status()
            curr.update(dict(r.json()))
        # if int(curr.get("remaining")) == 0:
        #     return {"Status": "game finished"}
    return curr


# m2 check answer
async def verify_answer(guess: str, game_id: int, data: dict):
    async with httpx.AsyncClient() as client:
        params = {"answer_guess": guess, "game_id": game_id}
        r = await client.get('http://127.0.0.1:5100/validate-answer', params=params)
        data.update(dict(r.json()))


# m4 update game record
async def update_guess(current_game: int, user_id: UUID, guess: str, data: dict):
    async with httpx.AsyncClient() as client:
        params = {"user_id": user_id, "guess_word": guess}
        r = await client.put(f'http://127.0.0.1:5300/update-game/{current_game}', params=params)
        curr = dict(r.json())
        data["remaining"] = 6 - int(curr.get("counter"))


async def get_result(user_id: UUID, data: dict):
    async with httpx.AsyncClient() as client:
        d = datetime.now()
        time = d.strftime("%Y-%m-%d")
        params = {"user_uuid": user_id, "current_date": str(time)}
        r = await client.get('http://127.0.0.1:5200/wordle-statistics', params=params)
        data.update(dict(r.json()))


async def record_result(user_id: UUID, current_game: int, result: int, curr: dict):
    async with httpx.AsyncClient() as client:
        d = datetime.now()
        time = d.strftime("%Y%m%d")
        guesses = 6 - curr.get("remaining")
        curr_data = {"game_id": current_game, "finished": time, "guesses": guesses, "won": result}
        params = {"user_uuid": user_id, "game": curr_data}
        r = await client.post('http://127.0.0.1:5200/game-result', params=params, json=curr_data)
        curr.update(dict(r.json()))


@app.post("/game/{game_id}")
async def running_game(game_id: int, user_id: UUID, guess: str):
    data: dict = {}
    is_verify = False
    with httpx.Client() as client:
        params = {"guess": guess}
        r = client.get('http://127.0.0.1:5000/validate-guess', params=params)
        if r.status_code == httpx.codes.OK:
            is_verify = True
        if is_verify:
            params = {"user_id": user_id, "game_id": game_id}
            r = client.get('http://127.0.0.1:5300/get-state-game', params=params)
            curr = dict(r.json())
            data["remaining"] = 6 - int(curr.get("counter"))

        if not is_verify or not data.get("remaining"):
            data["Status"] = "invalid"
            return data
    await asyncio.gather(
        update_guess(game_id, user_id, guess, data),
        verify_answer(guess, game_id, data)
    )
    curr = data.get("correct")
    if len(curr) == 5:
        data.update({"Status": "win"})
        await asyncio.gather(
            record_result(user_id, game_id, 1, data),
            get_result(user_id, data)
        )
        return data
    if len(curr) < 5 and not data.get("remaining"):
        data.update({"Status": "lose"})
        await asyncio.gather(
            record_result(user_id, game_id, 0, data),
            get_result(user_id, data)
        )
        return data
    if len(curr) < 5 and data.get("remaining"):
        data["Status"] = "incorrect"
        return data
