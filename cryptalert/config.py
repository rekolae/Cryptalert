"""
Handles reading all possible configurations from files and commandline and setting up logging
"""

from pathlib import Path
from argparse import ArgumentParser
from configparser import ConfigParser
from typing import Dict


class Config:
    """
    Class for handling configuration parsing and serving as well as setting up logging
    """

    def __init__(self):
        # Assume that the default config file is located in the root directory
        self.config_file = Path(__file__).parent.parent / "config.ini"
        self.config: Dict = {}
        self._config_parser = ConfigParser()
        self._arg_parser = ArgumentParser(
            description="Watch cryptocurrency movements and alert the user based on them",
            prog="cryptalert"
        )

        self._add_arguments()

    def _add_arguments(self) -> None:
        self._arg_parser.add_argument("-c", "--config", help="Config file path", type=Path)
        self._arg_parser.add_argument("-v", "--verbosity", action="count", default=0)

    def parse(self) -> bool:
        """
        Try to parse the config file either by using the default location or checking if the config file was specified
        in the commandline args

        :return: True if configuration parsing was succesful, False if not
        """

        self._parse_args()

        if not self.config_file.exists():
            return False

        self._parse_config_file()

        if self._check_config():
            return True

        else:
            return False

    def _parse_args(self) -> None:
        """
        Parse commandline args and extend the config file
        :return: True if configuration parsing was succesful, False if not
        """

        pass

    def _parse_config_file(self):
        """
        Parse configuration file and save the data to a class variable
        """

        pass

    def _check_config(self) -> bool:
        """
        Check if mandatory

        :return: True if configuration is ok, False if not
        """

        pass

    def get_config(self):
        """
        Return the parsed configuration

        :return: Dict holding parsed configurations
        """

        pass

    def config_logging(self):
        """
        Configure application logging
        """

        pass
