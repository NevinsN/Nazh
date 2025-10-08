import discord  # imports discord.py to build a bot
from discord.ext import commands # imports commands to handle command functions
import os  # imports os module
from dotenv import load_dotenv  # imports modules to handle .env files

# Imports from other classes
from modules import dice_roll
from modules import dice_views
from web_server import keep_alive

# loads .env file
load_dotenv()

# gets token from .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# load default intents and set needed intents
intents = discord.Intents.default()
intents.message_content = True  # access message content

# retrieves the client object from discord.py, and creates the bot
bot = commands.Bot(command_prefix="!", intents=intents)


# event listener to detect when bot switches from offline to online
@bot.event
async def on_ready():
    # counter to track number of guilds using bot
    guild_count = 0

    # loop to find all guilds bot is on and increment guild_Count for each
    for guild in bot.guilds:
        # print server name and id
        print(f"- {guild.id} (name: {guild.name})")

        # increment guild_count
        guild_count += 1

    # prints number of guilds bot is installed on
    print("Nahz is assisting " + str(guild_count) + " guilds.")

# Function to handle the build command, which allows to build a 
# dice pool utilizing a more visual UI
@bot.command(name="build")
async def build_dice_pool(ctx):
    view = dice_views.MainView(ctx)
    if ctx.author == bot.user:
        return

    await ctx.send("Let's get started.", view=view)


# Function to handle the roll command, the primary function of the bot
@bot.command(name="roll")
async def roll_dice(ctx, *, dice_command: str):
    # creates an instance of the DiceRoll class
    # Uses ctx, the prompting message, and dice_command as a string
    dice_pool = dice_roll.DiceRoll(dice_command)

    # Checks if there is an error present
    if dice_pool.getErrorMessage() != "none":
        await ctx.send(f"{dice_pool.getErrorMessage()}, {ctx.author.mention}")
        return

    # Performs the roll operation
    await dice_pool.getAndSendResultMessage(ctx)

# Quick function to help the bot stay alive on free hosting services 
if __name__ == '__main__':
    keep_alive() # start web server

    # Executes bot with token
    bot.run(DISCORD_TOKEN)
