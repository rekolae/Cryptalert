"""
Module defining mixin class for use with Cogs

Emil Rekola <emil.rekola@hotmail.com>
"""

# Local imports
from cryptalert.discord_bot.bot import CryptalertBot


class BotMixin:
    """
    Define mixing class base
    """

    def __init__(self, bot: CryptalertBot):
        self.bot = bot
