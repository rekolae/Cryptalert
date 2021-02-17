"""
Handles reading all possible configurations from files and commandline and setting up logging
"""

from pathlib import Path
from argparse import ArgumentParser
from configparser import ConfigParser
from typing import List


class Config:
    """
    Class for handling configuration parsing and serving as well as setting up logging
    """

    def __init__(self):
        # Assume that the default config file is located in the root directory
        self._config_file: Path = Path(__file__).parent.parent / "config.ini"
        self._verbosity: str = ""

        self._config_parser = ConfigParser(allow_no_value=True)
        self._arg_parser = ArgumentParser(
            prog="cryptalert",
            description="Watch cryptocurrency movements and alert the user based on them"
        )

        self._add_arguments()

    def _add_arguments(self) -> None:
        self._arg_parser.add_argument(
            "-c",
            "--config",
            help="Config file path",
            type=Path
        )

        self._arg_parser.add_argument(
            "-v",
            "--verbosity",
            help="Application verbosity",
            choices=["ERROR, INFO, DEBUG"],
            default="INFO",
            type=str
        )

    def parse(self) -> bool:
        """
        Try to parse the config file either by using the default location or checking if the config file was specified
        in the commandline args

        :return: True if configuration parsing was succesful, False if not
        """

        # Parse commandline args first
        self._parse_args()
        self._config_logging()

        if not self._config_file.exists() or not self._parse_config_file():
            return False

        return True

    def _parse_args(self) -> None:
        """
        Parse commandline args and extend the config file
        :return: True if configuration parsing was succesful, False if not
        """

        args = self._arg_parser.parse_args()

        # Override default config file location
        if args.config is not None:
            self.config_file = args.config

        self._verbosity = args.verbosity

    def _parse_config_file(self) -> bool:
        """
        Parse configuration file and check validity
        """

        self._config_parser.read(self._config_file)
        return self._check_config()

    def _check_config(self) -> bool:
        """
        Check if mandatory sections are present

        :return: True if configuration is ok, False if not
        """

        # Chech that needed sections are present
        for section in ["CURRENCIES", "API REQUEST"]:
            if section not in self._config_parser.sections():
                return False

        # Check for unknow currencies
        for curr in self._config_parser["CURRENCIES"]:
            if curr not in ["btc", "eth", "ltc", "xrp", "xlm"]:
                return False

        return True

    def get_section(self):
        """
        Return the parsed configuration

        :return: Dict holding parsed configurations
        """

        pass

    def _config_logging(self):
        """
        Configure application logging
        """

        pass
