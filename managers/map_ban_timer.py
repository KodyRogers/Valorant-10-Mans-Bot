import asyncio

from datetime import UTC
from datetime import datetime
from datetime import timedelta

from database import SessionLocal

from models import Match

from managers.map_ban_manager import MapBanManager


class MapTimer:

    DURATION = 30

    tasks = {}

    @staticmethod
    def start(match):

        print(f"Starting map timer for match {match.match_id}")

        match.timer_end = (
            datetime.now(UTC) +
            timedelta(seconds=MapTimer.DURATION)
        )

        task = MapTimer.tasks.get(match.match_id)

        if task:
            task.cancel()

        MapTimer.tasks[match.match_id] = asyncio.create_task(
            MapTimer.run(match.match_id)
        )


    @staticmethod
    async def run(match_id):

        try:

            while True:

                async with SessionLocal() as session:

                    match = await session.get(
                        Match,
                        match_id
                    )

                    if match is None:
                        return

                    if match.status not in (
                        "VOTE",
                        "MAP_BAN",
                        "SIDE"
                    ):
                        return

                    remaining = MapTimer.get_remaining(match)

                    if remaining <= 0:

                        if match.status == "VOTE":

                            await MapBanManager.finish_vote(
                                session,
                                match
                            )

                        elif match.status == "MAP_BAN":

                            # await MapBanManager.auto_ban(
                            #     session,
                            #     match
                            # )
                            pass

                        elif match.status == "SIDE":

                            # await MapBanManager.random_side(
                            #     session,
                            #     match
                            # )
                            pass

                        return

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass


    @staticmethod
    def get_remaining(match):

        if match.timer_end is None:
            return 0

        return max(
            0,
            int(
                (
                    match.timer_end -
                    datetime.now(UTC)
                ).total_seconds()
            )
        )