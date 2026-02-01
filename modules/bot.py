import discord
from discord.ext import commands
import logging

class NazhBot(commands.Bot):
    def __init__(self, cfg):
        # 1. Initialize Intents (Requirement for reading message content)
        intents = discord.Intents.default()
        intents.message_content = True 
        
        # 2. Pass prefix and intents to the parent class
        super().__init__(command_prefix=cfg.command_prefix, intents=intents)
        
        self.cfg = cfg
        self.logger = logging.getLogger("nazh.bot")

    async def setup_hook(self):
        """
        The setup_hook is a special discord.py method that runs before the bot connects.
        This is where professionals load 'Cogs' (Modular Command Collections).
        """
        self.logger.info("BOT_INIT: Loading command modules...")
        
        # We will move your !roll and !build commands into this Cog next
        try:
            await self.load_extension("modules.dice_cog")
            self.logger.info("BOT_INIT: Dice commands loaded successfully.")
        except Exception as e:
            self.logger.error(f"BOT_INIT_ERROR: Failed to load dice module: {e}")

    async def on_ready(self):
        """Standard health check signal."""
        self.logger.info(f"CONNECTED: {self.user} is active in {len(self.guilds)} guilds.")
        self.logger.info(f"VERSION: Running commit {self.cfg.render_commit}")
