"""
Discord bot for sending messages about current happenings in cryptocurrency movements

Emil Rekola <emil.rekola@hotmail.com>
"""

# STD imports
import logging
import datetime

# 3rd-party imports
from configargparse import Namespace
from discord.ext import commands
from discord.ext.commands import ExtensionNotFound, ExtensionFailed, NoEntryPointError

# Local imports
from cryptalert.data_fetcher.api_accessor import ApiAccessor


class CryptalertBot(commands.Bot):
    """
    Class with functionality and actions of the discord bot
    """

    extensions = [
        "crypto",
        "utils"
    ]

    def __init__(self, args: Namespace, api_accessor: ApiAccessor):
        super().__init__(command_prefix=args.prefix)
        self._main_channel_id: int = args.info_channel_id
        self.main_channel = None
        self.bot_name: str = self.user
        self.api_accessor: ApiAccessor = api_accessor
        self.update_interval: int = args.update_interval
        self._logger = logging.getLogger("discord.bot")
        self.startup_time: datetime = datetime.datetime.now()

    async def on_ready(self):
        """
        Executed when the bot has been initialized and connection has been made to discord
        """

        # Try to load extension, exit it there is a problem
        try:
            self.load_extensions()

        except (ExtensionNotFound, ExtensionFailed, NoEntryPointError):
            self._logger.exception("Extension load error, exiting!")
            await self.close(True)
            raise

        else:
            # Remove the "#xxxx" appendix from the bot username
            self.bot_name = str(self.user).split("#")[0]
            self._logger.info("%s is online!", self.bot_name)

            # If info channel was defined
            if self._main_channel_id is not None:
                self.main_channel = self.get_channel(self._main_channel_id)
                self._logger.debug("Sending login message")
                await self.main_channel.send(f"{self.bot_name} is online!")

    def load_extensions(self) -> None:
        """
        Try to load known extensions
        """

        for extension in self.extensions:
            self.load_extension(f"cryptalert.discord_bot.cogs.{extension}")

    async def close(self, error=False):
        """
        Overwrite close class method that is called when the Discord client is shutting down

        :param error: True if there was an error and no logout message is needed
        """

        # Send shutdown message if there was no error
        if not error:

            self._logger.info("Shutting down")

            if self._main_channel_id is not None:
                self._logger.info("Sending logout message")
                await self.main_channel.send(f"{self.bot_name} is going offline!")

        # Execute the original "close" function
        await super().close()
