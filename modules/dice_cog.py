import discord
from discord import app_commands
from discord.ext import commands
from modules.dice_roll import DiceRoll
from modules.dice_views import MainView
from modules.metrics import metrics

class DiceCog(commands.Cog):
    """
    A modular collection of dice-related slash commands.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Roll a complex dice pool (e.g., 2d20+5)")
    @app_commands.describe(dice_input="The dice string to parse (Example: 2d20+5, 1d100)")
    async def roll(self, interaction: discord.Interaction, dice_input: str):
        """Processes a dice roll request via slash command."""
        engine = DiceRoll(dice_input)
        
        if engine.error_message != "none":
            metrics.increment("roll_failed")
            await interaction.response.send_message(
                f"⚠️ **Error:** {engine.error_message}", ephemeral=True
            )
            return
            
        metrics.increment("roll_success")
        await engine.send_result_message(interaction)

    @app_commands.command(name="build", description="Open the interactive dice pool builder")
    async def build(self, interaction: discord.Interaction):
        """Spawns the visual builder for users unfamiliar with roll syntax."""
        metrics.increment("build_requests")
        view = MainView()
        await interaction.response.send_message(
            "Select dice options below to build your pool:", 
            view=view, 
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    """Entry point for discord.py extension loading."""
    await bot.add_cog(DiceCog(bot))
