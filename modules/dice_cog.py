import discord
from discord.ext import commands
from discord import app_commands
from modules.dice_roll import DiceRoll
from modules.metrics import metrics

class CommandModal(discord.ui.Modal, title="Copy Your Roll"):
    command_box = discord.ui.TextInput(label="Copy/Paste to reroll:", style=discord.TextStyle.short)
    def __init__(self, raw):
        super().__init__()
        self.command_box.default = f"/roll pool1:{raw}"
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Copied to view!", ephemeral=True)

class DiceView(discord.ui.View):
    def __init__(self, current_input: str, can_plot: bool):
        super().__init__(timeout=120)
        self.current_input = current_input
        if not can_plot: self.remove_item(self.add_pd)

    @discord.ui.button(label="Add Plot Die", style=discord.ButtonStyle.success, emoji="✨")
    async def add_pd(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_input = f"{self.current_input}, p1d6"
        # Since this logic is recursive, we call the roll command logic here
        # or simplify by just rerolling the whole new string
        cog = interaction.client.get_cog("DiceCog")
        await cog.process_roll(interaction, new_input)

    @discord.ui.button(label="Copy Command", style=discord.ButtonStyle.gray, emoji="📋")
    async def copy_cmd(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CommandModal(self.current_input))

class DiceCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def process_roll(self, interaction: discord.Interaction, full_input: str):
        engine = DiceRoll(full_input)
        if engine.error_message != "none":
            return await interaction.response.send_message(f"❌ {engine.error_message}", ephemeral=True)

        plot_boost = engine.plot_bonus
        embed = discord.Embed(title="🎲 Multi-Pool Results", color=discord.Color.blue())
        
        for r in engine.rolls:
            is_skill = r['sides'] == 20
            final_total = r['total'] + (plot_boost if is_skill else 0)
            boost_text = f" (+{plot_boost} Plot)" if is_skill and plot_boost > 0 else ""
            
            embed.add_field(
                name=f"Pool: {r['label']}{boost_text}",
                value=f"{r['display']} → **Total: {final_total}**",
                inline=False
            )

        metrics.increment("roll_success")
        view = DiceView(full_input, not ("p1d6" in full_input))
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="roll", description="Modular pool builder (Max 20 dice per pool)")
    async def roll(self, interaction: discord.Interaction, pool1: str = None, pool2: str = None, 
                   pool3: str = None, pool4: str = None, pool5: str = None, add_plot: bool = False):
        raw_inputs = [p for p in [pool1, pool2, pool3, pool4, pool5] if p]
        if add_plot: raw_inputs.append("p1d6")
        if not raw_inputs:
            return await interaction.response.send_message("❌ No pools specified!", ephemeral=True)
        
        await self.process_roll(interaction, ", ".join(raw_inputs))

async def setup(bot): await bot.add_cog(DiceCog(bot))
