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
        self.has_colors: bool = False
        self.colors: Dict = {}
        self.color_pairs: Dict = {}
        self.stdscr = None
        self.main_win = None
        self.status_win = None
        self.width: int = 0
        self.height: int = 0

    def init_tui(self):
        """
        Initialize the text ui
        """

        self.has_colors = curses.has_colors()
        self.height, self.width = self.stdscr.getmaxyx()

        # Remove cursor
        curses.curs_set(0)

        # No echo to screen
        curses.noecho()

        # Init screens
        self.init_colors()
        self.init_main_win()
        self.init_status_bar()

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
        while key_pressed != ord('q'):
            key_pressed = self.main_win.getch()
            self.main_win.addstr(5, 2, f"Key pressed: {key_pressed}")

            if key_pressed == curses.KEY_UP:
                self.main_win.addstr(6, 2, "going up...")

            elif key_pressed == curses.KEY_DOWN:
                self.main_win.addstr(6, 2, "going down...")

            elif key_pressed == curses.KEY_RIGHT:
                self.main_win.addstr(6, 2, "going right...")

            elif key_pressed == curses.KEY_LEFT:
                self.main_win.addstr(6, 2, "going left...")

            self.main_win.refresh()

        self.main_win.attroff(curses.color_pair(self.color_pairs["BlueOnBlack"]))
        curses.endwin()

    def init_main_win(self):
        """
        Initialize a window inside the main terminal window that houses other windows
        """

        self.main_win = self.stdscr.subwin(0, 0)

        # Turn on wanted colors
        self.main_win.attron(curses.color_pair(self.color_pairs["BlueOnBlack"]))

        self.main_win.keypad(True)
        self.main_win.border()

        # Turn off the set colors
        self.main_win.attroff(curses.color_pair(self.color_pairs["BlueOnBlack"]))

    def init_status_bar(self):
        """
        Initialize a statusbar window inside the main window, holds navigation and quit commands etc
        """

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

    def init_colors(self):
        """
        Initialize colors used by the TUI
        """

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
