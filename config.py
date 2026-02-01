import os
from dotenv import load_dotenv
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    """
    Centralized configuration for Nazh Engine.
    Using a frozen dataclass ensures settings are read-only at runtime.
    """
    # 1. Load the .env file immediately
    load_dotenv()

    # 2. Security & Credentials
    discord_token: str = os.getenv("DISCORD_TOKEN") #
    
    # 3. Infrastructure Settings
    port: int = int(os.getenv("PORT", 8080)) #
    render_commit: str = os.getenv("RENDER_GIT_COMMIT", "Local Build") #
    
    # 4. App Constants
    command_prefix: str = "!"#
    
    def validate(self):
        """SRE Fail-Fast: Validates essential environment variables."""
        if not self.discord_token:
            raise ValueError("CRITICAL: DISCORD_TOKEN is not set in the environment.") #
