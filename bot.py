import discord
from discord.ext import commands

from config import DISCORD_TOKEN

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot Setup
bot = commands.Bot(command_prefix = "!", intents = intents)

#DB
# TODO

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # TODO ADD DB
    
# ==========================
# JOIN QUEUE
# ==========================
@bot.command()
async def join(ctx):
    print("join working")
    #TODO

# ==========================
# Leave Queue
# ==========================
@bot.command()
async def leave(ctx):
    print("leave command")
    #TODO
    
# ==========================
# View Queue
# ==========================
@bot.command()
async def view(ctx):
    print("view command")
    #TODO
    
# ==========================
# Link RIOT Account
# ==========================
@bot.command(name="link")
async def link_riot(ctx, riot_id: str):
    print("link working", riot_id)
    #TODO
    
# ===================================
# FORCE START
# ===================================
@bot.command()
@commands.has_permissions(administrator=True)
async def start(ctx):
    print("Starting")
    # TODO
    
# ===================================
# RESET QUEUE
# ===================================
@bot.command()
@commands.has_permissions(administrator=True)
async def reset(ctx):
    print("Resetting")
    # TODO
    
# ===================================
# ERROR HANDLING
# ===================================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    else:
        print(error)
        
#run
bot.run(DISCORD_TOKEN)