import random
from sqlalchemy import select

from models import MatchPlayer

class DraftManager:

    # ========================
    # DRAFT ORDER
    # ========================

    DRAFT_ORDER = [1,2,2,1,1,2,2,1]
    CURRENT_PICK = 0

    async def get_captains(session, player_list):

        # Get two captains
        captain_1, captain_2 = random.sample(player_list, 2)

        remaining_players = []
        for player in player_list:
            if player not in (captain_1, captain_2):
                remaining_players.append(player)

        return captain_1, captain_2, remaining_players

    @staticmethod
    async def get_current_captain(session, match):
        from managers.match_manager import MatchManager

        players = await MatchManager.get_match_players(
            session,
            match.match_id
        )

        drafted = len([
            p
            for p in players
            if p.team != "None" and not p.is_captain
        ])

        if drafted >= len(DraftManager.DRAFT_ORDER):
            return None

        current_team = DraftManager.DRAFT_ORDER[drafted]

        for player in players:
            if player.team == current_team and player.is_captain:
                return player

        return None

    async def make_pick(session, match, player_id):

        if (match.status != "DRAFTING"):
            return False
    
        result = await session.execute(

            select(MatchPlayer).where(

                MatchPlayer.match_id == match.match_id,

                MatchPlayer.discord_id == player_id

            )

        )
        
        player = result.scalar_one_or_none()
        if player is None:
            return False

        current_captain = await DraftManager.get_current_captain(session, match)
        player.team = current_captain.team

        result = await session.execute(
            select(MatchPlayer).where(
                MatchPlayer.match_id == match.match_id,
                MatchPlayer.team == "None"
            )
        )
        remaining = result.scalars().first()

        if remaining is None:
            match.status = "MAP_BAN"
            print("Draft Concluded onto map bans")

        await session.commit()

        return True
    

