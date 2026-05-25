import datetime
import random
import discord
from discord.ext import commands

import models
from config import DISCORD_TOKEN, HENRIK_API_KEY
from valorant_api import HenrikAPI
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

#DB
# TODO

@bot.event
async def on_ready():
    await init_db()
    print("Database initialized.")
    
    db = SessionLocal()
    
    try:
        # Clear any existing queue entries on startup
        await db.execute(delete(Queue))
        await db.commit()
        print("Cleared existing queue entries.")
    finally:
        await db.close()
    
    print("Queue Cleared")
    print(f"Logged in as {bot.user}")
    
# ==========================
# JOIN QUEUE
# ==========================
@bot.command()
async def join(ctx):

    user_id = str(ctx.author.id)

    async with SessionLocal() as session:

        # ----------------------------
        # Verify linked account
        # ----------------------------
        result = await session.execute(
            select(Player).where(
                Player.discord_id == user_id
            )
        )

        player = result.scalar_one_or_none()

        if not player:
            await ctx.send(
                "You need to link your Riot account first.\n"
                "Use `!link RiotName#Tag`"
            )
            return

        # ----------------------------
        # Already queued?
        # ----------------------------
        existing_result = await session.execute(
            select(Queue).where(
                Queue.discord_id == user_id
            )
        )

        existing_entry = existing_result.scalar_one_or_none()

        if existing_entry:
            await ctx.send(
                f"{ctx.author.mention} is already in queue."
            )
            return

        # ----------------------------
        # Queue size
        # ----------------------------
        queue_result = await session.execute(
            select(Queue)
        )

        queue_entries = queue_result.scalars().all()

        if len(queue_entries) >= 10:
            await ctx.send(
                "Queue is already full."
            )
            return

        # ----------------------------
        # Add queue entry
        # ----------------------------
        queue_entry = Queue(
            discord_id=user_id
        )

        session.add(queue_entry)

        player.is_queued = True

        await session.commit()

        current_size = len(queue_entries) + 1

        # ==================================
        # AUTO START AT 10 PLAYERS
        # ==================================
        if current_size == 10:

            # Get all queued players
            full_queue_result = await session.execute(
                select(Queue).order_by(Queue.joined_at)
            )

            full_queue = full_queue_result.scalars().all()

            players = []

            for entry in full_queue:

                player_result = await session.execute(
                    select(Player).where(
                        Player.discord_id == entry.discord_id
                    )
                )

                player = player_result.scalar_one_or_none()

                if player:
                    players.append(player)

            # ----------------------------------
            # SORT PLAYERS BY ELO
            # ----------------------------------
            players.sort(
                key=lambda p: p.elo,
                reverse=True
            )

            # ----------------------------------
            # SNAKE DRAFT
            # ----------------------------------
            team1 = []
            team2 = []

            for index, player in enumerate(players):

                # Snake pattern
                if index % 4 in [0, 3]:
                    team1.append(player)
                else:
                    team2.append(player)

            # ----------------------------------
            # TEAM ELO
            # ----------------------------------
            team1_elo = sum(p.elo for p in team1)
            team2_elo = sum(p.elo for p in team2)

            # ----------------------------------
            # FORMAT TEAMS
            # ----------------------------------
            team1_text = "\n".join(
                [
                    f"{p.riot_name}#{p.riot_tag} ({p.elo})"
                    for p in team1
                ]
            )

            team2_text = "\n".join(
                [
                    f"{p.riot_name}#{p.riot_tag} ({p.elo})"
                    for p in team2
                ]
            )

            # ----------------------------------
            # CLEAR QUEUE
            # ----------------------------------
            await session.execute(delete(Queue))

            for player in players:
                player.is_queued = False

            await session.commit()

            # ----------------------------------
            # SEND MATCH
            # ----------------------------------
            await ctx.send(
                "🔥 Queue is FULL — Match Created!\n\n"
                f"🔵 TEAM A ({team1_elo})\n"
                f"{team1_text}\n\n"
                f"🔴 TEAM B ({team2_elo})\n"
                f"{team2_text}"
            )

        # ==================================
        # NORMAL JOIN MESSAGE
        # ==================================
        else:

            await ctx.send(
                f"{ctx.author.mention} joined the queue "
                f"({current_size}/10)"
            )
                                

