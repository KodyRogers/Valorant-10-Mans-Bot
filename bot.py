import discord
from discord.ext import commands

from database import init_db
from config import DISCORD_TOKEN, HENRIK_API_KEY
from managers.queue_manager import QueueManager

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

    await init_db()
    print("Database initialized.")

    await QueueManager.clear_queue()
    print("Queue cleared.")

    await bot.load_extension("commands.player_commands")
    print("Player commands loaded.")

    await bot.load_extension("commands.admin_commands")
    print("Admin commands loaded.")


bot.run(DISCORD_TOKEN)
