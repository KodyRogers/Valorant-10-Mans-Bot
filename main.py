import asyncio
import uvicorn

from old.bot import bot
from config import DISCORD_TOKEN
from web import app


async def start_bot():
    await bot.start(DISCORD_TOKEN)


async def start_api():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        start_bot(),
        start_api()
    )


if __name__ == "__main__":
    asyncio.run(main())