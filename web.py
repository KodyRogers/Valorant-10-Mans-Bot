from fastapi import FastAPI

from sqlalchemy import select

from database import SessionLocal
from models import Player

from old.bot import bot

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Valorant 10-Mans Bot is running!"}

@app.get("/queue")
async def queue():
    from old.bot import queue_manager
    
    return {
        "queue_size": len(queue_manager.queue),
        "players": queue_manager.queue
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