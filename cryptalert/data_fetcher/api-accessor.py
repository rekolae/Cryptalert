"""
Handles fetching cryptocurrency data from the coinmotion API

Emil Rekola <emil.rekola@hotmail.com>, 2021
"""

# STD imports
from time import sleep
from typing import List

# 3rd-party imports
from requests import get

# Local imports
from cryptalert import config


class ApiAccessor:
    """
    Class for handling data fetching for
    """

    def __init__(self):
        args = config.get_args()

        self.api_address: str = args.api_address
        self.ping_interval: int = args.ping_interval
        self.currencies: List = args.currencies

    def fetch_data(self):
        pass

    def parse_data(self):
        pass

    def sleep(self):
        pass

