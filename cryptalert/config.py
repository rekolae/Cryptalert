"""
Handles reading all possible configurations from files and commandline and setting up logging

Emil Rekola <emil.rekola@hotmail.com>
"""

# STD imports
import logging
from pathlib import Path
from typing import List

# 3rd-party imports
from configargparse import ArgParser, ArgumentDefaultsRawHelpFormatter, Namespace


class Config:
    """
    Class for handling configuration parsing and serving as well as setting up logging
    """

    def __init__(self):
        self._config_file: Path = Path(__file__).parent.parent / "config.ini"
        self._verbosity: str = ""
        self._supported_currencies: List = ["btc", "eth", "ltc", "xrp", "xlm", "aave", "link", "usdc", "uni"]
        self._logger = logging.getLogger("Config")

        self._arg_parser = ArgParser(
            prog="Cryptalert",
            description="Watch cryptocurrency movements and alert the user based on them.",
            formatter_class=ArgumentDefaultsRawHelpFormatter,
            default_config_files=[str(self._config_file)]
        )

        self._add_arguments()

        # Parse args from config file, commandline and env vars
        self._config: Namespace = self._arg_parser.parse_args()
        self._config_logging()

    def _add_arguments(self) -> None:
        """
        Define args that are acknowledged by the application
        """

        self._arg_parser.add_argument(
            "-c", "--config",
            help="Config file path",
            type=Path,
            is_config_file=True
        )

        self._arg_parser.add_argument(
            "-v", "--verbosity",
            help="Application verbosity",
            type=str.upper,
            choices=["ERROR", "INFO", "DEBUG"],
            default="INFO"
        )

        self._arg_parser.add_argument(
            "-x", "--currencies",
            help="List of watched currencies",
            type=str.lower,
            choices=self._supported_currencies,
            nargs='+',
            default=self._supported_currencies
        )

        self._arg_parser.add_argument(
            "-p", "--ping-interval",
            help="How often to ping for data",
            type=int,
            default=5
        )

        self._arg_parser.add_argument(
            "-a", "--api-address",
            help="Address of the coinmotion API for fetching rates",
            type=str
        )

        self._arg_parser.add_argument(
            "-d", "--enable-discord-bot",
            help="Enable discord bot for notifications",
            action="store_true"
        )

        self._arg_parser.add_argument(
            "-b", "--bot-token",
            help="Discord bot token, must be present if -e/--enable-bot is used",
            type=str,
            env_var="CRYPTALERT_DISCORD_TOKEN"
        )

        self._arg_parser.add_argument(
            "-i", "--info-channel-id",
            help="Main channel ID, used for notifications when bot comes online or going offline",
            type=int,
            env_var="CRYPTALERT_DISCORD_MAIN_CHANNEL_ID"
        )

        self._arg_parser.add_argument(
            "-t", "--enable-tui",
            help="Enable the text ui",
            action="store_true"
        )

        self._arg_parser.add_argument(
            "--prefix",
            help="Command prefix e.g. '!someCommand'",
            type=str,
            default="!"
        )

    def get_args(self) -> Namespace:
        """
        Return the previously parsed args

        :return: Namespace holding all args and corresponding values
        """

        return self._config

    def get_arg(self, arg: str):
        """
        Return a single arg matching the given arg

        :param arg: Name of the arg
        :return: Value corresponding to the arg
        :rtype: Any
        """

        return getattr(self._config, arg)

    def _config_logging(self):
        """
        Setups logging with default/given verbosity and log file
        """

        # Set logging verbosity based on user configuration
        logging_level = getattr(logging, self._config.verbosity)

        # Hide messages made to the root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(logging.NullHandler())

        # Configure logger, use a log file when TUI is enabled
        if self._config.enable_tui:
            handler = logging.FileHandler(filename='cryptalert.log', encoding='utf-8', mode='w')

        else:
            handler = logging.StreamHandler()

        # Set format and level
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
        handler.setLevel(logging_level)

        # Modules that are going to be used
        modules = [
            "discord",
            "discord.bot"
            "Config",
            "TUI",
            "ApiAccessor",
            "Cryptalert"
        ]

        # Set handler for the modules
        for module in modules:
            logger = logging.getLogger(module)
            logger.handlers.clear()
            logger.setLevel(logging_level)
            logger.addHandler(handler)

        self._logger.error("Logging level has been set to '%s'", self._config.verbosity)

        if self._config.verbosity == "DEBUG":
            print(self._arg_parser.format_values())
