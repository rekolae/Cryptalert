"""
Crypto related bot functionality

Emil Rekola <emil.rekola@hotmail.com>
"""

# STD imports
import json
from datetime import datetime
from asyncio import sleep
from typing import Tuple

# 3rd-party imports
import discord
from discord.ext import commands, tasks

# Local imports
from cryptalert.discord_bot.cogs.bot_mixin import BotMixin


def compare_vals(new: float, old: float, threshold: float) -> Tuple[bool, str]:
    """
    Calculate percentage change from given values

    :param new: The newer value used for comparison
    :param old: The older value used for comparison
    :param threshold: Threshold percentage value for when to report the change

    :return: Tuple containing bool and the change percent
    """

    negative_threshold = threshold * -1

    # Calculate change percent
    change = ((new - old) / old) * 100

    if change >= threshold:
        result = (True, f"Value raised by {round(change, 3)}%")

    elif change <= negative_threshold:
        result = (True, f"Value dropped by {round(change, 3)}%")

    else:
        result = (False, round(change, 3))

    return result


class Crypto(BotMixin, commands.Cog):
    """
    Bot crypto related actions
    """
    
    def __init__(self, bot):
        super().__init__(bot)

        # Used for checking if market is going up or down
        self.prev_total_change = None

        # Start tasks on init
        self.periodic_update.start()
        self.compare_short_interval.start()

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

    @tasks.loop(minutes=10.0)
    async def periodic_update(self):
        """
        Run task every 10min during daytime (7-23) that gives updates on the crypto currencies
        """

        # Get current time
        now = datetime.now()

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
        Wait until bot is ready to start the periodic update task
        """

        self.bot.logger.info("Waiting for bot to be ready before starting periodic_update task")
        await self.bot.wait_until_ready()
        self.bot.logger.info("Bot ready -> starting periodic_update task")

    @tasks.loop(seconds=15.0)
    async def compare_short_interval(self):
        """
        Check coin values every 15 seconds and send notifications if thresholds were passed
        """

        # Get current time
        now = datetime.now()

        # If time is between 23-07 -> mute rate comparison
        if 7 <= now.hour < 23:

            historical_data = self.bot.api_accessor.coin_histories

            embed_msg = discord.Embed(
                title="Short term update!",
                color=discord.Color.gold()
            )

            send_msg = False

            for coin, coin_data in historical_data.items():
                if len(coin_data) != 4:
                    self.bot.logger.info("Historical data not ready")

                else:
                    comp_short = compare_vals(coin_data[3], coin_data[2], self.bot.short_threshold)
                    comp_long = compare_vals(coin_data[3], coin_data[0], self.bot.long_threshold)

                    if comp_short[0] and comp_long[0]:

                        # 15s change threshold was passed
                        embed_msg.add_field(
                            name=coin,
                            value=f"{comp_short[1]} in the past 15 sec!",
                            inline=False
                        )

                        # 1min change threshold was passed
                        embed_msg.add_field(
                            name=coin,
                            value=f"{comp_long[1]} in the past minute!",
                            inline=False
                        )

                        send_msg = True

                    elif comp_short[0]:

                        # 15s change threshold was passed
                        embed_msg.add_field(
                            name=coin,
                            value=f"{comp_short[1]} in the past 15 sec!",
                            inline=False
                        )

                        send_msg = True

                    elif comp_long[0]:

                        # 1min change threshold was passed
                        embed_msg.add_field(
                            name=coin,
                            value=f"{comp_long[1]} in the past minute!",
                            inline=False
                        )

                        send_msg = True

            if send_msg:
                await self.bot.notify_channel.send(embed=embed_msg)

        # Sleep longer when it is hush hush times
        else:

            # Sleep for 1 hour
            await sleep(3600)

    @compare_short_interval.before_loop
    async def before_short_interval_compare(self):
        """
        Wait until bot is ready to start the value comparing task
        """

        self.bot.logger.info("Waiting for bot to be ready before starting compare_short_interval task")
        await self.bot.wait_until_ready()
        self.bot.logger.info("Bot ready -> starting compare_short_interval task")

    def get_market_status(self) -> str:
        """
        Check if market is going up or down and create a status message based on it

        :return: Market status as string
        """

        status = self.bot.api_accessor.api_data["market"]
        change = round(status['changePercent'], 3)

        msg_start = "Current market is"
        msg_end = "Current change is"

        # Market in total is positive
        if status["sign"]:
            same_or_no_prev_data = f"{msg_start} positive!\n{msg_end} {change}%!"

            # No previous rates recorded
            if self.prev_total_change is None:
                msg = same_or_no_prev_data

            # Rates are going down
            elif change < self.prev_total_change:
                msg = f"{msg_start} positive, but dropping!\n{msg_end} {change}%!"

            # Rates are going up
            elif change > self.prev_total_change:
                msg = f"{msg_start} positive and rising!\n{msg_end} {change}%!"

            # Rates are the same as previously so practically no change
            else:
                msg = same_or_no_prev_data

        # Market is negative
        else:
            same_or_no_prev_data = f"{msg_start} negative!\n{msg_end} {change}%!"

            # No previous rates recorded
            if self.prev_total_change is None:
                msg = same_or_no_prev_data

            # Rates are going down
            elif change < self.prev_total_change:
                msg = f"{msg_start} negative and dropping!\n{msg_end} {change}%!"

            # Rates are going up
            elif change > self.prev_total_change:
                msg = f"{msg_start} negative, but rising!\n{msg_end} {change}%!"

            # Rates are the same as previously so practically no change
            else:
                msg = same_or_no_prev_data

        self.prev_total_change = change

        return msg

    def get_update_embed(self, title="Status update!") -> discord.Embed:
        """
        Create a Discord Embed message and return it with added content

        :param title: Title of the Embed message, default: 'Status update!'
        :return: Discord Embed message
        """

        embed_msg = discord.Embed(
            title=title,
            description=self.get_market_status(),
            color=discord.Color.magenta()
        )

        currencies = [curr for curr in self.bot.api_accessor.api_data if curr != "market"]

        # Add buy, sell and change percent fields to the Embed message
        for currency in currencies:
            data = self.bot.api_accessor.api_data[currency]
            vals = f"Buy: {data['buy']}  Sell: {data['sell']}  %: {data['changePercent']}"
            embed_msg.add_field(
                name=currency,
                value=vals,
                inline=False
            )

        return embed_msg


def setup(bot):
    """
    Entry point for the 'commands.Bot.load_extension' function for loading extensions
    """

    bot.add_cog(Crypto(bot))
