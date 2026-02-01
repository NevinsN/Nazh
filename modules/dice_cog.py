import discord
from discord import app_commands
from discord.ext import commands
from modules.dice_roll import DiceRoll

class AddPoolModal(discord.ui.Modal, title="Add Another Dice Pool"):
    pool_input = discord.ui.TextInput(
        label="Pool String",
        placeholder="e.g., 2d6+2 or a1d20",
        min_length=2,
        max_length=20,
    )

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        # Add to the builder's stack
        self.parent_view.pools.append(self.pool_input.value)
        await self.parent_view.update_builder_message(interaction)

class DiceBuilderView(discord.ui.View):
    def __init__(self, user_id: int, initial_pools: list, cog):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.pools = initial_pools
        self.cog = cog

    async def update_builder_message(self, interaction: discord.Interaction):
        pool_display = "\n".join([f"🔹 `{p}`" for p in self.pools])
        content = f"🏗️ **Dice Builder Session**\n\n**Staged Pools:**\n{pool_display}\n\n*Add more dice or finalize to roll publicly!*"
        await interaction.response.edit_message(content=content, view=self)

    @discord.ui.button(label="Add Pool", style=discord.ButtonStyle.secondary, emoji="➕")
    async def add_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddPoolModal(self))

    @discord.ui.button(label="Roll Publicly", style=discord.ButtonStyle.primary, emoji="🎲")
    async def roll_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        full_input = ", ".join(self.pools)
        # Finalize by sending a public roll and clearing the ephemeral staging
        await self.cog.process_roll(interaction, full_input, ephemeral=False)
        await interaction.edit_original_response(content="✅ **Roll finalized and sent!**", view=None)
        self.stop()

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Quick roll or build a multi-pool session")
    @app_commands.describe(
        pool="Dice string (e.g. '1d20+5')",
        build="Set to True to stage multiple pools privately before rolling"
    )
    async def roll(self, interaction: discord.Interaction, pool: str = "1d20", build: bool = False):
        if not build:
            # FAST PATH: Immediate public response
            await self.process_roll(interaction, pool, ephemeral=False)
        else:
            # BUILDER PATH: Ephemeral staging
            view = DiceBuilderView(interaction.user.id, [pool], self)
            await interaction.response.send_message(
                content=f"🏗️ **Dice Builder Session**\n\n**Staged Pools:**\n🔹 `{pool}`\n\n*Add more dice or finalize to roll publicly!*",
                view=view,
                ephemeral=True
            )

    async def process_roll(self, interaction: discord.Interaction, pool_str: str, ephemeral: bool = False):
        # Your existing engine integration logic
        try:
            roll_data = DiceRoll(pool_str)
            # (Insert your logic here for creating the Embed based on roll_data)
            # For brevity, assuming embed creation is handled...
            embed = self.create_embed(roll_data) 
            
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
