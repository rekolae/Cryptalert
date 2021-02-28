"""
Handles showing the fetched data on a simple TUI

Emil Rekola <emil.rekola@hotmail.com>, 2021
"""

import curses
from typing import Dict, Tuple


class TUI:
    """
    Class for displaying a simple text UI
    """

    def __init__(self):
        self.has_colors = curses.has_colors()
        self.colors: Dict = {}

    def init_curses(self):
        pass

    def init_colors(self):
        """
        Initialize colors used by the TUI
        """

        # Check if terminal has color
        if self.has_colors:
            curses.start_color()

            # List of tuples with custom colors in format: (<NAME>, <R>, <G>, <B>)
            color_list = [
                ("Gray", 61, 61, 61),
                ("Light blue", 3, 155, 229)
            ]

            # Initialize the colors and add the colors to a class variable for lookup
            # Start from value of 9 because curses.start_color initializes 8 basic colors
            color_num = 9
            for color in color_list:
                # Add color to lookup table with name as key and color num as value
                self.colors[color[0]] = color_num

                # Convert value 0-255 -> 0-1000
                r, g, b = self._rgb_2_curses_color(color[1], color[2], color[3])
                curses.init_color(color_num, r, g, b)

                color_num += 1

    def update_data_windows(self):
        pass

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
