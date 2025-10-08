import discord # main discord import

from modules import dice_roll # imports dice rolls in order to roll dice internally


# Initial view to start an interaction for an ephemeral message
class MainView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()

    # Button to start dice pool building through BuilderView
    @discord.ui.button(label="Build a Dice Pool!", 
                           style=discord.ButtonStyle.primary, 
                           custom_id="init_button")
    # callback sends the ephemeral message then deletes this original one
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Current dice: ", view=BuilderView(), ephemeral=True)
        await interaction.message.delete()

# A class to handle the dice building ui
class BuilderView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.returnString = [] # holds individual dice strings for rolling
        self.workingString = '' # current string the bot is working on
        self.preCodes = '' # all preCodes
        self.numDice = '1' # number of dice
        self.numSides = '20' # number of sides
        self.modifiers = '0' # added modifier
        
    @discord.ui.select(placeholder = "Number of Dice", 
                       min_values=1, 
                       max_values=1,
                       custom_id="numDice",
                       default_values='1',
                       options = [
                                  discord.SelectOption(label = "1", value = "1"),
                                  discord.SelectOption(label = "2", value = "2"),
                                  discord.SelectOption(label = "3", value = "3"),
                                  discord.SelectOption(label = "4", value = "4"),
                                  discord.SelectOption(label = "5", value = "5"),
                                  discord.SelectOption(label = "6", value = "6"),
                                  discord.SelectOption(label = "7", value = "7"),
                                  discord.SelectOption(label = "8", value = "8"),
                                  discord.SelectOption(label = "9", value = "9"),
                                  discord.SelectOption(label = "10", value = "10")
                                  ])
    async def numDice_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.numDice = select.values[0]

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {','.join(self.returnString)}[ {self.workingString} ]")
    
    @discord.ui.select(placeholder="Number of Sides",
                       min_values=1,
                       max_values=1,
                       custom_id="numSides",
                       default_values='20',
                       options=[
                                discord.SelectOption(label="d2", value='2'),
                                discord.SelectOption(label="d4", value='4'),
                                discord.SelectOption(label="d6", value='6'),
                                discord.SelectOption(label="d8", value='8'),
                                discord.SelectOption(label="d10", value='10'),
                                discord.SelectOption(label="d12", value='12'),
                                discord.SelectOption(label="d20", value='20'),
                                discord.SelectOption(label="d100", value='100')
                               ])
    async def numSides_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.numSides = select.values[0]

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {','.join(self.returnString)}[ {self.workingString} ]")
    
    @discord.ui.select(placeholder="Modifier",
                       min_values=1,
                       max_values=1,
                       custom_id="modifiers",
                       default_values='0',
                       options=[
                                discord.SelectOption(label="1", value='1'),
                                discord.SelectOption(label="2", value='2'),
                                discord.SelectOption(label="3", value='3'),
                                discord.SelectOption(label="4", value='4'),
                                discord.SelectOption(label="5", value='5'),
                                discord.SelectOption(label="6", value='6'),
                                discord.SelectOption(label="7", value='7'),
                                discord.SelectOption(label="8", value='8'),
                                discord.SelectOption(label="9", value='9'),
                                discord.SelectOption(label="10", value='10')
                               ],
                               row = 2)
    async def modifiers_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.modifiers = select.values[0]

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {', '.join(self.returnString)}[ {self.workingString} ]")
    
    @discord.ui.button(custom_id="plus", row = 3, label = "+")
    async def plus_callback(self, interaction: discord.Interaction, button: discord.ui.button):        
        if int(self.modifiers) < 0:
            self.modifiers = str(int(self.modifiers) * -1)

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {', '.join(self.returnString)}[ {self.workingString} ]")

    @discord.ui.button(custom_id="minus", row = 3, label = "-")
    async def minus_callback(self, interaction: discord.Interaction, button: discord.ui.button):        
        if int(self.modifiers) >= 0:
            self.modifiers = str(int(self.modifiers) * -1)

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {', '.join(self.returnString)}[ {self.workingString} ]")

    @discord.ui.button(custom_id="advantage", row = 3, label = "a")
    async def advantage_callback(self, interaction: discord.Interaction, button: discord.ui.button):        
        if len(self.preCodes) == int(self.numDice):
            tempStr = self.preCodes.replace('d', 'a', 1)
            self.preCodes = tempStr
        elif len(self.preCodes) < int(self.numDice):
            self.preCodes += 'a'
        

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {', '.join(self.returnString)}[ {self.workingString} ]")

    @discord.ui.button(custom_id="disadvantage", row = 3, label = "d")
    async def disadvantage_callback(self, interaction: discord.Interaction, button: discord.ui.button):        
        if len(self.preCodes) == int(self.numDice):
            tempStr = self.preCodes.replace('a', 'd', 1)
            self.preCodes = tempStr
        elif len(self.preCodes) < int(self.numDice):
            self.preCodes += 'd'

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {', '.join(self.returnString)}[ {self.workingString} ]")

    @discord.ui.button(custom_id="resetPrecode", row = 3, label = "Reset Precodes")
    async def resetPrecode_callback(self, interaction: discord.Interaction, button: discord.ui.button):        
        self.preCodes = ''

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {', '.join(self.returnString)}[ {self.workingString} ]")

    @discord.ui.button(custom_id="cancel", row = 4, label = "Cancel")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.button):        
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"You cancelled the dice pool. Please dismiss this message", view=None)

    @discord.ui.button(custom_id="addDice", row = 4, label = "Add Dice")
    async def addDice_callback(self, interaction: discord.Interaction, button: discord.ui.button):        
        self.returnString.append(self.workingString)

        self.preCodes = ''
        self.numDice = '1'
        self.numSides = '20'
        self.modifiers = '0'

        self.workingString = f"{self.preCodes}{self.numDice}d{self.numSides}{'+' if int(self.modifiers) >= 0 else ''}{self.modifiers}"
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"Current Dice: {', '.join(self.returnString)}[ {self.workingString} ]")

    @discord.ui.button(custom_id="rollDice", row = 4, label = "Roll 'Em!")
    async def rollDice_callback(self, interaction: discord.Interaction, button: discord.ui.button):        
        if not self.returnString:
            self.returnString.append(self.workingString)

        roll = dice_roll.DiceRoll(', '.join(self.returnString))
        await roll.getAndSendResultMessage(interaction)
        