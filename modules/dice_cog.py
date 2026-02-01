import discord
from discord import app_commands
from discord.ext import commands
from modules.dice_roll import DiceRoll
from modules.dice_views import BuilderView

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Roll dice or open the visual builder")
    @app_commands.describe(
        pool="Dice string (e.g. 1d20)", 
        build="Set to True for visual builder"
    )
    async def roll(self, interaction: discord.Interaction, pool: str = None, build: bool = False):
        # 1. Handle Quick Roll (build=False)
        if not build:
            roll_str = pool if pool else "1d20" # Default for quick roll
            await interaction.response.defer(ephemeral=False)
            roll_data = DiceRoll(roll_str)
            embed = self.create_embed(interaction.user, roll_data)
            await interaction.followup.send(embed=embed)
            return

        # 2. Handle Builder (build=True)
        # Split pool string into a list if it exists, else start empty
        initial_pools = [p.strip() for p in pool.split(",")] if pool else []
        
        view = BuilderView(interaction.user.id, initial_pools)
        
        # Display logic
        staged_display = ", ".join(initial_pools) if initial_pools else "[ Empty ]"
        content = f"🏗️ **Dice Builder Session**\n**Staged:** `{staged_display}`\n**Current:** `1d20+0`"
        
        await interaction.response.send_message(
            content=content,
            view=view,
            ephemeral=True
        )

    def create_embed(self, user, roll_data):
        """Standardized result embed matching your engine's keys."""
        embed = discord.Embed(title="🎲 Nazh Engine Result", color=discord.Color.blue())
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        
        if roll_data.error_message and roll_data.error_message != "none":
            embed.description = f"❌ {roll_data.error_message}"
            embed.color = discord.Color.red()
            return embed

        for i, pool in enumerate(roll_data.rolls):
            # Mapping to engine keys: label, total, display
            label = pool.get('label', 'Unknown')
            total = pool.get('total', 0)
            display = pool.get('display', '')
            embed.add_field(name=f"Pool {i+1}: {label}", value=f"**{total}** ⟵ {display}", inline=False)
            
        if roll_data.plot_bonus > 0:
            embed.add_field(name="✨ Plot Influence", value=f"+{roll_data.plot_bonus} added to d20s!", inline=False)
        return embed

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
