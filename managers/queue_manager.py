from sqlalchemy import select, delete
from database import SessionLocal
from models import Player, Queue

QUEUE_SIZE = 10


class QueueManager:

    @staticmethod
    async def join_queue(discord_id: str):
        async with SessionLocal() as session:

            if await QueueManager.is_full():
                return False, "Queue is full.", None
            
            # Player exists?
            result = await session.execute(
                select(Player).where(Player.discord_id == discord_id)
            )
            player = result.scalar_one_or_none()

            if player is None:
                return False, "Player is not registered.", None

            if player.is_queued:
                return False, "You are already in queue.", None

            # Update player
            player.is_queued = True

            # Add queue entry
            session.add(
                Queue(discord_id=discord_id)
            )

            await session.commit()

            size = await QueueManager.queue_size()

            return (
                True,
                f"✅ You joined the queue! ({size}/{QUEUE_SIZE})",
                size
            )

    @staticmethod
    async def leave_queue(discord_id: str):
        async with SessionLocal() as session:

            result = await session.execute(
                select(Player).where(Player.discord_id == discord_id)
            )

            player = result.scalar_one_or_none()

            if player is None:
                return False, "Player not found.", None

            if not player.is_queued:
                return False, "You are not in queue.", None

            player.is_queued = False

            await session.execute(
                delete(Queue).where(
                    Queue.discord_id == discord_id
                )
            )

            await session.commit()

            size = await QueueManager.queue_size()

            return (
                True,
                f"❌ You left the queue. ({size}/{QUEUE_SIZE})",
                size
            )

    @staticmethod
    async def queue_size():

        async with SessionLocal() as session:

            result = await session.execute(
                select(Queue)
            )

            return len(result.scalars().all())

    @staticmethod
    async def get_queue():

        async with SessionLocal() as session:

            result = await session.execute(
                select(Queue).order_by(Queue.joined_at)
            )

            return result.scalars().all()

    @staticmethod
    async def clear_queue():

        async with SessionLocal() as session:

            players = await session.execute(
                select(Player).where(Player.is_queued == True)
            )

            for player in players.scalars():
                player.is_queued = False

            await session.execute(delete(Queue))

            await session.commit()

    @staticmethod
    async def is_full():
        return await QueueManager.queue_size() >= QUEUE_SIZE

    @staticmethod
    async def pop_first_ten():

        async with SessionLocal() as session:

            result = await session.execute(
                select(Queue)
                .order_by(Queue.joined_at)
                .limit(10)
            )

            queue = result.scalars().all()

            players = []

            for entry in queue:

                result = await session.execute(
                    select(Player).where(
                        Player.discord_id == entry.discord_id
                    )
                )

                player = result.scalar_one()

                player.is_queued = False

                players.append(player)

                await session.delete(entry)

            await session.commit()

            return players