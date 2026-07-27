from authlib.integrations.starlette_client import OAuth

from config import (
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET
)

oauth = OAuth()

oauth.register(
    name="discord",

    client_id=DISCORD_CLIENT_ID,
    client_secret=DISCORD_CLIENT_SECRET,

    authorize_url="https://discord.com/api/oauth2/authorize",
    access_token_url="https://discord.com/api/oauth2/token",
    api_base_url="https://discord.com/api/",

    client_kwargs={
        "scope": "identify"
    },
)