"""
Bot utility functionality

Emil Rekola <emil.rekola@hotmail.com>
"""

# STD imports
import datetime

# 3rd-party imports
from discord.ext import commands

# Local imports
from cryptalert import VERSION
from cryptalert.discord_bot.cogs.bot_mixin import BotMixin


class Utilities(BotMixin, commands.Cog):
    """
    Bot actions
    """

    @commands.command()
    async def ping(self, ctx):
        """
        Ping Pong!!!
        """

        await ctx.send("Pong!")

    @commands.command()
    async def version(self, ctx):
        """
        Display bot version
        """

        await ctx.send(f"Bot version: {VERSION}")

    @commands.command()
    async def uptime(self, ctx):
        """
        Display bot uptime
        """

        # Time difference between starting and now
        time_delta = datetime.datetime.now() - self.bot.startup_time

        # Calculate hours, minutes and seconds
        hours = int(time_delta.seconds / 3600)
        mins = int((time_delta.seconds / 60) % 60)
        secs = int(time_delta.seconds % 60)

        uptime = f"Bot uptime: {time_delta.days} days {hours} hours {mins} minutes {secs} seconds"
        await ctx.send(uptime)


def setup(bot):
    """
    Entry point for the 'commands.Bot.load_extension' function for loading extensions
    """

    bot.add_cog(Utilities(bot))
