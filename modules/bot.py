import discord
from discord.ext import commands
from discord import app_commands
import logging
from config import Config

class NazhBot(commands.Bot):
    """
    The core orchestrator for the Nazh Engine.
    Inherits from commands.Bot to provide modular Cog support.
    """
    def __init__(self, cfg: Config):
        intents = discord.Intents.default()
        intents.message_content = True  # Required for legacy fallback, though we use Slash
        
        super().__init__(
            command_prefix=cfg.command_prefix, 
            intents=intents,
            help_command=None
        )
        self.cfg = cfg
        self.logger = logging.getLogger("nazh.bot")

    async def setup_hook(self) -> None:
        """
        Executes during bot startup. Loads modules and syncs Slash Commands.
        """
        self.logger.info("BOT_INIT: Loading command extensions...")
        await self.load_extension("modules.dice_cog")
        
        # SRE Note: Syncing commands globally allows for instant deployment 
        # tracking across all guilds.
        self.logger.info("BOT_SYNC: Synchronizing application commands...")
        await self.tree.sync()

    async def on_ready(self) -> None:
        """Logs connectivity status and versioning metadata."""
        self.logger.info(f"CONNECTED: Logged in as {self.user} (ID: {self.user.id})")
        self.logger.info(f"INFRA: Serving {len(self.guilds)} guilds.")
        self.logger.info(f"VERSION: {self.cfg.render_commit}")
