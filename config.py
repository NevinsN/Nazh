import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Config:
    """
    Centralized configuration manager for the Nazh Engine.
    
    Attributes:
        discord_token (str): Secret key for Discord API.
        port (int): Web server port for dashboard.
        render_commit (str): Git hash for version traceability.
        command_prefix (str): Bot trigger prefix.
    """
    load_dotenv()
    
    discord_token: str = os.getenv("DISCORD_TOKEN")
    port: int = int(os.getenv("PORT", 8080))
    render_commit: str = os.getenv("RENDER_GIT_COMMIT", "Local-Dev")
    command_prefix: str = "!"

    def validate(self) -> None:
        """Validates that all critical environment variables are present."""
        if not self.discord_token:
            raise ValueError("CRITICAL: DISCORD_TOKEN is missing.")
