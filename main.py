import asyncio
from config import DISCORD_TOKEN
from bot import bot
from server import iniciar_servidor


async def main():
    await iniciar_servidor()
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
