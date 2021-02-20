"""
Main entry point for the application

Emil Rekola <emil.rekola@hotmail.com>, 2021
"""

# STD imports
from pathlib import Path

# Local imports
from cryptalert.config import Config


# Get application name from the project folder name
prog_name = Path(__file__).parent.parent.name

# Initialize application config class
config = Config()
