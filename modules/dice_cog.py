import discord
from discord import app_commands
from discord.ext import commands
from modules.dice_roll import DiceRoll

class AddPoolModal(discord.ui.Modal, title="Configure Dice Pool"):
    # Individual fields for high-precision entry on mobile
    num_dice = discord.ui.TextInput(
        label="Number of Dice",
        placeholder="e.g., 1",
        default="1",
        min_length=1,
        max_length=2
    )
    sides = discord.ui.TextInput(
        label="Dice Sides (d20, d6, etc.)",
        placeholder="20",
        default="20",
        min_length=1,
        max_length=3
    )
    modifier = discord.ui.TextInput(
        label="Modifier (+/-)",
        placeholder="0",
        default="0",
        required=False
    )
    tags = discord.ui.TextInput(
        label="Tags (a = Adv, d = Disadv)",
        placeholder="Leave blank for normal",
        required=False,
        max_length=1
    )

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        # Assemble the dice string from the modal inputs
        tag = self.tags.value.lower() if self.tags.value else ""
        try:
            val = int(self.modifier.value) if self.modifier.value else 0
            mod_str = f"{val:+}" if val != 0 else ""
        except ValueError:
            mod_str = ""

        pool_string = f"{tag}{self.num_dice.value}d{self.sides.value}{mod_str}"
        self.parent_view.pools.append(pool_string)
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
        self.pools.append("p1d6")
        button.disabled = True
        button.label = "Plot Die Added"
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Remove Last", style=discord.ButtonStyle.danger, emoji="🔙")
    async def undo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.pools:
            return await interaction.response.send_message("Nothing to remove!", ephemeral=True)
        
        removed = self.pools.pop()
        
        # Re-enable Plot Die button if we just removed it
        if removed == "p1d6":
            for child in self.children:
                if isinstance(child, discord.ui.Button) and "Plot" in str(child.label):
                    child.disabled = False
                    child.label = "Add Plot Die"
        
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Roll Publicly", style=discord.ButtonStyle.primary, emoji="🎲")
    async def roll_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This isn't your session!", ephemeral=True)
            
        full_input = ", ".join(self.pools)
        await self.cog.process_roll(interaction, full_input, ephemeral=False)
        
        # Clean up the ephemeral builder
        await interaction.edit_original_response(content="✅ **Roll Dispatched to Channel.**", view=None)
        self.stop()

    async def update_builder_message(self, interaction: discord.Interaction):
        pool_display = "\n".join([f"🔹 `{p}`" for p in self.pools]) or "*Empty Session*"
        content = f"🏗️ **Dice Builder Session**\n\n**Staged Pools:**\n{pool_display}\n\n*Finalize to post publicly!*"
        await interaction.response.edit_message(content=content, view=self)

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Quick roll or build a multi-pool session")
    @app_commands.describe(
        pool="Dice string (e.g. '1d20+5')",
        build="Set to True to build your roll pool-by-pool"
    )
    async def roll(self, interaction: discord.Interaction, pool: str = "1d20", build: bool = False):
        if not build:
            await self.process_roll(interaction, pool, ephemeral=False)
        else:
            view = DiceBuilderView(interaction.user.id, [pool], self)
            await interaction.response.send_message(
                content=f"🏗️ **Dice Builder Session**\n\n**Staged Pools:**\n🔹 `{pool}`",
                view=view,
                ephemeral=True
            )

    async def process_roll(self, interaction: discord.Interaction, pool_str: str, ephemeral: bool = False):
        try:
            roll_data = DiceRoll(pool_str)
            
            if roll_data.error_message:
                # Use followup if the interaction was already responded to (common in Builders)
                if interaction.response.is_done():
                    return await interaction.followup.send(roll_data.error_message, ephemeral=True)
                return await interaction.response.send_message(roll_data.error_message, ephemeral=True)

            embed = self.create_embed(interaction.user, roll_data)
            
            # THE FIX: If we are coming from a button click in a View, 
            # we MUST use followup.send() because the interaction was 'consumed' 
            # by the button click or modal submit.
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
                
        except discord.errors.NotFound:
            # This handles the case where the interaction expired (3-second limit)
            print("Interaction expired. This usually happens if the engine takes too long or Discord is laggy.")
        except Exception as e:
            msg = f"❌ **System Error:** {str(e)}"
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)


    def create_embed(self, user, roll_data):
        embed = discord.Embed(
            title="🎲 Nazh Engine Result",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

        for i, pool in enumerate(roll_data.rolls):
            name = f"Pool {i+1}: {pool['input']}"
            # Bold the total for readability
            value = f"**{pool['total']}** ⟵ {pool['display']}"
            embed.add_field(name=name, value=value, inline=False)

        if roll_data.plot_bonus > 0:
            embed.add_field(
                name="✨ Plot Influence", 
                value=f"The Plot Die added a **+{roll_data.plot_bonus}** bonus to all d20s!", 
                inline=False
            )
        
        return embed

async def setup(bot):
    await bot.add_cog(DiceCog(bot))
