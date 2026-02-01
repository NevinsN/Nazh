import discord
from discord import app_commands
from discord.ext import commands
from modules.dice_roll import DiceRoll

class AddPoolModal(discord.ui.Modal, title="Configure Dice Pool"):
    num_dice = discord.ui.TextInput(label="Number of Dice", default="1", max_length=2)
    sides = discord.ui.TextInput(label="Dice Sides", default="20", max_length=3)
    modifier = discord.ui.TextInput(label="Modifier (+/-)", default="0", required=False)
    tags = discord.ui.TextInput(label="Tags (a=Adv, d=Disadv)", required=False, max_length=1)

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        # We MUST acknowledge the modal submit immediately
        await interaction.response.defer(ephemeral=True)
        
        tag = self.tags.value.lower() if self.tags.value else ""
        mod = self.modifier.value if self.modifier.value else "0"
        # Ensure mod has a sign
        if mod.isdigit() or (mod.startswith('-') and mod[1:].isdigit()):
            mod = f"{int(mod):+}" if int(mod) != 0 else ""
        
        pool_string = f"{tag}{self.num_dice.value}d{self.sides.value}{mod}"
        self.parent_view.pools.append(pool_string)
        
        # Update the original builder message
        await self.parent_view.update_builder_message(interaction)

class DiceBuilderView(discord.ui.View):
    def __init__(self, user_id: int, initial_pools: list, cog):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.pools = initial_pools
        self.cog = cog

    @discord.ui.button(label="Add Pool", style=discord.ButtonStyle.secondary, emoji="➕")
    async def add_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddPoolModal(self))

    @discord.ui.button(label="Add Plot Die", style=discord.ButtonStyle.success, emoji="🎭")
    async def plot_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        self.pools.append("p1d6")
        button.disabled = True
        button.label = "Plot Die Added"
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Remove Last", style=discord.ButtonStyle.danger, emoji="🔙")
    async def undo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if self.pools:
            removed = self.pools.pop()
            if removed == "p1d6":
                for child in self.children:
                    if isinstance(child, discord.ui.Button) and "Plot" in str(child.label):
                        child.disabled = False
                        child.label = "Add Plot Die"
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Roll Publicly", style=discord.ButtonStyle.primary, emoji="🎲")
    async def roll_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Defer immediately to prevent 404/10062
        await interaction.response.defer(ephemeral=True)
        
        # 2. Process math
        full_input = ", ".join(self.pools)
        await self.cog.process_roll(interaction, full_input, ephemeral=False)
        
        # 3. Cleanup builder
        await interaction.edit_original_response(content="✅ **Roll Sent!**", view=None)
        self.stop()

    async def update_builder_message(self, interaction: discord.Interaction):
        pool_display = "\n".join([f"🔹 `{p}`" for p in self.pools]) or "*Empty Session*"
        content = f"🏗️ **Dice Builder Session**\n\n**Staged Pools:**\n{pool_display}"
        await interaction.edit_original_response(content=content, view=self)

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Quick roll or build a session")
    async def roll(self, interaction: discord.Interaction, pool: str = "1d20", build: bool = False):
        if not build:
            # Fast Path: Defer first, then process
            await interaction.response.defer(ephemeral=False)
            await self.process_roll(interaction, pool, ephemeral=False)
        else:
            # Builder Path: Initial message is the response
            view = DiceBuilderView(interaction.user.id, [pool], self)
            await interaction.response.send_message(
                content=f"🏗️ **Dice Builder Session**\n\n**Staged Pools:**\n🔹 `{pool}`",
                view=view, ephemeral=True
            )

    async def process_roll(self, interaction: discord.Interaction, pool_str: str, ephemeral: bool = False):
        try:
            roll_data = DiceRoll(pool_str)
            if roll_data.error_message:
                return await interaction.followup.send(roll_data.error_message, ephemeral=True)

            embed = self.create_embed(interaction.user, roll_data)
            # Since we always defer before calling this, we ALWAYS use followup
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        except Exception as e:
            await interaction.followup.send(f"❌ **Error:** {str(e)}", ephemeral=True)

    def create_embed(self, user, roll_data):
        embed = discord.Embed(title="🎲 Nazh Engine Result", color=discord.Color.blue())
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        for i, pool in enumerate(roll_data.rolls):
            embed.add_field(name=f"Pool {i+1}: {pool['input']}", value=f"**{pool['total']}** ⟵ {pool['display']}", inline=False)
        if roll_data.plot_bonus > 0:
            embed.add_field(name="✨ Plot Influence", value=f"+{roll_data.plot_bonus} bonus applied!", inline=False)
        return embed

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
