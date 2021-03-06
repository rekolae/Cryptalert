"""
Handles fetching cryptocurrency data from the coinmotion API

Emil Rekola <emil.rekola@hotmail.com>, 2021
"""

# STD imports
import logging
from time import sleep
from typing import List, Dict
from multiprocessing import Event

# 3rd-party imports
from requests import get

# Local imports
from cryptalert.config import config


class ApiAccessor:
    """
    Class for handling data fetching for the application
    """

    def __init__(self, stop_flag):
        args = config.get_args()

        self.api_address: str = args.api_address
        self.ping_interval: int = args.ping_interval
        self.currency_keys: List = [f"{currency}eur" for currency in args.currencies]
        self._stop_flag: Event = stop_flag

    def fetch_data(self) -> Dict:
        """
        Fetch data by making a GET request to the coinmotion API
        """

        response = get(self.api_address)
        data = self._parse_json(response.json())
        return data

    def _parse_json(self, response: Dict) -> Dict:
        """
        Parse the reponse that is a Dict and return filtered data

        :param response: Dict holding the response
        :return: Parsed data from the response
        :rtype: Dict
        """

        if not response["success"]:
            return {}

        filtered_currencies = self._filter_keys(response["payload"].keys())

        parsed_data = {}

        for currency in filtered_currencies:
            currency_data = response["payload"][currency]

            parsed_data[currency_data["currencyCode"]] = {
                "buy": currency_data["buy"],
                "sell": currency_data["sell"],
                "changeAmount": currency_data["changeAmount"],
                "fchangep": currency_data["fchangep"],
                "fhigh": currency_data["fhigh"]
            }

        return parsed_data

    def _filter_keys(self, keys) -> List:
        """
        Filter the the dict keys based on what currencies the user configured to be watched

        :param keys: List of the keys that are to filtered
        :return: Filtered keys
        :rtype: List
        """

        filtered_keys = []

        # Filter out keys that represent currencies that were not configured to be watched
        for key in keys:
            if key.lower() in self.currency_keys:
                filtered_keys.append(key)

        return filtered_keys

    def sleep(self) -> None:
        """
        Sleep for configured amount of time before fetching data from the API again
        """

        sleep(self.ping_interval)

    def run(self) -> None:
        """
        Loop indefinitely fetching data and sleeping until stop flag is set
        """

        logging.info("Starting data fetching loop")

        while not self._stop_flag.is_set():
            print(self.fetch_data())
            self.sleep()

        logging.info("Data fetching loop stopped")
