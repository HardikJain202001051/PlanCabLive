from telethon import TelegramClient
from ..config import Config

# noinspection PyTypeChecker
drivers_bot: TelegramClient = None
drivers_bot_username = None
# noinspection PyTypeChecker
riders_bot: TelegramClient = None
riders_bot_username = None
# noinspection PyTypeChecker
config: Config = None
