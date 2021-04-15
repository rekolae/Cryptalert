"""
Brings all of the other modules together and starts the application

Emil Rekola <emil.rekola@hotmail.com>
"""


# Local imports
import asyncio
import logging
from time import sleep
from threading import Thread, Event

# 3rd-party imports
from configargparse import Namespace

# Local imports
from cryptalert.exceptions import ApiAddressException, UnsupportedOperationModeException
from cryptalert.config import Config
from cryptalert.data_fetcher.api_accessor import ApiAccessor
from cryptalert.discord_bot.bot import DiscordBot
from cryptalert.text_ui.tui import TUI


class Application:
    """
    Class for configuring and running the application
    """

    def __init__(self):

        self.args: Namespace = Config().get_args()
        self.exit_flag: Event = Event()
        self.start_bot: bool = False
        self.api_accessor = ApiAccessor(self.args, self.exit_flag)
        self._logger = logging.getLogger("Cryptalert")
        self.loop = None
        self.bot = None

    def run(self):
        """
        Run the application
        """

        print("Starting Cryptalert...")

        self.check_config()

        # Create a thread for the data fetcher
        self._logger.info("Starting ApiAccessor thread")
        api_thread = Thread(target=self.api_accessor.start)
        api_thread.start()

        self.api_accessor.data_ready.wait()

        if self.start_bot and self.args.enable_tui:
            self._logger.info("Starting both Discord bot and TUI")
            self.bot = DiscordBot(self.args.info_channel_id, self.api_accessor)
            self.loop = asyncio.get_event_loop()
            self._start_tui_and_bot()

        elif self.start_bot:
            self.bot = DiscordBot(self.args.info_channel_id, self.api_accessor)
            self._start_bot_only()

        elif self.args.enable_tui:
            self._start_tui()

        if self.args.enable_tui:
            print("Closing API data fetcher thread...")

        self._logger.info("Waiting for ApiAccessor thread to join")
        api_thread.join()

        if self.args.enable_tui:
            print("Shutdown complete!")

        self._logger.info("Shutdown complete")

    def _start_tui(self) -> None:
        """
        Start the text UI
        """

        self._logger.info("Starting TUI")
        TUI(self.exit_flag, self.api_accessor).start()
        self.exit_flag.wait()

    def _start_bot_only(self) -> None:
        """
        Start the Discord bot and set the shutdown flag on exit
        """

        self._logger.info("Starting Discord bot")
        self.bot.run(self.args.bot_token)
        self.exit_flag.set()

    def _start_tui_and_bot(self) -> None:
        """
        Start the Discord bot on a separate thread and shut it down on TUI exit
        """

        self.loop.create_task(self.bot.start(self.args.bot_token))

        self._logger.info("Starting Discord bot thread")
        bot_thread = Thread(target=self.loop.run_forever, name="Discord")
        bot_thread.start()

        self._start_tui()

        print("Closing Discord bot thread...")
        self._logger.info("Creating 'close' task for Discord bot")
        self.bot.loop.create_task(self.bot.close())

        # Give discord some time to shutdown properly
        self._logger.info("Giving time for the Discord bot to shutdown")
        sleep(15)

        print("Closing event loop...")
        self._logger.info("Stopping and closing event loop")
        self.loop.call_soon_threadsafe(self.loop.stop)
        bot_thread.join()

        self.loop.close()

    def check_config(self):
        """
        Parse configuration that were parsed from config file, commandline etc
        """

        self._logger.info("Checking config")

        if self.args.api_address is None:
            self._logger.critical("API address is None")
            raise ApiAddressException("API address is None")

        if not (self.args.enable_discord_bot or self.args.enable_tui):
            self._logger.critical("Discord bot and TUI aren't enabled")
            raise UnsupportedOperationModeException("Discord bot and TUI aren't enabled, atleast one must be enabled")

        if self.args.enable_discord_bot:
            if self.args.bot_token is not None:
                self.start_bot = True

            else:
                if not self.args.enable_tui:
                    self._logger.critical("Discord bot token not given and TUI not enabled")
                    raise UnsupportedOperationModeException("Discord bot token not given and TUI not enabled")

                self._logger.error("Discord bot token is None, bot will not be enabled")


# Start application if file is run as main
if __name__ == '__main__':
    app = Application()
    app.run()
