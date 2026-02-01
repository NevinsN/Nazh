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
        embed = discord.Embed(title="🎲 Nazh Engine Result", color=discord.Color.blue())
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

        # Header of the table
        table_header = "**Pool** | **Rolls** | **Total**\n:--- | :--- | :---"
        table_rows = []

        for pool in roll_data.rolls:
            label = pool.get('label', '???')
            total = pool.get('total', 1)
            display = pool.get('display', '')
            was_floored = pool.get('was_floored', False)

            # Handle Plot Bonus for d20s
            is_d20 = "d20" in label.lower()
            final_total = total + (roll_data.plot_bonus if is_d20 else 0)
            
            # Formatting flags
            floor_suffix = "*(M)*" if was_floored else ""
            plot_suffix = f" (+{roll_data.plot_bonus}P)" if is_d20 and roll_data.plot_bonus > 0 else ""

            # Create the row
            table_rows.append(f"`{label}` | `{display}` | **{final_total}**{plot_suffix}{floor_suffix}")

        # Combine into the description
        embed.description = table_header + "\n" + "\n".join(table_rows)

        if roll_data.plot_bonus > 0:
            embed.set_footer(text="P = Plot Bonus Applied | M = Minimum 1 Rule Applied")
            embed.color = discord.Color.gold()

        return embed


async def setup(bot):
    await bot.add_cog(DiceCog(bot))
