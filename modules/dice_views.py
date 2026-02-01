import discord
from typing import List
from modules.dice_roll import DiceRoll

class BuilderView(discord.ui.View):
    def __init__(self, user_id: int, initial_pools: List[str]):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.pool_list = initial_pools
        self.num_dice, self.num_sides, self.modifiers, self.tags = "1", "20", "0", ""

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your session!", ephemeral=True)
            return False
        return True

    def _generate_current_string(self) -> str:
        try:
            m = int(self.modifiers)
            mod_str = f"{m:+}" if m != 0 else ""
        except: mod_str = ""
        return f"{self.tags}{self.num_dice}d{self.num_sides}{mod_str}"

    async def update_view(self, interaction: discord.Interaction):
        staged = ", ".join(self.pool_list) if self.pool_list else "[ Empty ]"
        content = f"🏗️ **Dice Builder**\n**Staged:** `{staged}`\n**Current:** `{self._generate_current_string()}`"
        # Immediate edit prevents "Interaction Failed"
        await interaction.response.edit_message(content=content, view=self)

    @discord.ui.select(
        placeholder="Choose Die",
        options=[discord.SelectOption(label=f"d{s}", value=str(s)) for s in [2,4,6,8,10,12,20,100]]
    )
    async def select_sides(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.num_sides = select.values[0]
        await self.update_view(interaction)

    @discord.ui.button(label="Dice +1", style=discord.ButtonStyle.secondary, row=1)
    async def add_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num_dice = str(int(self.num_dice) + 1)
        await self.update_view(interaction)

    @discord.ui.button(label="Add to Pool", style=discord.ButtonStyle.success, emoji="➕", row=2)
    async def add_to_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pool_list.append(self._generate_current_string())
        self.tags = "" # Reset tags
        await self.update_view(interaction)

    @discord.ui.button(label="Roll Publicly", style=discord.ButtonStyle.primary, emoji="🎲", row=3)
    async def roll_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() # Acknowledge immediately
        dice_str = ", ".join(self.pool_list) if self.pool_list else self._generate_current_string()
        roll_data = DiceRoll(dice_str)
        cog = interaction.client.get_cog("DiceCog")
        if cog:
            embed = cog.create_embed(interaction.user, roll_data)
            # Use followup because we deferred
            from modules.dice_cog import CopyButtonView
            await interaction.followup.send(embed=embed, view=CopyButtonView(dice_str))
            await interaction.edit_original_response(content="✅ **Roll Sent!**", view=None)

    # ... (Include other buttons like Plot Die, Undo, etc., using await self.update_view(interaction))
