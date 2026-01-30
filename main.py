import discord  
from discord.ext import commands 
import os  
import asyncio
from dotenv import load_dotenv  
from discord.errors import LoginFailure, HTTPException

# Modular Imports
from modules import dice_roll
from modules import dice_views
from web_server import keep_alive

# 1. SECURITY & CONFIGURATION
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Fail-Fast: SREs ensure the environment is valid before the loop starts
if not DISCORD_TOKEN:
    print("ERROR: DISCORD_TOKEN missing from environment. Deployment halted.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True # Requirement: Enable 'Message Content' in Discord Portal
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. EVENT LISTENERS
@bot.event
async def on_ready():
    """Logs presence with high signal-to-noise ratio."""
    print(f"STATUS: Nahz connected to {len(bot.guilds)} guilds.")
    
    # Traceability: identifies exact code version in production
    commit = os.getenv('RENDER_GIT_COMMIT', 'Local Build')
    print(f"TRACE: Running version {commit}")

# 3. COMMANDS (Your Core Logic)
@bot.command(name="build")
async def build_dice_pool(ctx):
    if ctx.author == bot.user: return
    view = dice_views.MainView(ctx)
    await ctx.send("Let's get started.", view=view)

@bot.command(name="roll")
async def roll_dice(ctx, *, dice_command: str):
    dice_pool = dice_roll.DiceRoll(dice_command)
    if dice_pool.getErrorMessage() != "none":
        await ctx.send(f"{dice_pool.getErrorMessage()}, {ctx.author.mention}")
        return
    await dice_pool.getAndSendResultMessage(ctx)

# 4. RELIABILITY LAYER (The Exponential Backoff Fix)
async def start_bot():
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            # We use bot.start() for custom event loop management
            await bot.start(DISCORD_TOKEN)
        except HTTPException as e:
            if e.status == 429: # Rate Limited
                wait_time = (2 ** retries) * 60 # SRE Strategy: Wait 1m, 2m, 4m...
                print(f"RETRY: Rate limit hit. Waiting {wait_time}s before next Identify attempt.")
                await asyncio.sleep(wait_time)
                retries += 1
            else:
                print(f"HTTP ERROR: {e.status} - {e.text}")
                raise e
        except LoginFailure:
            print("CRITICAL: Authentication failed. Please verify your token in Render settings.")
            break 

# 5. ENTRY POINT
if __name__ == '__main__':
    # Initialize web sidecar with bot reference for the /guilds dashboard
    keep_alive(bot) 
    
    print("BOOTING: Starting bot event loop...")
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("SHUTDOWN: Process ended by user.")
