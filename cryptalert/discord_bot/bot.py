"""
Discord bot for sending messages about current happenings in cryptocurrency movements

Emil Rekola <emil.rekola@hotmail.com>, 2021
"""

# STD imports
import logging

# 3rd-party imports
import discord


class DiscordBot(discord.Client):
    """
    Class with functionality and actions of the discord bot
    """

    def __init__(self, channel_id):
        super().__init__()
        self._main_channel_id = channel_id
        self.bot_name = self.user

    async def on_ready(self):
        """
        Executed when the bot has been initialized and connection has been made to discord
        """

        # Remove the "#xxxx" appendix from the bot username
        self.bot_name = str(self.user).split("#")[0]
        logging.info("%s is online!", self.bot_name)

        # If info channel was defined
        if self._main_channel_id is not None:
            logging.debug("Sending bot login message")
            await self.send_message(self.get_channel(self._main_channel_id), f"{self.bot_name} is online!")

    async def on_message(self, message):
        """
        When message is sent to any of the channels, check the message and respond appropriately

        :param message: Message that was recieved from the discord server
        """

        # Ignore bot's own messages
        if message.author == self.user:
            return

        else:
            logging.info("Message from %s at %s: %s", message.author, message.channel, message.content)

        # Play some Ping Pong with another user
        if message.content.lower() == "ping":
            await self.send_message(message.channel, "Pong")

    async def send_message(self, channel, message):
        """
        Send given message to the given channel

        :param channel: Target channel for the message
        :param message: Message to be sent to the channel
        """

        logging.debug("Sending '%s' to '%s'", message, channel)
        await channel.send(message)
