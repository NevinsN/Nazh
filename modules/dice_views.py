import discord
from typing import List
from modules.dice_roll import DiceRoll

class CustomInputModal(discord.ui.Modal, title="Custom Dice Settings"):
    """Pop-up to handle specific custom numbers and tags."""
    num = discord.ui.TextInput(label="Number of Dice", default="1", min_length=1, max_length=2)
    sides = discord.ui.TextInput(label="Sides (e.g. 12, 8, 100)", default="20", max_length=3)
    mod = discord.ui.TextInput(label="Modifier (+/-)", default="0", required=False)
    tags = discord.ui.TextInput(label="Tags (a/d)", placeholder="e.g. aa for 2 Advantage", required=False)

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.num_dice = self.num.value
        self.parent_view.num_sides = self.sides.value
        self.parent_view.modifiers = self.mod.value
        self.parent_view.tags = self.tags.value.lower()
        await self.parent_view.update_builder_message(interaction)

class BuilderView(discord.ui.View):
    """Advanced stateful view for assembling complex dice pools."""
    def __init__(self, user_id: int, initial_pools: List[str]):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.pool_list: List[str] = initial_pools if initial_pools else []
        self.num_dice: str = "1"
        self.num_sides: str = "20"
        self.modifiers: str = "0"
        self.tags: str = ""

    def _generate_current_string(self) -> str:
        """Assembles the current selections into a Nazh-compatible string."""
        try:
            m = int(self.modifiers)
            mod_str = f"{m:+}" if m != 0 else ""
        except ValueError:
            mod_str = ""
        
        # Format: [tags][count]d[sides][mod]
        return f"{self.tags}{self.num_dice}d{self.num_sides}{mod_str}"

    async def update_builder_message(self, interaction: discord.Interaction):
        """Refreshes the UI content."""
        staged = ", ".join(self.pool_list) if self.pool_list else "[ Empty ]"
        current = self._generate_current_string()
        content = f"🏗️ **Dice Builder**\n**Staged:** `{staged}`\n**Current:** `{current}`"
        await interaction.response.edit_message(content=content, view=self)

    @discord.ui.select(
        placeholder="Quick Die Selection",
        options=[
            discord.SelectOption(label="d4", value="4"),
            discord.SelectOption(label="d6", value="6"),
            discord.SelectOption(label="d10", value="10"),
            discord.SelectOption(label="d12", value="12"), # Added d12
            discord.SelectOption(label="d20", value="20", default=True),
            discord.SelectOption(label="d100", value="100"),
        ]
    )
    async def select_sides(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.num_sides = select.values[0]
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Dice +1", style=discord.ButtonStyle.secondary, row=1)
    async def add_one_dice(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num_dice = str(int(self.num_dice) + 1)
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Adv (a)", style=discord.ButtonStyle.secondary, row=1)
    async def add_adv(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Adds one 'a' tag, capped at the number of dice."""
        if len(self.tags) < int(self.num_dice):
            self.tags += "a"
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Dis (d)", style=discord.ButtonStyle.secondary, row=1)
    async def add_dis(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Adds one 'd' tag, capped at the number of dice."""
        if len(self.tags) < int(self.num_dice):
            self.tags += "d"
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Custom Settings", style=discord.ButtonStyle.secondary, emoji="⚙️", row=2)
    async def custom_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CustomInputModal(self))

    @discord.ui.button(label="Add to Pool", style=discord.ButtonStyle.success, emoji="➕", row=2)
    async def add_to_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pool_list.append(self._generate_current_string())
        self.tags = "" # Reset tags for next die
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Undo", style=discord.ButtonStyle.danger, emoji="🔙", row=3)
    async def remove_last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.pool_list:
            self.pool_list.pop()
        await self.update_builder_message(interaction)

    @discord.ui.button(label="Roll Publicly", style=discord.ButtonStyle.primary, emoji="🎲", row=3)
    async def roll_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.pool_list:
            self.pool_list.append(self._generate_current_string())
        
        await interaction.response.defer()
        dice_str = ", ".join(self.pool_list)
        roll_data = DiceRoll(dice_str)
        
        cog = interaction.client.get_cog("DiceCog")
        if cog:
            embed = cog.create_embed(interaction.user, roll_data)
            await interaction.followup.send(embed=embed)
            await interaction.edit_original_response(content="✅ **Roll Dispatched.**", view=None)
        self.stop()
