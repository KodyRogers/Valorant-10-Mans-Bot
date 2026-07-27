import aiohttp
from config import HENRIK_API_KEY

class HenrikAPI:

    def __init__(self, api_key):
        self.api_key = api_key

        self.base_url = "https://api.henrikdev.xyz/valorant"

        self.headers = {
            "Authorization": api_key
        }

    # ===================================
    # GET ACCOUNT INFO
    # ===================================

    async def get_account(
        self,
        name,
        tag
    ):

        url = f"{self.base_url}/v1/account/{name}/{tag}"

        async with aiohttp.ClientSession() as session:

            async with session.get(
                url,
                headers=self.headers
            ) as response:

                if response.status == 200:

                    data = await response.json()

                    return data["data"]

        return None

    # ===================================
    # GET PLAYER PEAK MMR
    # ===================================

    async def get_mmr_peak(
        self,
        region,
        name,
        tag
    ):

        url = f"{self.base_url}/v3/mmr/{region}/{name}/{tag}"

        async with aiohttp.ClientSession() as session:

            async with session.get(
                url,
                headers=self.headers
            ) as response:

                if response.status == 200:

                    data = await response.json()

                    return data["data"]["peak"]

        return None

    # ===================================
    # GET CURRENT MMR
    # ===================================

    async def get_mmr_current(
        self,
        region,
        name,
        tag
    ):

        url = f"{self.base_url}/v3/mmr/{region}/{name}/{tag}"

        async with aiohttp.ClientSession() as session:

            async with session.get(
                url,
                headers=self.headers
            ) as response:

                if response.status == 200:

                    data = await response.json()

                    return data["data"]

        return None

    # ===================================
    # GET RECENT MATCHES
    # ===================================

    async def get_matches(
        self,
        name,
        tag,
        size=5
    ):

        url = (
            f"{self.base_url}/v4/matches/"
            f"na/pc/{name}/{tag}?size={size}"
        )

        async with aiohttp.ClientSession() as session:

            async with session.get(
                url,
                headers=self.headers
            ) as response:

                if response.status == 200:

                    data = await response.json()

                    return data["data"]

        return []

    # ===================================
    # FIND CUSTOM MATCH
    # ===================================

    async def find_custom_match(
        self,
        region,
        name,
        tag,
        queued_players
    ):

        matches = await self.get_matches(
            region,
            name,
            tag
        )

        for match in matches:

            players_in_match = []

            for player in match["players"]["all_players"]:

                players_in_match.append(
                    player["puuid"]
                )

            if all(
                puuid in players_in_match
                for puuid in queued_players
            ):
                return match

        return None

henrik = HenrikAPI(HENRIK_API_KEY)