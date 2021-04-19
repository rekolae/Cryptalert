"""
Crypto related bot functionality

Emil Rekola <emil.rekola@hotmail.com>
"""

# STD imports
import json
import datetime
from asyncio import sleep

# 3rd-party imports
import discord
from discord.ext import commands, tasks

# Local imports
from cryptalert.discord_bot.cogs.bot_mixin import BotMixin


class Crypto(BotMixin, commands.Cog):
    """
    Bot actions
    """

    prev_total_change: float = None

    @commands.command()
    async def rates(self, ctx):
        """
        Get current rates for configured crypto currencies
        """

        await ctx.send(f"Current rates:\n{json.dumps(self.bot.api_accessor.api_data, indent=4, ensure_ascii=False)}")

    @commands.command(aliases=["marketStatus", "status"])
    async def market(self, ctx):
        """
        Get current market status
        """

        await ctx.send(self.get_market_status())

    @commands.command(aliases=["statusUpdate"])
    async def update(self, ctx):
        """
        Get brief update on crypto market and rates
        """

        await ctx.send(embed=self.get_update_embed("Current market status!"))

    @tasks.loop(minutes=10)
    async def periodic_update(self):
        """
        Run task every 10min during daytime (7-23) that gives updates on the crypto currencies
        """

        # Get current time
        now = datetime.datetime.now()

        # If time is between 23-07 -> mute periodic updates
        if 7 <= now.hour < 23:
            await self.bot.main_channel.send(embed=self.get_update_embed())

        # Sleep longer when it is hush hush times
        else:

            # Sleep for 1 hour
            await sleep(3600)

    @periodic_update.before_loop
    async def before_periodic_update(self):
        """
        Wait until bot is ready to start the looping task
        """

        await self.bot.wait_until_ready()

    def get_market_status(self) -> str:
        status = self.bot.api_accessor.api_data["market"]
        change = round(status['changePercent'], 3)

        msg_start = "Current market is"
        msg_end = "Current change is"

        if status["sign"]:
            same_or_no_prev_data = f"{msg_start} positive!\n{msg_end} {change}%!"

            if self.prev_total_change is None:
                msg = same_or_no_prev_data

            elif change < self.prev_total_change:
                msg = f"{msg_start} positive, but dropping!\n{msg_end} {change}%!"

            elif change > self.prev_total_change:
                msg = f"{msg_start} positive and rising!\n{msg_end} {change}%!"

            else:
                msg = same_or_no_prev_data

        else:
            same_or_no_prev_data = f"{msg_start} negative!\n{msg_end} {change}%!"

            if self.prev_total_change is None:
                msg = same_or_no_prev_data

            elif change < self.prev_total_change:
                msg = f"{msg_start} negative and dropping!\n{msg_end} {change}%!"

            elif change > self.prev_total_change:
                msg = f"{msg_start} negative, but rising!\n{msg_end} {change}%!"

            else:
                msg = same_or_no_prev_data

        self.prev_total_change = change

        return msg

    def get_update_embed(self, title="Status update!") -> discord.Embed:
        embed_msg = discord.Embed(
            title=title,
            description=self.get_market_status(),
            color=discord.Color.magenta()
        )

        for currency in self.bot.api_accessor.api_data:
            if currency != "market":
                for op in ("buy", "sell", "changePercent"):
                    embed_msg.add_field(
                        name=f"{currency} {op}",
                        value=self.bot.api_accessor.api_data[currency][op],
                        inline=True
                    )

        return embed_msg


def setup(bot):
    """
    Entry point for the 'commands.Bot.load_extension' function for loading extensions
    """

    bot.add_cog(Crypto(bot))
