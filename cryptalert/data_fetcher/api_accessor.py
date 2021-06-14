"""
Handles fetching cryptocurrency data from the coinmotion API

Emil Rekola <emil.rekola@hotmail.com>
"""

# STD imports
import json
import logging
from time import sleep
from typing import List, Dict
from threading import Event
from datetime import datetime

# 3rd-party imports
from requests import get, ConnectionError


class ApiAccessor:
    """
    Class for handling data fetching for the application
    """

    def __init__(self, args, stop_flag):
        self.api_data: Dict = {}
        self.data_ready: Event = Event()
        self.api_address: str = args.api_address
        self.ping_interval: int = args.ping_interval
        self.currency_keys: List = [f"{currency}eur" for currency in args.currencies]
        self._stop_flag: Event = stop_flag
        self.last_succcesful_fetch = None
        self._logger = logging.getLogger("ApiAccessor")

    def fetch_data(self) -> None:
        """
        Fetch data by making a GET request to the coinmotion API
        """

        self._logger.debug("Fetching data")

        # Try to fetch data
        try:
            response = get(self.api_address)
            res = response.json()

        except json.JSONDecodeError:
            self._logger.error("No suitable response from API address '%s'", self.api_address)

        except ConnectionError:
            self._logger.error("Connection error while trying to fetch data")

        else:
            # Ignore empty data
            if data := self._parse_json(res):
                self.api_data = data
                self.last_succcesful_fetch = datetime.now().time()

    def _parse_json(self, response: Dict) -> Dict:
        """
        Parse the reponse that is a Dict and return filtered data

        :param response: Dict holding the response
        :return: Parsed data from the response
        """

        if not response["success"]:
            return {}

        filtered_currencies = self._filter_keys(response["payload"].keys())

        parsed_data = {}

        try:
            for currency in filtered_currencies:
                currency_data = response["payload"][currency]

                # Buy/Sell must be inverted to get the prespective of the user
                parsed_data[currency_data["currencyCode"]] = {
                    "sell": currency_data["buy"],
                    "buy": currency_data["sell"],
                    "changePercent": currency_data["fchangep"],
                    "high": currency_data["fhigh"]
                }

            # Total market trend
            parsed_data["market"] = {
                "changePercent": response["payload"]["market"]["changeAmount"],
                "sign": response["payload"]["market"]["changeSign"]
            }

        # If invalid Dict key is somehow used -> return empty Dict
        except KeyError:
            return {}

        else:
            return parsed_data

    def _filter_keys(self, keys) -> List:
        """
        Filter the the dict keys based on what currencies the user configured to be watched

        :param keys: List of the keys that are to filtered
        :return: Filtered keys
        """

        filtered_keys = []

        # Filter out keys that represent currencies that were not configured to be watched
        for key in keys:
            if key.lower() in self.currency_keys:
                filtered_keys.append(key)

        return filtered_keys

    def _sleep(self) -> None:
        """
        Sleep for configured amount of time before fetching data from the API again
        """

        # Try to skip the sleeping period if the flag was set during data fetch
        if not self._stop_flag.is_set():
            sleep(self.ping_interval)

    def start(self) -> None:
        """
        Loop indefinitely fetching data and sleeping until stop flag is set
        """

        self._logger.info("Starting data fetching loop")

        # Set flag after first batch of data is ready, loop until data could be fetched succesfully
        while not self.api_data:
            self.fetch_data()

        self.data_ready.set()

        # Fetch data and sleep
        while not self._stop_flag.is_set():
            self.fetch_data()
            self._sleep()

        self._logger.info("Data fetching loop stopped")
