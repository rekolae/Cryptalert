"""
Discord bot initialization

Emil Rekola <emil.rekola@hotmail.com>, 2021
"""

# Local imports
from cryptalert.config import config
from cryptalert.discord_bot.bot import DiscordBot

print(config.get_args())
discord_bot = DiscordBot(config.get_arg("info_channel_id"))
