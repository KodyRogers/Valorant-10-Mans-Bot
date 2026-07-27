from fastapi import FastAPI, Request

from sqlalchemy import select

from starlette.middleware.sessions import SessionMiddleware

from config import SESSION_SECRET

from database import SessionLocal
from managers.match_manger import MatchManager
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
        
        match_players = await MatchManager.get_match_players(session, match.match_id)

        players_info = []

        for player in match_players:
            riot_info = await QueueManager.get_riot_account_info(session, player.discord_id)
            players_info.append({
                "discord_id": player.discord_id,
                "riot_id": f"{riot_info['riot_name']}#{riot_info['riot_tag']}" if riot_info else "Unknown",
                "team": player.team,
                "is_captain": player.is_captain
            })

        return {
            "match_code": match.match_code,
            "status": match.status,
            "captain_1": match.captain_1,
            "captain_2": match.captain_2,
            "selected_map": match.selected_map,
            "winning_team": match.winning_team,
            "created_at": match.created_at.isoformat(),
            "players": players_info
        }