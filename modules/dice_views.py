import discord
from typing import List, Optional
from modules.dice_roll import DiceRoll
from modules.metrics import metrics

class MainView(discord.ui.View):
    """Initial landing view for the Dice Builder."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Builder", style=discord.ButtonStyle.success)
    async def open_builder(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Current Pool: [ Empty ]", 
            view=BuilderView(), 
            ephemeral=True
        )

class BuilderView(discord.ui.View):
    """Stateful view for assembling multi-dice strings."""
    def __init__(self):
        super().__init__(timeout=300)
        self.pool_list: List[str] = []
        self.num_dice: str = "1"
        self.num_sides: str = "20"
        self.modifiers: str = "0"

    def _generate_current_string(self) -> str:
        """Helper to format the 'in-progress' dice string."""
        sign = "+" if int(self.modifiers) >= 0 else ""
        return f"{self.num_dice}d{self.num_sides}{sign}{self.modifiers}"

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
        self.num_sides = select.values[0]
        await interaction.response.edit_message(content=f"Current Pool: {', '.join(self.pool_list)} [ {self._generate_current_string()} ]")

    @discord.ui.button(label="Add to Pool", style=discord.ButtonStyle.secondary)
    async def add_to_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pool_list.append(self._generate_current_string())
        await interaction.response.edit_message(content=f"Current Pool: {', '.join(self.pool_list)}")

    @discord.ui.button(label="Roll Pool!", style=discord.ButtonStyle.primary)
    async def roll_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.pool_list:
            self.pool_list.append(self._generate_current_string())
        
        metrics.increment("roll_success")
        engine = DiceRoll(", ".join(self.pool_list))
        await engine.send_result_message(interaction)
