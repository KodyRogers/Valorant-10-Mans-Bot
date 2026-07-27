import os
from dotenv import load_dotenv

load_dotenv("API_KEYS.env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HENRIK_API_KEY = os.getenv("HENRIKDEV_API_KEY")

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
SESSION_SECRET = os.getenv("SESSION_SECRET")
