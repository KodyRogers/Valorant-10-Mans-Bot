import random
from sqlalchemy import select

from managers.draft_timer import DraftTimer
from managers.map_ban_timer import MapTimer
from managers.player_manager import PlayerManager
from models import MatchPlayer

class DraftManager:

    # ========================
    # DRAFT ORDER
    # ========================

    DRAFT_ORDER = [1,2,2,1,1,2,2,1]

    async def get_captains(session, player_list):
        
        # Get two captains
        captain_1, captain_2 = random.sample(player_list, 2)
        captain_2 = player_list[9]


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

    async def make_pick(session, match, discord_id, player_id):
        current_captain = await DraftManager.get_current_captain(session, match)
        print(f"Current Captain: {current_captain.discord_id}, Discord ID: {discord_id}")
        if (str(discord_id) != str(current_captain.discord_id)):
            return False

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
            match.status = "VOTE"
            await session.commit()
            await MapTimer.start(match.match_id)
            print("Draft Concluded onto map bans")
            return True

        await session.commit()
        

        return True
    
    @staticmethod
    async def get_draft_state(session, match):
        from managers.match_manager import MatchManager
        available_players = await MatchManager.get_available_players(session, match.match_id)
        team_1_players = await MatchManager.get_team_players(session, match.match_id, 1)
        team_2_players = await MatchManager.get_team_players(session, match.match_id, 2)
        current_captain = await DraftManager.get_current_captain(session, match)
        
        current_captain_return = None
        if current_captain is not None:
            current_captain_info = await PlayerManager.get_riot_account_info(current_captain.discord_id) 
            current_captain_riot_name = current_captain_info["riot_name"]
            current_captain_riot_tag = current_captain_info["riot_tag"]
            current_captain_elo = await PlayerManager.get_player_mmr(current_captain.discord_id)
            current_captain_return = {
                "discord_id": current_captain.discord_id,
                "riot_name": current_captain_riot_name,
                "riot_tag": current_captain_riot_tag,
                "elo": current_captain_elo
            }
        
        return {
            "success": True,
            "status": match.status,
            "current_captain": current_captain_return,
            "remaining_timer": DraftTimer.get_remaining(match.match_id),
            "available_players": [
                {
                    "discord_id": player.discord_id,
                    "riot_name": player.riot_name,
                    "riot_tag": player.riot_tag,
                    "elo": player.elo
                }
                for player in available_players
            ],
            "team_1_players": [
                {
                    "discord_id": player.discord_id,
                    "riot_name": player.riot_name,
                    "riot_tag": player.riot_tag,
                    #"is_captain": player.is_captain,
                    "elo": player.elo
                }
                for player in team_1_players
            ],
            "team_2_players": [
                {
                    "discord_id": player.discord_id,
                    "riot_name": player.riot_name,
                    "riot_tag": player.riot_tag,
                    #"is_captain": player.is_captain,
                    "elo": player.elo
                }
                for player in team_2_players
            ]
        }
