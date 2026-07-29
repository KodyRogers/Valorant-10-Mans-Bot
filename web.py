from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy import select

from starlette.middleware.sessions import SessionMiddleware

from config import SESSION_SECRET

from database import SessionLocal
from managers.match_manager import MatchManager
from managers.player_manager import PlayerManager
from managers.queue_manager import QueueManager
from models import Player
from routes.login import router

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key = SESSION_SECRET
)

app.include_router(router)
templates = Jinja2Templates(directory="templates") 
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root(request: Request):
    if "discord_id" not in request.session:
        return {"logged_in": False}

    return {
        "logged_in": True,
        "discord_id": request.session["discord_id"],
        "username": request.session["username"]
    }

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

@app.get("/match/{match_code}")
async def match_info(match_code: str, request: Request):
    async with SessionLocal() as session:

        match = await MatchManager.getMatch(session, match_code)

        if not match:
            return {"error": "Match not found."}

        match_players = await MatchManager.get_match_players(
            session,
            match.match_id
        )

        players_info = []
        discord_ids = []

        for player in match_players:
            riot_id = await PlayerManager.get_riot_account_info(
                player.discord_id
            )

            discord_ids.append(str(player.discord_id))

            players_info.append({
                "discord_id": player.discord_id,
                "riot_id": f"{riot_id['riot_name']}#{riot_id['riot_tag']}",
                "team": player.team,
                "is_captain": player.is_captain
            })

        login_id = str(request.session.get("discord_id", ""))

        return templates.TemplateResponse(
            request,
            "match.html",
            {
                "match": match,
                "players": players_info,
                "logged_in": login_id,
                "authorized": login_id in discord_ids
            }
        )

