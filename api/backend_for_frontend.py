# we don't need traefik
# we can use the port name
# api = 5000, answersApi = 5100, trackApi = 5200, currentStateApi = 5300

import asyncio
import json
import httpx
from uuid import UUID
from fastapi import FastAPI, Depends, Response, HTTPException, status, Request
from datetime import datetime
app = FastAPI()


@app.post("/game/new", status_code=status.HTTP_201_CREATED)
def new_game(username: str):
    with httpx.Client() as client:
        params = {"username": username}
        # try:
        r = client.get('http://127.0.0.1:5200/user-data', params=params)
        # except httpx.RequestError as exc:
        #     raise
        curr = {"status": "new"}
        curr.update(dict(r.json()))
        d = datetime.now()
        # time = f"{d.year}{d.month}{d.day}"
        time = "2022507"
        curr["game_id"] = int(time)
        params = {"user_id": curr.get("user_uuid"), "game_id": curr.get("game_id")}
        r = client.post('http://127.0.0.1:5300/start-new-game', params=params)
        # if r.status_code != httpx.codes.CREATED:
        #     return r.raise_for_status()
        data = dict(r.json())
        if int(data["counter"]) > 0:
            curr["status"] = "In-progress"
            curr.update(data)
            counter = int(curr.pop("counter"))
            curr["remaining"] = 6 - counter
            params = {"answer_guess": curr.get("list")[counter - 1]}
            r = client.get('http://127.0.0.1:5100/validate-answer', params=params)
            # if r.status_code != httpx.codes.OK:
            #     return r.raise_for_status()
            curr.update(dict(r.json()))
    return curr


# # m1 dict
# async def verify_guess(guess: str, data: dict):
#     async with httpx.AsyncClient() as client:
#         params = {"guess": guess}
#         r = await client.get('http://127.0.0.1:5000/validate-guess', params=params)
#         data["status"] = r.status_code
#
#
# # m4 current state
# async def check_remaining(game_id: int, user_id: UUID, data: dict):
#     async with httpx.AsyncClient() as client:
#         params = {"user_id": user_id, "game_id": game_id}
#         r = await client.get('http://127.0.0.1:5300/get-state-game', params=params)
#         data.update(dict(r.json()))


# m2 check answer
async def verify_answer(guess: str, data: dict):
    async with httpx.AsyncClient() as client:
        params = {"answer_guess": guess}
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
        params = {"user_id": user_id, "game_id": game_id}
        r = client.get('http://127.0.0.1:5300/get-state-game', params=params)
        curr = dict(r.json())
        data["remaining"] = 6 - int(curr.get("counter"))

        if not is_verify or not data.get("remaining"):
            data["Status"] = "invalid"
            return data
    await asyncio.gather(
        update_guess(game_id, user_id, guess, data),
        verify_answer(guess, data)
    )
    data["Status"] = "incorrect"
    curr = data.get("correct")
    if len(curr) == 5:
        data.update({"Status": "win"})
        await asyncio.gather(
            record_result(user_id, game_id, 1, data),
            get_result(user_id, data)
        )
        return data
    elif len(curr) < 5 and not data.get("remaining"):
        data.update({"Status": "lose"})
        await asyncio.gather(
            record_result(user_id, game_id, 0, data),
            get_result(user_id, data)
        )
        return data
    return data
