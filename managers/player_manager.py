from database import SessionLocal
from models import Player
from sqlalchemy import select
from managers.valorant_api import henrik

class PlayerManager:

    # ===============================
    # Register Player
    # ===============================
    @staticmethod
    async def register_player(discord_id,riot_name,riot_tag):

        # Check if player already exists
        if await PlayerManager.player_exists(discord_id):
            return False, "Player is already registered."

        # Riot account exists?
        if await PlayerManager.riot_account_exists(riot_name, riot_tag) == False:
            return False, "Riot account is not found. Please check your Riot ID and try again."

        # PUUID already registered?
        henrik_player = await henrik.get_account(riot_name, riot_tag)
        puuid = henrik_player["puuid"]

        # Save player
        async with SessionLocal() as session:
            player = Player(
                discord_id=discord_id,
                riot_name=riot_name,
                riot_tag=riot_tag,
                puuid=puuid
            )
            session.add(player)
            await session.commit()

        return True, "Registration successful!"

    # ===============================
    # Change Riot ID
    # ===============================
    @staticmethod
    async def change_riot_id(discord_id, new_riot_name, new_riot_tag):
        # Check if player exists
        if not await PlayerManager.player_exists(discord_id):
            return False, "Player is not registered."

        # Riot account exists?
        if await PlayerManager.riot_account_exists(new_riot_name, new_riot_tag) == False:
            return False, "Riot account is not found. Please check your Riot ID and try again."

        # PUUID already registered?
        henrik_player = await henrik.get_account(new_riot_name, new_riot_tag)
        puuid = henrik_player["puuid"]

        # Update player
        async with SessionLocal() as session:
            result = await session.execute(
                select(Player).where(Player.discord_id == discord_id)
            )
            player = result.scalar_one_or_none()

            player.riot_name = new_riot_name
            player.riot_tag = new_riot_tag
            player.puuid = puuid

            await session.commit()

        return True, "Riot ID updated successfully!"

    # ==============================
    # Check if player exists
    # ==============================
    @staticmethod
    async def player_exists(discord_id):
        async with SessionLocal() as session:
            result = await session.execute(
                select(Player).where(Player.discord_id == discord_id)
            )
            player = result.scalar_one_or_none()
            return player is not None

    # ==============================
    # Check if Riot account exists
    # ==============================
    @staticmethod
    async def riot_account_exists(riot_name, riot_tag):
        account = await henrik.get_account(riot_name, riot_tag)
        if account is None:
            return False
        return True

    # ==============================
    # Get riot account info by Discord ID
    # ==============================
    @staticmethod
    async def get_riot_account_info(discord_id):
        player = await PlayerManager.get_player(discord_id)
        if not player:
            return None
        return {
            "riot_name": player.riot_name,
            "riot_tag": player.riot_tag,
            "puuid": player.puuid
        }

    # ==============================
    # Get players mmr by Discord ID
    # ==============================
    @staticmethod
    async def get_player_mmr(discord_id):
        player = await PlayerManager.get_player(discord_id)
        if not player:
            return None
        return player.elo

    # ==============================
    # Get player by Discord ID
    # ==============================
    @staticmethod
    async def get_player(discord_id):
        async with SessionLocal() as session:
            result = await session.execute(
                select(Player).where(Player.discord_id == discord_id)
            )
            player = result.scalar_one_or_none()
            return player