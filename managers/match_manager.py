from datetime import UTC, datetime
import random
from re import match
import string

from sqlalchemy import select, delete

from config import WEBSITE_URL
from database import SessionLocal
from models import Match, MatchPlayer, Player
from managers.draft_manager import DraftManager

class MatchManager:
    

    @staticmethod
    def generate_match_id(length=8):

        """
        Generates a random match ID consisting of uppercase letters and digits.
        """
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def generate_website_url(match_code: str):
        return f"{WEBSITE_URL}/match/{match_code}"

    @staticmethod
    async def create_match(players_queue):

        from managers.draft_timer import DraftTimer
            
        async with SessionLocal() as session:

            # Create a new match
            match_code = MatchManager.generate_match_id()
            match_website_url = MatchManager.generate_website_url(match_code)

            while await MatchManager.match_code_exists(session, match_code):
                match_code = MatchManager.generate_match_id()

            captain_1, captain_2, remaining_players = await DraftManager.get_captains(session, players_queue)

            # Create a new match instance
            match = Match(
                match_code=match_code,
                status = "DRAFTING",
                captain_1=captain_1.discord_id,
                captain_2=captain_2.discord_id,
                selected_map="None",
                winning_team="None",
                created_at=datetime.now(UTC)
            )

            session.add(match)

            #give the match.id before commit
            await session.flush()

            session.add(MatchPlayer(match_id=match.match_id, discord_id=captain_1.discord_id, team=1, is_captain=True))
            session.add(MatchPlayer(match_id=match.match_id, discord_id=captain_2.discord_id, team=2, is_captain=True))

            # Add players to the match
            for player in remaining_players:
                session.add(MatchPlayer(match_id=match.match_id, discord_id=player.discord_id, team="None", is_captain=False))
            await session.commit()
            await session.refresh(match)

            if (
                match.status == "DRAFTING"
                and match.match_id not in DraftTimer.timers
            ):
                print("Starting draft timer...")
                await DraftTimer.start(match.match_id)

            return match, match_website_url

        #return match
    
    @staticmethod
    async def match_code_exists(session, match_code):
        result = await session.execute(select(Match).filter_by(match_code=match_code))
        return result.scalars().first() is not None


    @staticmethod
    async def getMatch(session, match_code: str):
        result = await session.execute(select(Match).filter_by(match_code=match_code))
        return result.scalars().first()

    @staticmethod
    async def get_match_players(session, match_id: int):
        result = await session.execute(select(MatchPlayer).filter_by(match_id=match_id))
        return result.scalars().all()

    @staticmethod
    async def get_match_by_id(session, match_id: int):
        results = await session.execute(select(Match).filter_by(match_id=match_id))
        return results.scalars().first()
    