import discord  # imports discord.py to build a bot
from discord.ext import commands
import os  # imports os module
from dotenv import load_dotenv  # imports modules to handle .env files

from modules import dice_roll
from modules import dice_view

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

@bot.command(name="build")
async def build_dice_pool(ctx):
    view = dice_view.MyView(ctx)
    if ctx.author == bot.user:
        return

    await ctx.send("Hello there!", view=view)

@bot.command(name="roll")
async def roll_dice(ctx, dice_notation: str):
    # roll dice in XdY notation
    try:
        numDice, numSides = map(int, dice_notation.lower().split('d'))
    except ValueError:
        await ctx.send("Invalid dice notation. Please use XdY format")

    if numDice <= 0 or numSides <= 0:
        await ctx.send("Number of dice and sides must be above 0.")
        return

    rolls = dice_roll.roll(numDice, numSides)
    total = sum(rolls)

    await ctx.send(f"Rolling {numDice}d{numSides}: {', '.join(map(str, rolls))} (Total: {total})")

# Executes bot with token
bot.run(DISCORD_TOKEN)
