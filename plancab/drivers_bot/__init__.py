from .handlers import init_handlers
from telethon import TelegramClient
import logging


async def init(bot: TelegramClient, parent_logger: logging.Logger):
    await init_handlers(bot, parent_logger.getChild("drivers"))


__all__ = ["init"]
