import discord
from typing import List
from modules.dice_roll import DiceRoll

class BuilderView(discord.ui.View):
    """Stateful view for assembling multi-dice strings."""
    def __init__(self, user_id: int, initial_pools: List[str]):
        super().__init__(timeout=300)
        self.user_id = user_id
        # Use provided pools or start empty
        self.pool_list: List[str] = initial_pools if initial_pools else []
        self.num_dice: str = "1"
        self.num_sides: str = "20"
        self.modifiers: str = "0"

    def _generate_current_string(self) -> str:
        """Helper to format the 'in-progress' dice string."""
        try:
            mod_val = int(self.modifiers)
            sign = "+" if mod_val >= 0 else ""
            return f"{self.num_dice}d{self.num_sides}{sign}{mod_val}"
        except ValueError:
            return f"{self.num_dice}d{self.num_sides}+0"

    def _get_content(self) -> str:
        """Helper to generate the message text based on the current state."""
        staged = ", ".join(self.pool_list) if self.pool_list else "[ Empty ]"
        current = self._generate_current_string()
        return f"🏗️ **Dice Builder**\n**Staged:** `{staged}`\n**Current:** `{current}`"

    @discord.ui.select(
        placeholder="Select Die Type",
        options=[
            discord.SelectOption(label="d4", value="4"),
            discord.SelectOption(label="d6", value="6"),
            discord.SelectOption(label="d10", value="10"),
            discord.SelectOption(label="d20", value="20", default=True),
            discord.SelectOption(label="d100", value="100"),
        ]
    )
    async def select_sides(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This isn't your session!", ephemeral=True)
        self.num_sides = select.values[0]
        await interaction.response.edit_message(content=self._get_content(), view=self)

    @discord.ui.button(label="Add to Pool", style=discord.ButtonStyle.secondary, emoji="➕")
    async def add_to_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pool_list.append(self._generate_current_string())
        await interaction.response.edit_message(content=self._get_content(), view=self)

    @discord.ui.button(label="Remove Last", style=discord.ButtonStyle.danger, emoji="🔙")
    async def remove_last(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Removes the last added pool from the list."""
        if self.pool_list:
            self.pool_list.pop()
            await interaction.response.edit_message(content=self._get_content(), view=self)
        else:
            await interaction.response.send_message("Pool is already empty!", ephemeral=True)

    @discord.ui.button(label="Roll Pool!", style=discord.ButtonStyle.primary, emoji="🎲")
    async def roll_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only allow rolling if there's something to roll
        if not self.pool_list:
            self.pool_list.append(self._generate_current_string())
        
        await interaction.response.defer()
        dice_str = ", ".join(self.pool_list)
        roll_data = DiceRoll(dice_str)
        
        cog = interaction.client.get_cog("DiceCog")
        if cog:
            embed = cog.create_embed(interaction.user, roll_data)
            await interaction.followup.send(embed=embed)
            await interaction.edit_original_response(content="✅ **Roll Sent!**", view=None)
        self.stop()
