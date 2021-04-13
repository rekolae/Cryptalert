"""
Discord bot for sending messages about current happenings in cryptocurrency movements

Emil Rekola <emil.rekola@hotmail.com>
"""

# STD imports
import logging
import json
import datetime
from typing import Dict
from asyncio import sleep

# 3rd-party imports
import discord

# Local imports
from cryptalert.data_fetcher.api_accessor import ApiAccessor


class DiscordBot(discord.Client):
    """
    Class with functionality and actions of the discord bot
    """

    def __init__(self, channel_id, api_accessor: ApiAccessor):
        super().__init__()
        self._main_channel_id: int = channel_id
        self.bot_name: str = self.user
        self.api_accessor: ApiAccessor = api_accessor
        self.rates: Dict = {}
        self._logger = logging.getLogger("discord.bot")

    async def on_ready(self):
        """
        Executed when the bot has been initialized and connection has been made to discord
        """

        # Remove the "#xxxx" appendix from the bot username
        self.bot_name = str(self.user).split("#")[0]
        self._logger.info("%s is online!", self.bot_name)

        # If info channel was defined
        if self._main_channel_id is not None:
            self._logger.debug("Sending bot login message")
            await self.send_message(self.get_channel(self._main_channel_id), f"{self.bot_name} is online!")

        # Add task that runs in the background every 10min
        self.loop.create_task(self.periodic_update())

    async def on_message(self, message):
        """
        When message is sent to any of the channels, check the message and respond appropriately

        :param message: Message that was recieved from the discord server
        """

        # Ignore bot's own messages
        if message.author != self.user:
            self._logger.info("Message from %s at %s: %s", message.author, message.channel, message.content)

            # Play some Ping Pong with another user
            if message.content.lower() == "ping":
                await self.send_message(message.channel, "Pong")

            elif message.content.lower() == "!rates":
                await self.send_message(message.channel, f"Current rates:\n{self.get_data()}")

            elif message.content.lower() == "!market":
                await self.send_message(message.channel, self.get_market())

    async def send_message(self, channel, message):
        """
        Send given message to the given channel

        :param channel: Target channel for the message
        :param message: Message to be sent to the channel
        """

        self._logger.debug("Sending message to '%s'", channel)
        await channel.send(message)

    def get_data(self) -> str:
        """
        Fetch latest data from data fetcher and format it for sending

        :return: Formatted string with market data
        """

        return json.dumps(self.api_accessor.api_data, indent=4, ensure_ascii=False)

    def get_market(self) -> str:
        """
        Get current market trend and format it for sending

        :return: String with current market status
        """

        status = self.api_accessor.api_data["market"]

        if status["sign"]:
            msg = f"Current market is rising!\nCurrent change is +{status['changePercent']}%!"

        else:
            msg = f"Current market is dropping!\nCurrent change is -{status['changePercent']}%!"

        return msg

    async def periodic_update(self):
        """
        Run task every 10min during daytime (7-23) that gives updates on the crypto currencies
        """

        while True:

            # Get current time
            now = datetime.datetime.now()

            # If time is between 23-07 -> mute periodic updates
            if 7 <= now.hour <= 23:
                embed_msg = discord.Embed(
                    title="Status update!",
                    description=self.get_market(),
                    color=discord.Color.magenta()
                )

                for currency in self.api_accessor.api_data:
                    if currency != "market":
                        for op in ("buy", "sell", "changePercent"):
                            embed_msg.add_field(
                                name=f"{currency} {op}",
                                value=self.api_accessor.api_data[currency][op],
                                inline=True
                            )

                await self.get_channel(self._main_channel_id).send(embed=embed_msg)

                # Sleep for 10min
                await sleep(600)

            # Sleep longer when it is quiet times
            else:

                # Sleep for 1 hour
                await sleep(3600)
