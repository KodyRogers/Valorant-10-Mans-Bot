import os
from dotenv import load_dotenv

load_dotenv("API_KEYS.env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HENRIK_API_KEY = os.getenv("HENRIKDEV_API_KEY")

