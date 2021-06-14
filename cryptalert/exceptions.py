"""
Definitions for different custom exceptions

Emil Rekola <emil.rekola@hotmail.com>
"""


class DataLengthException(Exception):
    """
    Custom exception when given data size is zero
    """


class ApiAddressException(Exception):
    """
    Custom exception when API address is none or the given address was invalid
    """


class UnsupportedOperationModeException(Exception):
    """
    Custom exception when both discord bot and TUI are disabled
    """
