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
        # 1. Logic Fix: Use 'pool' if provided, otherwise default to 1d20
        roll_str = pool if pool else "1d20"
        
        if not build:
            await interaction.response.defer(ephemeral=False)
            roll_data = DiceRoll(roll_str)
            embed = self.create_embed(interaction.user, roll_data)
            
            # Add the Copy Button back
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Copy Roll", style=discord.ButtonStyle.link, url=f"https://discord.com/channels/@me")) # Placeholder/Helper
            # Note: link buttons can't copy to clipboard, so we use a standard button for that logic
            
            await interaction.followup.send(embed=embed, view=CopyButtonView(roll_str))
        else:
            initial_pools = [p.strip() for p in pool.split(",")] if pool else []
            view = BuilderView(interaction.user.id, initial_pools)
            staged_display = ", ".join(initial_pools) if initial_pools else "[ Empty ]"
            content = f"🏗️ **Dice Builder Session**\n**Staged:** `{staged_display}`\n**Current:** `1d20+0`"
            await interaction.response.send_message(content=content, view=view, ephemeral=True)

    def create_embed(self, user, roll_data):
        embed = discord.Embed(title="🎲 Nazh Engine Result", color=discord.Color.blue())
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        
        if roll_data.error_message and roll_data.error_message.lower() != "none":
            embed.description = f"❌ {roll_data.error_message}"
            return embed

        table_header = "**Pool** | **Rolls** | **Total**\n:--- | :--- | :---"
        table_rows = []
        for pool in roll_data.rolls:
            label, total, display = pool.get('label'), pool.get('total'), pool.get('display')
            is_d20 = "d20" in label.lower()
            final_total = total + (roll_data.plot_bonus if is_d20 else 0)
            floor_suffix = "*(M)*" if pool.get('was_floored') else ""
            plot_suffix = f" (+{roll_data.plot_bonus}P)" if is_d20 and roll_data.plot_bonus > 0 else ""
            table_rows.append(f"`{label}` | `{display}` | **{final_total}**{plot_suffix}{floor_suffix}")

        embed.description = table_header + "\n" + "\n".join(table_rows)
        if roll_data.plot_bonus > 0:
            embed.set_footer(text="P = Plot Bonus | M = Minimum 1 Rule")
            embed.color = discord.Color.gold()
        return embed

class CopyButtonView(discord.ui.View):
    """Simple view to hold the Copy Roll button."""
    def __init__(self, roll_str: str):
        super().__init__(timeout=None)
        self.roll_str = roll_str

    @discord.ui.button(label="Copy String", style=discord.ButtonStyle.secondary, emoji="📋")
    async def copy_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending the string in a hidden message makes it easy for user to copy
        await interaction.response.send_message(content=f"`/roll pool:{self.roll_str}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
