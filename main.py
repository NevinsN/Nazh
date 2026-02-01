import asyncio
import logging
from config import Config
from modules.logger import setup_logging
from modules.bot import NazhBot
from web_server import keep_alive

async def main():
    # 1. Setup
    setup_logging()
    cfg = Config()
    cfg.validate()
    
    # 2. Initialization
    bot = NazhBot(cfg)
    
    # 3. Observability
    keep_alive(bot)
    
    # 4. Run
    async with bot:
        await bot.start(cfg.discord_token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("System shut down by user.")
