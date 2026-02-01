import discord
from discord.ext import commands
from modules import dice_roll, dice_views

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="build")
    async def build_dice_pool(self, ctx):
        """Refactored version of your original !build command."""
        if ctx.author == self.bot.user: 
            return
            
        view = dice_views.MainView(ctx)
        await ctx.send("Press the button to build your pool!", view=view)

    @commands.command(name="roll")
    async def roll_dice(self, ctx, *, dice_command: str):
        """Refactored version of your original !roll command."""
        dice_pool = dice_roll.DiceRoll(dice_command)
        
        if dice_pool.getErrorMessage() != "none":
            await ctx.send(f"⚠️ {dice_pool.getErrorMessage()}, {ctx.author.mention}")
            return
            
        await dice_pool.getAndSendResultMessage(ctx)

# This function is required for the bot to "see" the Cog
async def setup(bot):
    await bot.add_cog(DiceCog(bot))
