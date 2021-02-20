"""
Handles reading all possible configurations from files and commandline and setting up logging

Emil Rekola <emil.rekola@hotmail.com>, 2021
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
        self._config: Namespace = Namespace()
        self._supported_currencies: List = ["btc", "eth", "ltc", "xrp", "xlm"]

        self._arg_parser = ArgParser(
            prog="cryptalert",
            description="Watch cryptocurrency movements and alert the user based on them.",
            formatter_class=ArgumentDefaultsRawHelpFormatter,
            default_config_files=[str(self._config_file)]
        )

        self._add_arguments()

    def _add_arguments(self) -> None:
        self._arg_parser.add_argument(
            "-c",
            "--config",
            help="Config file path",
            type=Path,
            is_config_file=True
        )

        self._arg_parser.add_argument(
            "-v",
            "--verbosity",
            help="Application verbosity",
            choices=["ERROR", "INFO", "DEBUG"],
            default="INFO",
            type=str.upper
        )

        self._arg_parser.add_argument(
            "--currencies",
            help="List of watched currencies",
            choices=self._supported_currencies,
            nargs='+',
            default=self._supported_currencies,
            type=str.lower
        )

        self._arg_parser.add_argument(
            "-p",
            "--ping-interval",
            help="How often to ping for data",
            default=10,
            type=int
        )

        self._arg_parser.add_argument(
            "-e",
            "--enable-bot",
            help="Enable discord bot",
            action="store_true"
        )

        self._arg_parser.add_argument(
            "-t",
            "--bot-token",
            help="Discord bot token, must be present if -e/--enable-bot is used",
            type=str,
            env_var="CRYPTALERT_DISCORD_TOKEN"
        )

    def parse_args(self) -> None:
        """
        Try to parse the config file either by using the default location or checking if the config file was specified
        in the commandline args

        :return: True if configuration parsing was succesful, False if not
        """

        # Parse commandline args first
        self._config = self._arg_parser.parse_args()
        self._config_logging()

    def get_args(self) -> Namespace:
        """
        Return the parsed args

        :return: Namespace holding all args and corresponding values
        """

        return self._config

    def _config_logging(self):
        """
        Setups logging with default/given verbosity
        """

        # Set logging verbosity based on user configuration
        logging_level = getattr(logging, self._config.verbosity)

        # Configure logger
        logging.basicConfig(level=logging_level)

        logging.info("Logging has been set to %s", self._config.verbosity)
        logging.debug(self._arg_parser.format_values())
