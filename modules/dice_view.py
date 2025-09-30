import discord


class MyView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        # You can add persistent views here if needed for restarts

        self.add_item(discord.ui.Button(label="d4", row=0))
        self.add_item(discord.ui.Button(label="d6", row=0))
        self.add_item(discord.ui.Button(label="d8", row=0))

        @discord.ui.button(label="Click Me!", 
                           style=discord.ButtonStyle.primary, 
                           custom_id="my_button")
        async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message("You clicked the button!", ephemeral=True)