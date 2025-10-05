import discord


class MyView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        # You can add persistent views here if needed for restarts

        # self.add_item(discord.ui.Button(label="Build a Dice Pool!", row=0))
        #self.add_item(self.init_button)

    @discord.ui.button(label="Build a Dice Pool!", 
                           style=discord.ButtonStyle.primary, 
                           custom_id="init_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)