# ==========================
# LEAVE QUEUE
# ==========================
@bot.command()
async def leave(ctx):

    user_id = str(ctx.author.id)

    async with SessionLocal() as session:

        result = await session.execute(
            select(Queue).where(
                Queue.discord_id == user_id
            )
        )

        queue_entry = result.scalar_one_or_none()

        if not queue_entry:
            await ctx.send(
                f"{ctx.author.mention} is not in queue."
            )
            return

        # Remove queue entry
        await session.delete(queue_entry)

        # Update player status
        player_result = await session.execute(
            select(Player).where(
                Player.discord_id == user_id
            )
        )

        player = player_result.scalar_one_or_none()

        if player:
            player.is_queued = False

        await session.commit()

        # Get new queue size
        remaining_result = await session.execute(
            select(Queue)
        )

        remaining = remaining_result.scalars().all()

        await ctx.send(
            f"{ctx.author.mention} left the queue "
            f"({len(remaining)}/10)"
        )
    
# ===================================
# VIEW PLAYER INFO
# ===================================
@bot.command()
async def view(ctx, member: discord.Member = None):
    print("view command")

    # Default to command author
    target = member or ctx.author

    db = SessionLocal()

    try:
        # Get player
        result = await db.execute(
            select(Player).where(
                Player.discord_id == str(target.id)
            )
        )

        player = result.scalar_one_or_none()

        if not player:
            await ctx.send(f"{target.mention} is not registered.")
            return

        # Check queue status
        queue_result = await db.execute(
            select(Queue).where(
                Queue.discord_id == str(target.id)
            )
        )

        queue_entry = queue_result.scalar_one_or_none()

        queue_status = "Yes" if queue_entry else "No"

        # Create embed
        embed = discord.Embed(
            title=f"{target.display_name}'s Stats",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Riot ID",
            value=f"{player.riot_name}#{player.riot_tag}",
            inline=False
        )

        embed.add_field(
            name="ELO",
            value=str(player.elo),
            inline=True
        )

        embed.add_field(
            name="Wins",
            value=str(player.wins),
            inline=True
        )

        embed.add_field(
            name="Losses",
            value=str(player.losses),
            inline=True
        )

        embed.add_field(
            name="Queued",
            value=queue_status,
            inline=True
        )

        embed.add_field(
            name="Registered",
            value=player.created_at.strftime("%Y-%m-%d"),
            inline=True
        )

        embed.set_thumbnail(url=target.display_avatar.url)

        await ctx.send(embed=embed)

    finally:
        await db.close()


