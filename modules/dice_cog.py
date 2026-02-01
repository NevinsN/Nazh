import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from modules.dice_roll import DiceRoll
from modules.dice_views import BuilderView

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Quick roll or build a session")
    async def roll(self, interaction: discord.Interaction, pool: Optional[str] = None, build: bool = False):
        roll_str = pool if pool else "1d20"
        
        if not build:
            # FIX: Defer immediately to prevent timeout
            await interaction.response.defer(ephemeral=False)
            roll_data = DiceRoll(roll_str)
            embed = self.create_embed(interaction.user, roll_data)
            await interaction.followup.send(embed=embed, view=CopyButtonView(roll_str))
        else:
            initial_pools = [p.strip() for p in pool.split(",")] if pool else []
            view = BuilderView(interaction.user.id, initial_pools)
            staged = ", ".join(initial_pools) if initial_pools else "[ Empty ]"
            content = f"🏗️ **Dice Builder**\n**Staged:** `{staged}`\n**Current:** `1d20+0`"
            await interaction.response.send_message(content=content, view=view, ephemeral=True)

    def create_embed(self, user, roll_data):
        embed = discord.Embed(title="🎲 Nazh Engine Result", color=discord.Color.blue())
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        
        if roll_data.error_message:
            embed.description = f"❌ {roll_data.error_message}"
            return embed

        # Table Header
        table = "**Pool** | **Rolls** | **Total**\n:--- | :--- | :---"
        rows = []
        for p in roll_data.rolls:
            is_d20 = "d20" in p['label'].lower()
            total = p['total'] + (roll_data.plot_bonus if is_d20 else 0)
            floor = " *(M)*" if p['was_floored'] else ""
            plot = f" (+{roll_data.plot_bonus}P)" if is_d20 and roll_data.plot_bonus > 0 else ""
            rows.append(f"`{p['label']}` | `{p['display']}` | **{total}**{plot}{floor}")

        embed.description = table + "\n" + "\n".join(rows)
        if roll_data.plot_bonus > 0:
            embed.set_footer(text="P = Plot Bonus | M = Minimum 1 Applied")
            embed.color = discord.Color.gold()
        return embed

class CopyButtonView(discord.ui.View):
    def __init__(self, roll_str: str):
        super().__init__(timeout=None)
        self.roll_str = roll_str

    @discord.ui.button(label="Copy String", style=discord.ButtonStyle.secondary, emoji="📋")
    async def copy_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content=f"`/roll pool:{self.roll_str}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
