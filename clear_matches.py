import asyncio

from database import engine
from models import Match, MatchPlayer, Queue


async def reset_match_tables():
    async with engine.begin() as conn:
        print("Dropping match tables...")

        # Drop child tables first
        await conn.run_sync(MatchPlayer.__table__.drop, checkfirst=True)
        await conn.run_sync(Queue.__table__.drop, checkfirst=True)
        await conn.run_sync(Match.__table__.drop, checkfirst=True)

        print("Recreating match tables...")

        await conn.run_sync(Match.__table__.create, checkfirst=True)
        await conn.run_sync(MatchPlayer.__table__.create, checkfirst=True)
        await conn.run_sync(Queue.__table__.create, checkfirst=True)

    print("Done.")


if __name__ == "__main__":
    asyncio.run(reset_match_tables())