# ===================================
# VIEW ACTIVE QUEUE
# ===================================
@bot.command()
async def queue(ctx):
    print("queue command")

    db = SessionLocal()

    try:
        # Get queue entries ordered by join time
        result = await db.execute(
            select(Queue).order_by(Queue.joined_at)
        )

        queue_entries = result.scalars().all()

        if not queue_entries:
            await ctx.send("Queue is currently empty.")
            return

        embed = discord.Embed(
            title="Current Queue",
            color=discord.Color.green()
        )

        description = ""

        for index, entry in enumerate(queue_entries, start=1):

            # Get player info
            player_result = await db.execute(
                select(Player).where(
                    Player.discord_id == entry.discord_id
                )
            )

            player = player_result.scalar_one_or_none()

            if player:
                description += (
                    f"**{index}.** "
                    f"{player.riot_name}#{player.riot_tag} "
                    f"(ELO: {player.elo})\n"
                )
            else:
                description += (
                    f"**{index}.** Unknown Player\n"
                )

        embed.description = description

        embed.set_footer(
            text=f"{len(queue_entries)}/10 players queued"
        )

        await ctx.send(embed=embed)

    finally:
        await db.close()
    
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

    db = SessionLocal()

    try:

        result = await db.execute(
            select(Queue).order_by(Queue.joined_at)
        )

        queue_entries = result.scalars().all()

        if len(queue_entries) < 10:
            await ctx.send(
                "Need 10 players before starting."
            )
            return

        players = []

        for entry in queue_entries:

            player_result = await db.execute(
                select(Player).where(
                    Player.discord_id == entry.discord_id
                )
            )

            player = player_result.scalar_one_or_none()

            if player:
                players.append(player)

        # Shuffle teams
        random.shuffle(players)

        team1 = players[:5]
        team2 = players[5:]

        # Build output
        team1_text = "\n".join(
            [
                f"{p.riot_name}#{p.riot_tag}"
                for p in team1
            ]
        )

        team2_text = "\n".join(
            [
                f"{p.riot_name}#{p.riot_tag}"
                for p in team2
            ]
        )

        # Clear queue
        await db.execute(delete(Queue))

        for player in players:
            player.is_queued = False

        await db.commit()

        await ctx.send(
            f"🔵 Team A\n{team1_text}\n\n"
            f"🔴 Team B\n{team2_text}"
        )

    finally:
        await db.close()
    
# ===================================
# RESET QUEUE
# ===================================
@bot.command()
@commands.has_permissions(administrator=True)
async def reset(ctx):
    
    db = SessionLocal()
    
    try:
        await db.execute(delete(Queue))
        await db.commit()
    finally:
        await db.close()
        
    print("Resetting")
    # TODO

# ===================================
# MOCK QUEUE DATA
# !mock 7
# ===================================
@bot.command()
@commands.has_permissions(administrator=True)
async def mock(ctx, amount: int = 20):
    print("mock command")

    # Clamp amount between 1 and 20
    amount = max(1, min(amount, 20))

    db = SessionLocal()

    try:
        # Clear existing queue
        await db.execute(delete(Queue))

        # Mock player pool
        mock_players = [
            ("1", "TenZ", "NA1", 1450),
            ("2", "yay", "OPTIC", 1520),
            ("3", "Aspas", "BR1", 1480),
            ("4", "Demon1", "EG", 1550),
            ("5", "leaf", "C9", 1410),
            ("6", "zekken", "SEN", 1475),
            ("7", "s0m", "NRG", 1430),
            ("8", "Derke", "FNC", 1505),
            ("9", "Chronicle", "EMEA", 1510),
            ("10", "Less", "LOUD", 1495),
            ("11", "Boaster", "FNC", 1390),
            ("12", "Ethan", "NRG", 1440),
            ("13", "Crashies", "100T", 1425),
            ("14", "Victor", "SEN", 1460),
            ("15", "Marved", "NA", 1535),
            ("16", "bang", "100T", 1400),
            ("17", "Jawgemo", "EG", 1470),
            ("18", "nAts", "TL", 1515),
            ("19", "Sayf", "VIT", 1485),
            ("20", "Mako", "DRX", 1540),
        ]

        # Only take requested amount
        selected_players = mock_players[:amount]

        for discord_id, riot_name, riot_tag, elo in selected_players:

            # Check if player exists
            existing_player = await db.get(Player, discord_id)

            if not existing_player:
                player = Player(
                    discord_id=discord_id,
                    riot_name=riot_name,
                    riot_tag=riot_tag,
                    elo=elo,
                    wins=0,
                    losses=0,
                    is_queued=True
                )

                db.add(player)

            else:
                existing_player.is_queued = True

            # Add queue entry
            queue_entry = Queue(
                discord_id=discord_id
            )

            db.add(queue_entry)

        await db.commit()

        await ctx.send(
            f"Mock queue created with {amount}/10 players."
        )

    finally:
        await db.close()

# ===================================
# ERROR HANDLING
# ===================================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    else:
        print(error)
        
