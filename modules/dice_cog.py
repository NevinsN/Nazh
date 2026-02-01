import discord
from discord import app_commands
from discord.ext import commands
from modules.dice_roll import DiceRoll
from modules.dice_views import BuilderView

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Quick roll or build a session")
    async def roll(self, interaction: discord.Interaction, pool: Optional[str] = None, build: bool = False):
        if not build:
            # Fast Path: 1d20 default if no pool provided
            roll_str = pool if pool else "1d20"
            await interaction.response.defer(ephemeral=False)
            roll_data = DiceRoll(roll_str)
            embed = self.create_embed(interaction.user, roll_data)
            await interaction.followup.send(embed=embed)
        else:
            # Builder Path
            initial_pools = [p.strip() for p in pool.split(",")] if pool else []
            view = BuilderView(interaction.user.id, initial_pools)
            
            staged_display = ", ".join(initial_pools) if initial_pools else "[ Empty ]"
            content = f"🏗️ **Dice Builder Session**\n**Staged:** `{staged_display}`\n**Current:** `1d20+0`"
            
            await interaction.response.send_message(content=content, view=view, ephemeral=True)

    def create_embed(self, user, roll_data):
        """Constructs the result embed using engine data."""
        embed = discord.Embed(title="🎲 Nazh Engine Result", color=discord.Color.blue())
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        
        # Check for error state (None vs "none")
        if roll_data.error_message and roll_data.error_message.lower() != "none":
            embed.description = f"❌ {roll_data.error_message}"
            embed.color = discord.Color.red()
            return embed

        for i, pool in enumerate(roll_data.rolls):
            # Map keys: label, total, display
            label = pool.get('label', 'Unknown')
            total = pool.get('total', 0)
            display = pool.get('display', '')
            
            # Apply Plot Bonus to d20 pools visually
            is_d20 = "d20" in label.lower()
            final_total = total + (roll_data.plot_bonus if is_d20 else 0)
            bonus_note = f" (+{roll_data.plot_bonus})" if is_d20 and roll_data.plot_bonus > 0 else ""

            embed.add_field(
                name=f"Pool {i+1}: {label}", 
                value=f"**{final_total}**{bonus_note}\n⟵ {display}", 
                inline=False
            )
            
        if roll_data.plot_bonus > 0:
            embed.add_field(name="✨ Plot Influence", value=f"Bonus of +{roll_data.plot_bonus} added to d20s.", inline=False)
            embed.color = discord.Color.gold()
            
        return embed

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
