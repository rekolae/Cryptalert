"""
Handles showing the fetched data on a simple TUI

Emil Rekola <emil.rekola@hotmail.com>
"""

# STD imports
import curses
import logging
from multiprocessing import Event
from typing import Dict, Tuple, List

# Local imports
from cryptalert.data_fetcher.api_accessor import ApiAccessor
from cryptalert.exceptions import DataLengthException


class TUI:
    """
    Class for displaying a simple text UI
    """

    def __init__(self, exit_flag, api_accessor):
        self.api_accessor_proc: ApiAccessor = api_accessor
        self.api_data: Dict = {}
        self.has_colors: bool = False
        self.colors: Dict = {}
        self.color_pairs: Dict = {}
        self.stdscr = None
        self.main_win = None
        self.status_win = None
        self.data_win = None
        self.width: int = 0
        self.height: int = 0
        self.data_keys: List = []
        self.top_data_index: int = 0
        self.exit_flag: Event = exit_flag
        self._logger = logging.getLogger("TUI")

    def start(self) -> None:
        """
        Start the text UI in a wrapper
        """

        curses.wrapper(self.run)
        self.exit_flag.set()

    def run(self, stdscr):
        """
        Main function to be run by 'curses.wrapper', handles drawing the screen and displaying
        given data.

        :param stdscr: The main window object given by curses.wrapper
        """

        self.stdscr = stdscr
        self.init_tui()

        self.main_win.attron(curses.color_pair(self.color_pairs["BlueOnBlack"]))

        key_pressed = -1

        # Loop until user quits by pressing "q"
        while key_pressed != ord('q'):
            key_pressed = self.main_win.getch()

            if key_pressed == curses.KEY_UP:
                self.change_data("UP")

            elif key_pressed == curses.KEY_DOWN:
                self.change_data("DOWN")

            # Update data and refresh window
            self.display_data()
            self.main_win.refresh()

        self.main_win.attroff(curses.color_pair(self.color_pairs["BlueOnBlack"]))
        curses.endwin()

    def init_tui(self):
        """
        Initialize the text ui
        """

        self._logger.info("Initializing TUI")

        self.has_colors = curses.has_colors()
        self.height, self.width = self.stdscr.getmaxyx()

        # Remove cursor
        curses.curs_set(0)

        # No echo to screen
        curses.noecho()

        # Init screens
        self.init_colors()
        self.init_main_win()
        self.init_statusbar()
        self.init_data_win()

    def init_colors(self):
        """
        Initialize colors used by the TUI
        """

        self._logger.info("Initializing colors")

        # Check if terminal has color
        if not self.has_colors:
            return

        curses.start_color()

        # List of tuples with custom colors in format: (<NAME>, <R>, <G>, <B>)
        color_list = [
            ("Blue gray", 55, 71, 79),
            ("Light blue", 3, 155, 229)
        ]

        # Initialize the colors and add the colors to a class variable for lookup
        # Start from value of 9 because curses.start_color initializes 8 basic colors
        color_num = 9
        for color in color_list:

            # Convert color value scale from 0-255 -> 0-1000
            r, g, b = self._rgb_2_curses_color(color[1], color[2], color[3])

            # Add color to lookup table with name as key and color num as value
            self.colors[color[0]] = color_num
            curses.init_color(color_num, r, g, b)

            color_num += 1

        # List of tuples with custom color pairs in format: (<NAME>, <FOREGROUND>, <BACKGROUND>)
        color_pair_list = [
            ("BlueOnGray", self.colors["Light blue"], self.colors["Blue gray"]),
            ("BlueOnBlack", self.colors["Light blue"], curses.COLOR_BLACK)
        ]

        # Initialize the color pairs and add them to a class variable for lookup
        # Start from value of 1 because 0 is reserved for black/white and cannot be overwritten
        color_pair_num = 1
        for color_pair in color_pair_list:
            self.color_pairs[color_pair[0]] = color_pair_num
            curses.init_pair(color_pair_num, color_pair[1], color_pair[2])

            color_pair_num += 1

    def init_main_win(self):
        """
        Initialize a window inside the main terminal window that houses other windows
        """

        self._logger.info("Initializing main window")

        self.main_win = self.stdscr.subwin(0, 0)

        # Turn on wanted colors
        self.main_win.attron(curses.color_pair(self.color_pairs["BlueOnBlack"]))

        self.main_win.keypad(True)

        # Set input timeout to 250ms
        self.main_win.timeout(250)

        self.main_win.border()

        # Turn off the set colors
        self.main_win.attroff(curses.color_pair(self.color_pairs["BlueOnBlack"]))

    def init_statusbar(self):
        """
        Initialize a statusbar window inside the main window, holds navigation and quit commands etc
        """

        self._logger.info("Initializing statusbar")

        self.status_win = self.main_win.subwin(3, self.width - 2, 1, 1)

        # Turn on wanted colors
        self.status_win.attron(curses.color_pair(self.color_pairs["BlueOnBlack"]))

        self.status_win.border()

        prog = "Cryptalert V0.0.0 ALPHA"
        creator = "Emil Rekola <emil.rekola@hotmail.com>"
        commands = "Q to quit | UP/DOWN to change data"
        status_str = f"{prog} | {creator} | {commands}"

        # Calculate center position for the string
        center = round(self.width / 2) - round(len(status_str) / 2)
        self.status_win.addstr(1, center, status_str)

        # Turn off the set colors
        self.status_win.attroff(curses.color_pair(self.color_pairs["BlueOnBlack"]))

    def init_data_win(self):
        """
        Initialize data window, shows the given data
        """

        self._logger.info("Initializing data window")

        self.data_keys = list(self.api_accessor_proc.api_data.keys())

        # No data to display
        if len(self.data_keys) == 0:
            raise DataLengthException("No data to display")

        # Set window size based on watched currencies
        if len(self.data_keys) == 1:
            self.data_win = self.main_win.subwin(7, self.width - 2, 8, 1)

        elif len(self.data_keys) == 2:
            self.data_win = self.main_win.subwin(13, self.width - 2, 8, 1)

        else:
            self.data_win = self.main_win.subwin(19, self.width - 2, 8, 1)

        self.display_data()

        self.data_win.bkgd(curses.color_pair(1))

    def display_data(self):
        """
        Display the given data on the TUI
        """

        # Get data every time display data is called
        self.api_data = self.api_accessor_proc.api_data

        self.main_win.attron(curses.color_pair(self.color_pairs["BlueOnBlack"]))

        if self.api_data["market"]["sign"]:
            msg = f"Current market is rising! Current change is +{self.api_data['market']['changePercent']}%!"

        else:
            msg = f"Current market is dropping! Current change is -{self.api_data['market']['changePercent']}%!"

        self.main_win.addstr(5, 2, msg)

        self.main_win.attroff(curses.color_pair(self.color_pairs["BlueOnBlack"]))

        self.data_win.clear()
        self.data_win.border()

        # Turn on wanted colors
        self.data_win.attron(curses.color_pair(self.color_pairs["BlueOnGray"]))

        if len(self.data_keys) == 1:
            data_row = 1
            self.data_win.addstr(data_row, 1, self.data_keys[0])
            for key, val in self.api_data[self.data_keys[0]].items():
                data_row += 1
                self.data_win.addstr(data_row, 12, f"{key}: {val}")

        # Display the fetched data on the created data window
        else:
            end_index = 3

            if len(self.data_keys) == 2:
                end_index = 2

            separator = "-" * (self.width - 4)

            data_row = 1
            row_multiplier = 1

            for index in range(self.top_data_index, self.top_data_index + end_index):
                self.data_win.addstr(data_row, 1, self.data_keys[index])

                for key, val in self.api_data[self.data_keys[index]].items():
                    self.data_win.addstr(data_row + 1, 12, f"{key}: {val}")
                    data_row += 1

                if index < self.top_data_index + end_index - 1:
                    self.data_win.addstr(data_row + 1, 1, separator)

                data_row = row_multiplier * 6 + 1
                row_multiplier += 1

        # Turn off the set colors
        self.data_win.attroff(curses.color_pair(self.color_pairs["BlueOnGray"]))

    def change_data(self, direction: str):
        """
        Move data in the data window up or down

        :param direction: Tell if data should be moved up or down
        """

        if direction == "UP" and self.top_data_index >= 1:
            self.top_data_index -= 1
            self.display_data()

        elif direction == "DOWN" and self.top_data_index + 3 < len(self.data_keys):
            self.top_data_index += 1
            self.display_data()

    @staticmethod
    def _rgb_2_curses_color(r, g, b) -> Tuple[int, int, int]:
        """
        Convert standard 8-bit RGB values (0-255) to a range that curses module
        understands (0-1000). e.g. 128 -> 502

        :param r: Red value
        :param g: Green value
        :param b: Blue value
        :return: Scaled RGB values
        """

        # Scale values and round them to integers
        r = round((r / 255) * 1000)
        g = round((g / 255) * 1000)
        b = round((b / 255) * 1000)

        return r, g, b
