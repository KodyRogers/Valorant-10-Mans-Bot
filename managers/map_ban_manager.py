from models import MatchPlayer, MatchVote
from sqlalchemy import select
from collections import Counter
import random


class MapBanManager:

    @staticmethod
    async def ban_map(session, match, player_id, map_name):
        # Check if the player is the current captain
        current_captain = await MapBanManager.get_current_captain(session, match)
        if current_captain.player_id != player_id:
            raise Exception("Player is not the current captain.")

        # Add the map to the banned maps list
        banned_maps = await MapBanManager.get_banned_maps(session, match)
        if map_name in banned_maps:
            raise Exception("Map has already been banned.")

        available_maps = await MapBanManager.get_available_maps(session, match)
        if map_name not in available_maps:
            raise Exception("Map is not available for banning.")
        
        banned_maps.append(map_name)
        match.banned_maps = banned_maps
        await session.commit()

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
        await MapTimer.start(
            session,
            match
        )

    @staticmethod
    async def get_map_ban_state(session, match):

        from managers.map_ban_timer import MapTimer

        banned_maps = await MapBanManager.get_banned_maps(session, match)
        available_maps = await MapBanManager.get_available_maps(session, match)
        current_captain = await MapBanManager.get_current_captain(session, match)

        time_remaining = MapTimer.get_remaining(match.match_id)

        return {
            "success": True,
            "status": match.status,
            "banned_maps": banned_maps,
            "available_maps": available_maps,
            "current_captain": current_captain.discord_id if current_captain else None,
            "time_remaining": time_remaining
        }