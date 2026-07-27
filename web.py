from fastapi import FastAPI, Request

from sqlalchemy import select

from starlette.middleware.sessions import SessionMiddleware

from config import SESSION_SECRET

from database import SessionLocal
from managers.queue_manager import QueueManager
from models import Player
from routes.login import router

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key = SESSION_SECRET
)

app.include_router(router)

@app.get("/")
async def root(request: Request):
    if "discord_id" not in request.session:
        return {"logged_in": False}

    return {
        "logged_in": True,
        "discord_id": request.session["discord_id"],
        "username": request.session["username"]
    }

@app.get("/queue")
async def queue(request: Request):
    async with SessionLocal() as session:

        result = await session.execute(
            select(Player)
        )

        players = result.scalars().all()

        queue_data = []
        is_logged_in = False
        for player in players:

            queue_data.append({
                "discord_id": player.discord_id,
                "riot_id": f"{player.riot_name}#{player.riot_tag}",
                "elo": player.elo
            })

            web_disc_id = request.session["discord_id"]
            if player.discord_id == web_disc_id:
                is_logged_in = True

        # Sort highest elo first
        queue_data.sort(
            key=lambda x: x["elo"],
            reverse=True
        )

         

        return queue_data, is_logged_in

@app.get("/leaderboard")
async def leaderboard():

    async with SessionLocal() as session:

        result = await session.execute(
            select(Player)
        )

        players = result.scalars().all()

        leaderboard_data = []

        for player in players:

            leaderboard_data.append({
                "discord_id": player.discord_id,
                "riot_id": f"{player.riot_name}#{player.riot_tag}",
                "wins": player.wins,
                "losses": player.losses,
                "elo": player.elo
            })

        # Sort highest elo first
        leaderboard_data.sort(
            key=lambda x: x["elo"],
            reverse=True
        )

        return leaderboard_data