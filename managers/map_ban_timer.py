import asyncio
import time

from database import SessionLocal

from managers.websocket_manager import draft_connections


class MapTimer:

    #
    # Running timers
    #
    timers = {}

    started = {}

    #
    # Length of each phase
    #
    PHASE_TIME = 15


    # ===========================
    # START TIMER
    # ===========================

    @staticmethod
    async def start(match_id: int):

        #
        # Cancel previous timer
        #
        await MapTimer.cancel(match_id)

        MapTimer.started[match_id] = time.time()
        
        print("MAP TIMER STARTED!")
        task = asyncio.create_task(

            MapTimer._run(match_id)

        )

        MapTimer.timers[match_id] = task


    # ===========================
    # GET REMAINING
    # ===========================

    @staticmethod
    def get_remaining(match_id):

        started = MapTimer.started.get(match_id)

        if started is None:
            return MapTimer.PHASE_TIME

        elapsed = int(time.time() - started)

        return max(
            0,
            MapTimer.PHASE_TIME - elapsed
        )


    # ===========================
    # CANCEL TIMER
    # ===========================

    @staticmethod
    async def cancel(match_id: int):

        task = MapTimer.timers.pop(
            match_id,
            None
        )

        if task:

            task.cancel()


    # ===========================
    # TIMER LOOP
    # ===========================

    @staticmethod
    async def _run(match_id: int):

        from managers.match_manager import MatchManager
        from managers.map_ban_manager import MapBanManager

        try:

            await asyncio.sleep(
                MapTimer.PHASE_TIME
            )

            async with SessionLocal() as session:

                match = await MatchManager.get_match_by_id(
                    session,
                    match_id
                )

                if not match:
                    return

                #
                # Match already moved on?
                #

                if match.status not in (
                    "VOTE",
                    "MAP_BAN",
                    "SIDE"
                ):
                    return

                #
                # Vote timeout
                #

                if match.status == "VOTE":

                    success = await MapBanManager.finish_vote(
                        session,
                        match
                    )
                    if success:
                        await draft_connections.broadcast(
                            match.match_code,
                            {
                                "type": "refresh"
                            }
                        )

                    await MapTimer.start(
                        match.match_id
                    )

                #
                # Ban timeout
                #

                elif match.status == "MAP_BAN":
                    success = await MapBanManager.auto_ban(
                        session,
                        match
                    )

                    if success:
                        await draft_connections.broadcast(
                            match.match_code,
                            {
                                "type": "refresh"
                            }
                        )

                    await MapTimer.start(
                        match.match_id
                    )
                #
                # Side timeout
                #

                elif match.status == "SIDE":
                    pass
                    # await MapBanManager.random_side(
                    #     session,
                    #     match
                    # )

        except asyncio.CancelledError:

            #
            # Timer cancelled
            #

            pass