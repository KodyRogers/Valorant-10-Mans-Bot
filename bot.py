import discord
from discord.ext import commands

import models
from config import DISCORD_TOKEN, HENRIK_API_KEY
from valorant_api import HenrikAPI
from queue_manager import QueueManager
from database import init_db, SessionLocal
from models import Player, Queue

from sqlalchemy import select, delete

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot Setup
bot = commands.Bot(command_prefix = "!", intents = intents)

# API and Queue Manager Instances
vapi = HenrikAPI(HENRIK_API_KEY)
queue_manager = QueueManager()

#DB
# TODO

@bot.event
async def on_ready():
    await init_db()
    print("Database initialized.")
    print(f"Logged in as {bot.user}")
    
# ==========================
# JOIN QUEUE
# ==========================
@bot.command()
async def join(ctx):
    
    user_id = str(ctx.author.id)
    username = ctx.author.name
    
    async with SessionLocal() as session:
        # Check if player has linked their Riot account
        result = await session.execute(
            select(Player).where(Player.discord_id == user_id)
        )
        player = result.scalar_one_or_none()
        
        if not player:
            await ctx.send("You need to link your Riot account before joining the queue. Use `!link RiotName#Tag`.")
            return
    
    message = queue_manager.add_player(user_id, username)
    if "has been added" in message:
        # Add player to database queue
        async with SessionLocal() as session:
            queue_entry = Queue(discord_id=user_id)
            session.add(queue_entry)
            await session.commit()
        
    await ctx.send(message)
                                

# ==========================
# Leave Queue
# ==========================
@bot.command()
async def leave(ctx):
    user_id = str(ctx.author.id)
    username = ctx.author.display_name

    # Remove from queue manager
    message = queue_manager.remove_player(user_id, username)

    # Remove from DB
    if "has been removed" in message:
        async with SessionLocal() as session:
            await session.execute(
                delete(Queue).where(Queue.discord_id == user_id)
            )

            await session.commit()

    await ctx.send(message)
    
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
async def link_riot(ctx, *,riot_id: str):
    print("link working", riot_id)
    split_id = riot_id.split("#")
    if len(split_id) != 2:
        await ctx.send("Invalid format. Please use `!link RiotName#Tag`.")
        return
    
    name = split_id[0]
    tag = split_id[1]
    
    response = vapi.get_account(name, tag)
    if response is None:
        await ctx.send("Could not find Riot account. Please check the name and tag and try again.")
        return
    
    discord_id = str(ctx.author.id)
    
    async with SessionLocal() as session:
        # Check if player already exists
        result = await session.execute(
            select(Player).where(Player.discord_id == discord_id)
        )

        player = result.scalar_one_or_none()

        if player:
            # Update existing account
            player.riot_name = name
            player.riot_tag = tag
        else:
            # Create new player
            new_player = Player(
                discord_id=discord_id,
                riot_name=name,
                riot_tag=tag
            )

            session.add(new_player)

        await session.commit()

        await ctx.send(f"Riot account `{name}#{tag}` linked successfully.")
        
    
    
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
        
