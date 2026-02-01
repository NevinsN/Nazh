import discord
from typing import List
from modules.dice_roll import DiceRoll

class BuilderView(discord.ui.View):
    def __init__(self, user_id: int, initial_pools: List[str]):
        super().__init__(timeout=300)
        self.user_id, self.pool_list = user_id, initial_pools
        self.num_dice, self.num_sides, self.modifiers, self.tags = "1", "20", "0", ""

    async def update_view(self, interaction: discord.Interaction):
        staged = ", ".join(self.pool_list) if self.pool_list else "[ Empty ]"
        content = f"🏗️ **Dice Builder**\n**Staged:** `{staged}`\n**Current:** `{self._gen_str()}`"
        await interaction.response.edit_message(content=content, view=self)

    def _gen_str(self):
        m = int(self.modifiers)
        return f"{self.tags}{self.num_dice}d{self.num_sides}{f'{m:+}' if m != 0 else ''}"

    @discord.ui.select(placeholder="Choose Die", options=[discord.SelectOption(label=f"d{s}", value=str(s)) for s in [4,6,8,10,12,20,100]])
    async def select_sides(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.num_sides = select.values[0]
        await self.update_view(interaction)

    @discord.ui.button(label="Dice +1", style=discord.ButtonStyle.secondary, row=1)
    async def add_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num_dice = str(int(self.num_dice) + 1)
        await self.update_view(interaction)

    @discord.ui.button(label="Adv (a)", style=discord.ButtonStyle.success, row=1)
    async def add_adv(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tags = "a"
        await self.update_view(interaction)

    @discord.ui.button(label="Dis (d)", style=discord.ButtonStyle.danger, row=1)
    async def add_dis(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tags = "d"
        await self.update_view(interaction)

    @discord.ui.button(label="Plot Die", style=discord.ButtonStyle.success, emoji="🎭", row=2)
    async def add_plot(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pool_list.append("p1d6")
        await self.update_view(interaction)

    @discord.ui.button(label="Add to Pool", style=discord.ButtonStyle.success, emoji="➕", row=2)
    async def add_to_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pool_list.append(self._gen_str())
        self.tags = ""
        await self.update_view(interaction)

    @discord.ui.button(label="Roll Publicly", style=discord.ButtonStyle.primary, emoji="🎲", row=3)
    async def roll_pool(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() 
        dice_str = ", ".join(self.pool_list) if self.pool_list else self._gen_str()
        roll_data = DiceRoll(dice_str)
        cog = interaction.client.get_cog("DiceCog")
        if cog:
            from modules.dice_cog import CopyButtonView
            await interaction.followup.send(embed=cog.create_embed(interaction.user, roll_data), view=CopyButtonView(dice_str))
            await interaction.edit_original_response(content="✅ **Roll Dispatched!**", view=None)
