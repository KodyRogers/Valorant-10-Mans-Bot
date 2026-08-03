from discord.ext import commands

from managers.draft_timer import DraftTimer
from managers.queue_manager import QueueManager
from views.queue_view import QueueView
from mock.mock_players import MockPlayers
from database import SessionLocal

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ===================================
    # CREATE QUEUE PANEL
    # ===================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def queuepanel(self, ctx):
        """
        Creates a new queue panel.
        Run this after the bot starts.
        """

        queue = await QueueManager.get_queue()

        await ctx.send(
            embed=await QueueView.build_embed(queue),
            view=QueueView()
        )

    # ===================================
    # FORCE START
    # ===================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def start(self, ctx):
        """
        Force starts the draft.
        """

        if await QueueManager.queue_size() < 10:
            await ctx.send("There must be 10 players in queue.")
            return

        players = await QueueManager.pop_first_ten()

    # ===================================
    # RESET QUEUE
    # ===================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        """
        Clears the queue.
        """

        await QueueManager.clear_queue()

        await ctx.send("Queue has been reset.")

    # ===================================
    # SHUTDOWN BOT
    # ===================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def shutdown(self, ctx):
        """
        Safely shuts down the bot.
        """

        await ctx.send("Shutting down...")

        await self.bot.close()


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def mock_queue(self, ctx, amount: int = 10):
        """
        Mocks a queue with the specified number of players.
        """

        await QueueManager.clear_queue()

        mock_players = MockPlayers()
        await mock_players.mock_players(count=amount)

        await ctx.send("Mock queue created.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drafttimer(self, ctx, match_id: int = 1):

        
        from managers.draft_timer import DraftTimer
        await DraftTimer.start(match_id)

        await ctx.send(f"Started draft timer for {match_id}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def canceldrafttimer(self, ctx, match_id: int = 1):

        from managers.draft_timer import DraftTimer
        await DraftTimer.cancel(match_id)

        await ctx.send(f"Cancelled draft timer for {match_id}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def maptimer(self, ctx, match_id: int = 1):
        
        from managers.map_ban_timer import MapTimer
            
        print("GOT HERE")
        await MapTimer.start(match_id)


        await ctx.send(f"Started map timer for {match_id}.")

async def setup(bot):
    await bot.add_cog(Admin(bot))