from discord.ext import commands

from managers.queue_manager import QueueManager
from managers.draft_manager import DraftManager
from views.queue_view import QueueView


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
            embed=QueueView.build_embed(queue),
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

        await DraftManager.start_draft(
            self.bot,
            ctx.channel,
            players
        )

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


async def setup(bot):
    await bot.add_cog(Admin(bot))