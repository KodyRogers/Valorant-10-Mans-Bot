from discord.ext import commands

from managers.player_manager import PlayerManager


class PlayerCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register(self, ctx, * ,riot_id: str = None):

        if riot_id is None:
            await ctx.send("Please provide your Riot ID in the format: RiotName#Tagline")
            return

        split_id = riot_id.split("#")
        if (len(split_id) != 2):
            await ctx.send("Invalid Riot ID format. Please use the format: RiotName#Tagline")
            return
        
        riot_name, riot_tag = split_id
        success, message = await PlayerManager.register_player(
            discord_id=str(ctx.author.id),
            riot_name=riot_name,
            riot_tag=riot_tag
        )

        await ctx.send(message)

    @commands.command()
    async def change_riot_id(self, ctx, *, new_riot_id: str = None):

        if new_riot_id is None:
            await ctx.send("Please provide your new Riot ID in the format: RiotName#Tagline")
            return
        
        split_id = new_riot_id.split("#")
        if (len(split_id) != 2):
            await ctx.send("Invalid Riot ID format. Please use the format: RiotName#Tagline")
            return
        
        new_riot_name, new_riot_tag = split_id
        success, message = await PlayerManager.change_riot_id(
            discord_id=str(ctx.author.id),
            new_riot_name=new_riot_name,
            new_riot_tag=new_riot_tag
        )

        await ctx.send(message)

    @commands.command()
    async def help(self, ctx):
        """
        Displays the help message for player commands.
        """

        help_message = (
            "**Player Commands:**\n"
            "`!register <RiotName#Tagline>` - Register your Riot account.\n"
            "`!change_riot_id <NewRiotName#NewTagline>` - Change your registered Riot account.\n"
            "`!help` - Display this help message."
        )

        await ctx.send(help_message)

async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))