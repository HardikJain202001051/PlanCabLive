from .callbacks import init_cb
from .messages import init_msg
from .raw import init_raw

from telethon import TelegramClient
import logging


async def init_handlers(bot: TelegramClient, parent_logger: logging.Logger):
    await init_msg(bot, parent_logger)
    await init_cb(bot, parent_logger)
    await init_raw(bot, parent_logger)


__all__ = ["init_handlers"]
