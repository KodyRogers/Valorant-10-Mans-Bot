import asyncio
import random
import time

from database import SessionLocal
from managers.websocket_manager import draft_connections

class DraftTimer:

    #
    # Running timers
    #
    # { match_id : asyncio.Task }
    #
    timers = {}

    started = {}

    #
    # Length of each pick
    #
    PICK_TIME = 10


    # ===========================
    # START TIMER
    # ===========================

    @staticmethod
    async def start(match_id: int):

        #
        # Cancel previous timer
        #
        await DraftTimer.cancel(match_id)

        DraftTimer.started[match_id] = time.time()

        task = asyncio.create_task(

            DraftTimer._run(match_id)

        )

        DraftTimer.timers[match_id] = task


    @staticmethod
    def get_remaining(match_id):

        started = DraftTimer.started.get(match_id)

        if started is None:
            return DraftTimer.PICK_TIME

        elapsed = int(time.time() - started)

        return max(
            0,
            DraftTimer.PICK_TIME - elapsed
        )

    # ===========================
    # CANCEL TIMER
    # ===========================

    @staticmethod
    async def cancel(match_id: int):

        task = DraftTimer.timers.pop(
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
        try:

            await asyncio.sleep(
                DraftTimer.PICK_TIME
            )
            async with SessionLocal() as session:
                
                match = await MatchManager.get_match_by_id(
                    session,
                    match_id
                )
                
                if not match:
                    return
                
                #
                # Draft finished?
                #
                
                if match.status != "DRAFTING":
                    print("timer stopped")
                    return
                
                #
                # Random draft
                #

                await DraftTimer.random_pick(
                    session,
                    match
                )

        except asyncio.CancelledError:

            #
            # Timer cancelled
            #

            pass


    # ===========================
    # RANDOM PICK
    # ===========================

    @staticmethod
    async def random_pick(
        session,
        match
    ):
        from managers.draft_manager import DraftManager
        from managers.match_manager import MatchManager
        players = await MatchManager.get_match_players(
            session,
            match.match_id
        )

        available = [

            player

            for player in players

            if player.team == "None"

        ]


        if not available:
            return

        player = random.choice(
            available
        )
        print(player.discord_id)
        #
        # Timeout ignores captain check
        #
        current_captain = await DraftManager.get_current_captain(session, match)

        success = await DraftManager.make_pick(

            session=session,

            match=match,

            discord_id= str(current_captain.discord_id),

            player_id=player.discord_id,

        )

        #
        # Continue draft
        #

        if success:

            await draft_connections.broadcast(
                match.match_code,
                {
                    "type": "refresh"
                }
            )

            await DraftTimer.start(
                match.match_id
            )