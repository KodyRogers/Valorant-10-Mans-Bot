from models import MatchPlayer, MatchVote
from sqlalchemy import select
from collections import Counter
import random
import requests

import json

with open("data/maps.json", "r", encoding="utf-8") as f:
    ALL_MAPS = json.load(f)

class MapBanManager:

    #Error here
    @staticmethod
    async def ban_map(session, match, discord_id, map_name):
        # Check if the player is the current captain

        current_captain = await MapBanManager.get_current_captain(session, match)
        if current_captain.discord_id != discord_id:
            print("Player not current captain")
            return False

        # Add the map to the banned maps list
        banned_maps = await MapBanManager.get_banned_maps(session, match)
        if map_name in banned_maps:
            print("Map has already been banned.")
            return False

        available_maps = await MapBanManager.get_available_maps(session, match)
        if map_name not in available_maps:
            print("Map is not available for banning.")
            return False

        print(map_name)
        match.banned_maps.append(map_name)
        await session.commit()

        remaining_maps = await MapBanManager.get_available_maps(session, match)
        if len(remaining_maps) == 1:
            match.selected_map = remaining_maps[0]
            match.status = "SIDE"
            await session.commit()

        return True

    @staticmethod
    async def auto_ban(session, match):
        get_available_maps = await MapBanManager.get_available_maps(session, match)
        captain = await MapBanManager.get_current_captain(session, match)
        map = random.choice(get_available_maps)
        success = await MapBanManager.ban_map(session, match, captain.discord_id, map)
        return success
        

    @staticmethod
    async def get_current_captain(session, match):

        results = await session.execute(
            select(MatchPlayer).where(
                MatchPlayer.match_id == match.match_id,
                MatchPlayer.is_captain == True
            ).order_by(MatchPlayer.team)
        )
        current_captains = results.scalars().all()

        banned_maps = match.banned_maps or []

        if (len(banned_maps) % 2 == 0):
            return current_captains[0]
        else:
            return current_captains[1]

    @staticmethod
    async def get_banned_maps(session, match):
        return match.banned_maps or []

    @staticmethod
    async def get_available_maps(session, match):
        map_list = []
        banned_maps = await MapBanManager.get_banned_maps(session, match)
        for map_name in match.map_pool:
            if map_name not in banned_maps:
                map_list.append(map_name)
        return map_list

    @staticmethod
    async def vote(session, match, discord_id, pool):
        print(f"{discord_id} voting {pool}")
        results = await session.execute(
            select(MatchVote).where(
                MatchVote.match_id == match.match_id,
                MatchVote.discord_id == discord_id
            )
        )
        vote = results.scalar_one_or_none()

        if vote is None:
            vote = MatchVote(
                match_id=match.match_id,
                discord_id=discord_id,
                vote=pool
            )
            session.add(vote)
        else:
            vote.vote = pool

        await session.commit()

    @staticmethod
    async def get_votes(session, match):
        result = await session.execute(
            select(MatchVote).where(
                MatchVote.match_id == match.match_id
            )
        )
        return result.scalars().all()

    @staticmethod
    async def finish_vote(session, match):
        from managers.map_ban_timer import MapTimer
        votes = await MapBanManager.get_votes(session, match)
        all_pool_options = ["ALL MAPS", "COMPETITIVE POOL", "WEEKLY POOL", "RANDOM"]
        winning_map = None

        if len(votes) == 0:
            winning_map = random.choice(all_pool_options)
        else:
            counts = Counter(vote.vote for vote in votes)
            highest_count = max(counts.values())

            winners = [
                pool
                for pool, count in counts.items()
                if count == highest_count
            ]
            winning_map = random.choice(winners)

        winning_pool = []

        if winning_map == "RANDOM":
            all_maps = ["Abyss", "Ascent", "Bind", "Breeze", "Corrode", "Fracture",
                            "Haven", "Icebox" ,"Lotus", "Pearl", "Split", "Sunset", "Summit",]
            match.selected_map = random.choice(all_maps)
            match.status = "SIDE"

        else:
            if winning_map == "ALL MAPS":
                winning_pool = ["Abyss", "Ascent", "Bind", "Breeze", "Corrode", "Fracture",
                                "Haven", "Icebox" ,"Lotus", "Pearl", "Split", "Sunset", "Summit",]

            elif winning_map == "COMPETITIVE POOL":
                winning_pool = ["Ascent", "Breeze", "Haven", "Lotus", "Split", "Sunset", "Summit",]

            elif winning_map == "WEEKLY POOL":
                winning_pool = ["Abyss", "Ascent", "Bind", "Corrode", "Icebox" ,"Lotus", "Summit",]

            match.map_pool = winning_pool
            match.status = "MAP_BAN"
        
        await session.commit()
        return True

    @staticmethod
    async def choose_side(session, match, discord_id, side):

        results = await session.execute(
            select(MatchPlayer).where(
                MatchPlayer.match_id == match.match_id,
                MatchPlayer.is_captain == True
            ).order_by(MatchPlayer.team)
        )
        current_captains = results.scalars().all()

        if not current_captains:
            print("Index Error")
            return False

        if (str(discord_id) != str(current_captains[0].discord_id)):
            print("Not the Correct Captain")
            return False

        if side not in ("ATTACK", "DEFENSE"):
            print("Incorrect side")
            return False

        match.team_1_starting_side = side
        await session.commit()
        return True

    @staticmethod
    async def random_side(session, match):
        
        side = random.choice(["ATTACK", "DEFENSE"])
        print("GOT HERE")
        results = await session.execute(
            select(MatchPlayer).where(
                MatchPlayer.match_id == match.match_id,
                MatchPlayer.is_captain == True
            ).order_by(MatchPlayer.team)
        )
        current_captains = results.scalars().all()
        success = await MapBanManager.choose_side(session, match, str(current_captains[0].discord_id), side)
        return success

    @staticmethod
    async def get_map_ban_state(session, match):

        from managers.map_ban_timer import MapTimer
        from managers.match_manager import MatchManager

        banned_maps = await MapBanManager.get_banned_maps(session, match)
        current_captain = await MapBanManager.get_current_captain(session, match)
        team_1 = await MatchManager.get_team_players(session, match.match_id, 1)
        team_2 = await MatchManager.get_team_players(session, match.match_id, 2)
        time_remaining = MapTimer.get_remaining(match.match_id)

        available_maps = [
            map_data
            for map_data in ALL_MAPS
            if map_data["displayName"] in match.map_pool
        ]

        available_maps.sort(
            key=lambda m: match.map_pool.index(m["displayName"])
        )
        selected_map = None
        if match.selected_map != "None":
            selected_map = next(
                (
                    m
                    for m in ALL_MAPS
                    if m["displayName"] == match.selected_map
                ),
                None
            )
        
        return {
            "success": True,
            "status": match.status,
            "banned_maps": banned_maps,
            "available_maps": available_maps,
            "current_captain": (
                current_captain.discord_id
                if current_captain
                else None
            ),
            "time_remaining": time_remaining,
            "team_1": team_1,
            "team_2": team_2,
            "selected_map": selected_map,
            "team_1_side": match.team_1_starting_side
        }