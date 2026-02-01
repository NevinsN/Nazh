import discord
from discord.ext import commands
from discord import app_commands
from modules.dice_roll import DiceRoll
from modules.metrics import metrics

class CommandModal(discord.ui.Modal, title="Copy Your Roll"):
    command_box = discord.ui.TextInput(label="Copy/Paste this to reroll:", style=discord.TextStyle.short)
    def __init__(self, raw):
        super().__init__()
        self.command_box.default = f"/roll dice_string:{raw}"
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Copied!", ephemeral=True)

class DiceView(discord.ui.View):
    def __init__(self, current_input: str, can_plot: bool):
        super().__init__(timeout=120)
        self.current_input = current_input
        if not can_plot: self.remove_item(self.add_pd)

    @discord.ui.button(label="Add Plot Die", style=discord.ButtonStyle.secondary, emoji="✨")
    async def add_pd(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_input = f"{self.current_input}, p1d6"
        engine = DiceRoll(new_input)
        await engine.send_result_message(interaction, view=DiceView(new_input, False))

    @discord.ui.button(label="Copy Command", style=discord.ButtonStyle.gray, emoji="📋")
    async def copy_cmd(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CommandModal(self.current_input))

class DiceCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="roll", description="Standard/Plot Dice Roll")
    async def roll(self, interaction: discord.Interaction, dice: int = 1, sides: int = 20, 
                   add_plot_die: bool = False, tags: str = "", modifier: int = 0, dice_string: str = None):
        if dice_string:
            full_input = dice_string
        else:
            p_tag = ", p1d6" if add_plot_die else ""
            m_tag = f"{modifier:+}" if modifier != 0 else ""
            full_input = f"{tags}{dice}d{sides}{p_tag}{m_tag}"
        
        engine = DiceRoll(full_input)
        if engine.error_message != "none":
            await interaction.response.send_message(f"❌ {engine.error_message}", ephemeral=True)
            metrics.increment("roll_failed")
        else:
            metrics.increment("roll_success")
            view = DiceView(full_input, not ("p1d6" in full_input))
            await engine.send_result_message(interaction, view=view)

async def setup(bot): await bot.add_cog(DiceCog(bot))
