import discord
from discord.ext import commands
from discord import app_commands
from modules.dice_roll import DiceRoll
from modules.metrics import metrics

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Standard or Positional Tag Roll (e.g., ad2d20)")
    @app_commands.describe(
        dice_string="Quick roll (e.g., 'ad2d20+5')",
        dice="Number of dice",
        sides="Number of sides",
        tags="Positional tags (a/d)",
        modifier="Flat bonus"
    )
    async def roll(
        self, 
        interaction: discord.Interaction, 
        dice_string: str = None,
        dice: int = None,
        sides: int = None,
        tags: str = "",
        modifier: int = 0
    ):
        # 1. Determine input source
        if dice_string:
            full_input = dice_string
        elif dice and sides:
            metrics.increment("build_requests")
            mod_part = f"{modifier:+}" if modifier != 0 else ""
            full_input = f"{tags}{dice}d{sides}{mod_part}"
        else:
            await interaction.response.send_message("❌ Provide either a `dice_string` OR `dice` and `sides`.", ephemeral=True)
            return

        # 2. Execute Engine
        engine = DiceRoll(full_input)
        
        if engine.error_message != "none":
            metrics.increment("roll_failed")
            await interaction.response.send_message(f"❌ {engine.error_message}", ephemeral=True)
        else:
            metrics.increment("roll_success")
            await engine.send_result_message(interaction)

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
