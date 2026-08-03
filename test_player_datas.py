from managers.valorant_api import henrik
from sqlalchemy import update
from models import MatchPlayer, Match
from database import SessionLocal

import sys
import asyncio
import json

sys.stdout.reconfigure(encoding="utf-8")

async def rico_test():
    
    test = await henrik.get_matches("orzo", "bigum", 2)

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(test, f, indent=4, ensure_ascii=False)

    map = test[0]["metadata"]["map"]["name"]
    print(map)
    players = test[0]["players"]
    for player in players:
        print (player["name"])

async def update_match_players():
    match_id = 2  # Change this to the match you want to reset
    
    async with SessionLocal() as session:

        await session.execute(
            update(MatchPlayer)
            .where(
                MatchPlayer.match_id == match_id,
                MatchPlayer.is_captain == False
            )
            .values(team="None")      # Change to team=0 if you use 0 instead of None
        )

        await session.execute(
            update(Match).where(
                Match.match_id == match_id
            ).values(status="DRAFTING")
        )
            
        await session.commit()

    print(f"Reset draft for match {match_id}.")

async def main():
    await update_match_players()
    

if __name__ == "__main__":
    asyncio.run(main())