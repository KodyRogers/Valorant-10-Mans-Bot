import asyncio
import random
import time

from database import SessionLocal

from managers.match_manager import MatchManager
from managers.draft_manager import DraftManager


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
    PICK_TIME = 3


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

        success = await DraftManager.make_pick(

            session=session,

            match=match,

            player_id=player.discord_id,

        )

        #
        # Continue draft
        #

        if success:

            await DraftTimer.start(
                match.match_id
            )