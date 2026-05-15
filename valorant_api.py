import requests

class HenrikAPI:
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.henrikdev.xyz/valorant"
        self.headers = {
            "Authorization": api_key
        }

    # ----------------------------
    # GET ACCOUNT INFO
    # ----------------------------
    def get_account(self, name, tag):
        url = f"{self.base_url}/v1/account/{name}/{tag}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            
            return response.json()["data"]

        return None

    # ----------------------------
    # GET PLAYER PEAK MMR
    # ----------------------------
    def get_mmr_peak(self, region, name, tag):
        url = f"{self.base_url}/v3/mmr/{region}/{name}/{tag}"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()["data"]["peak"]

        return None
    
    # ----------------------------
    # GET PLAYER CURRENT MMR
    # ----------------------------
    def get_mmr_current(self, region, name, tag):
        url = f"{self.base_url}/v3/mmr/{region}/{name}/{tag}"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()["data"]

        return None

    # ----------------------------
    # GET RECENT MATCHES
    # ----------------------------
    def get_matches(self, region, name, tag, size=5):
        url = f"{self.base_url}/v3/matches/{region}/{name}/{tag}?size={size}"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()["data"]

        return []

    # ----------------------------
    # FIND MATCH BY ID
    # ----------------------------
    def find_custom_match(self, region, name, tag, queued_players):
        matches = self.get_matches(region, name, tag)

        for match in matches:
            players_in_match = []

            for player in match["players"]["all_players"]:
                players_in_match.append(player["puuid"])

            # Check if all queued players are in same game
            if all(puuid in players_in_match for puuid in queued_players):
                return match

        return None