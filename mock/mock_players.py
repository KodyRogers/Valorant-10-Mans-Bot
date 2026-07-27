from sqlalchemy import select

from database import SessionLocal
from managers.queue_manager import QueueManager
from models import Player


class MockPlayers:

    async def mock_players(self, count=10):
        """
        Generates mock players for testing purposes.
        """
        print(f"Generating {count} mock players...")

        mock_players = [
            ("1", "TenZ", "NA1", 1450),
            ("2", "yay", "OPTIC", 1520),
            ("3", "Aspas", "BR1", 1480),
            ("4", "Demon1", "EG", 1550),
            ("5", "leaf", "C9", 1410),
            ("6", "zekken", "SEN", 1475),
            ("7", "s0m", "NRG", 1430),
            ("8", "Derke", "FNC", 1505),
            ("9", "Chronicle", "EMEA", 1510),
            ("10", "Less", "LOUD", 1495),
            ("11", "Boaster", "FNC", 1390),
            ("12", "Ethan", "NRG", 1440),
            ("13", "Crashies", "100T", 1425),
            ("14", "Victor", "SEN", 1460),
            ("15", "Marved", "NA", 1535),
            ("16", "bang", "100T", 1400),
            ("17", "Jawgemo", "EG", 1470),
            ("18", "nAts", "TL", 1515),
            ("19", "Sayf", "VIT", 1485),
            ("20", "Mako", "DRX", 1540),
        ]

        selected_mock_players = mock_players[:count]

        async with SessionLocal() as session:

            for discord_id, riot_name, riot_tag, mmr in selected_mock_players:

                result = await session.execute(
                    select(Player).where(Player.discord_id == discord_id)
                )
                existing_player = result.scalar_one_or_none()

                if existing_player is None:

                    player = Player(
                        discord_id=discord_id,
                        riot_name=riot_name,
                        riot_tag=riot_tag,
                        puuid=f"mock-puuid-{discord_id}",
                        elo=mmr,
                        wins=0,
                        losses=0,
                    )

                    session.add(player)

            # Save all new players first.
            await session.commit()

            # Queue them using the SAME session.
            for discord_id, riot_name, riot_tag, mmr in selected_mock_players:

                await QueueManager.join_queue(discord_id)

                print(
                    f"Added mock player: "
                    f"{riot_name}#{riot_tag} ({mmr})"
                )

            await session.commit()

        print("Mock player generation complete.")