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
    @app_commands.describe(pool="Dice string (e.g. 1d20+5)", build="True to use the visual builder")
    async def roll(self, interaction: discord.Interaction, pool: Optional[str] = None, build: bool = False):
        if not build:
            # --- Fast Path ---
            roll_str = pool if pool else "1d20"
            await interaction.response.defer(ephemeral=False)
            
            roll_data = DiceRoll(roll_str)
            embed = self.create_embed(interaction.user, roll_data)
            await interaction.followup.send(embed=embed)
        else:
            # --- Builder Path ---
            initial_pools = [p.strip() for p in pool.split(",")] if pool else []
            view = BuilderView(interaction.user.id, initial_pools)
            
            staged_display = ", ".join(initial_pools) if initial_pools else "[ Empty ]"
            content = (
                f"🏗️ **Dice Builder Session**\n"
                f"**Staged:** `{staged_display}`\n"
                f"**Current:** `1d20+0`"
            )
            
            await interaction.response.send_message(content=content, view=view, ephemeral=True)

    def create_embed(self, user, roll_data):
        """Constructs the final result embed with 'Min 1' and 'Plot' logic."""
        embed = discord.Embed(title="🎲 Nazh Engine Result", color=discord.Color.blue())
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        
        # 1. Handle Engine Errors
        if roll_data.error_message and roll_data.error_message.lower() != "none":
            embed.description = f"❌ **Syntax Error:** {roll_data.error_message}"
            embed.color = discord.Color.red()
            return embed

        # 2. Iterate through pools
        for i, pool in enumerate(roll_data.rolls):
            label = pool.get('label', 'Unknown')
            total = pool.get('total', 1)
            display = pool.get('display', '')
            was_floored = pool.get('was_floored', False)
            
            # Apply Plot Bonus to d20 pools visually
            # (Note: Engine calculates plot_bonus, Cog applies it to d20 totals)
            is_d20 = "d20" in label.lower()
            final_total = total + (roll_data.plot_bonus if is_d20 else 0)
            
            # Construct the value string
            bonus_note = f" (+{roll_data.plot_bonus} Plot)" if is_d20 and roll_data.plot_bonus > 0 else ""
            floor_note = " *(Min. 1 Applied)*" if was_floored else ""
            
            value_str = f"**{final_total}**{bonus_note}{floor_note}\n⟵ {display}"

            embed.add_field(
                name=f"Pool {i+1}: {label}", 
                value=value_str, 
                inline=False
            )
            
        # 3. Plot Influence Branding
        if roll_data.plot_bonus > 0:
            embed.add_field(
                name="✨ Plot Influence", 
                value=f"A Plot Die was active! Added **+{roll_data.plot_bonus}** to all d20 pools.", 
                inline=False
            )
            embed.color = discord.Color.gold()
            
        return embed

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
