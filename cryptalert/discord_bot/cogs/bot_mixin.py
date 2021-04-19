"""
Module defining mixin class

Emil Rekola <emil.rekola@hotmail.com>
"""

from cryptalert.discord_bot.bot import CryptalertBot


class BotMixin:
    """
    Define mixing class base
    """

    def __init__(self, bot: CryptalertBot):
        self.bot = bot
