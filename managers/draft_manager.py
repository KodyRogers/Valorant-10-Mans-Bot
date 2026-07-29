import random

class DraftManger:

    # ========================
    # DRAFT ORDER
    # ========================

    DRAFT_ORDER = [1,2,2,1,1,2,2,1]

    async def get_captains(session, player_list):

        # Get two captains
        captain_1, captain_2 = random.sample(player_list, 2)

        remaining_players = []
        for player in player_list:
            if player not in (captain_1, captain_2):
                remaining_players.append(player)

        return captain_1, captain_2, remaining_players


    
    

