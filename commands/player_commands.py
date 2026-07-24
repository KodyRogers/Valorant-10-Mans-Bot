from discord.ext import commands

from managers.player_manager import PlayerManager


class Register(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="register")
    async def register(
        self,
        ctx,
        riot_id: str,
    ):

        riot_name, riot_tag = riot_id.split("#")

        success, message = await PlayerManager.register_player(
            discord_id=str(ctx.author.id),
            riot_name=riot_name,
            riot_tag=riot_tag
        )

        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Register(bot))