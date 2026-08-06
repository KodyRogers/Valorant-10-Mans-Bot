

class LiveManager():

    @staticmethod
    async def get_live_state(session, match):

        from managers.map_ban_manager import ALL_MAPS
        from managers.match_manager import MatchManager

        team_1 = await MatchManager.get_team_players(session, match.match_id, 1)
        team_2 = await MatchManager.get_team_players(session, match.match_id, 2)
        
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
            "team1": team_1,
            "team2": team_2,
            "selected_map": selected_map,
            "team_1_side": match.team_1_starting_side
        }