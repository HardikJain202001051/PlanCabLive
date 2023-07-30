import os

from plancab import database, drivers_bot, riders_bot, shared, config, workers, locales
import asyncio
import tracemalloc
import tortoise
from telethon import TelegramClient

import logging

# whether to use colorlog or not
COLOR_MODE = os.getenv("COLOR_MODE", "").lower() in ("true", "1", "yes")
# logging level for 3rd party libraries
GLOBAL_LOGGING_LEVEL = logging.WARNING
# logging level for the cab bot
LOCAL_LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = "%(asctime)-15s.%(msecs)03d [%(levelname)-8s] %(name)-22s > %(filename)-18s:%(lineno)-5d - %(message)s"
LOGGING_DT_FORMAT = "%b %d %H:%M:%S"

if COLOR_MODE:
    import colorlog

    # color handler+formatter
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s" + LOGGING_FORMAT,
        datefmt=LOGGING_DT_FORMAT,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(formatter)

    # global logging
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(GLOBAL_LOGGING_LEVEL)

    logging.basicConfig(
        format=LOGGING_FORMAT,
        datefmt=LOGGING_DT_FORMAT,
        level=root_logger.level,
    )

    # local logging
    logger = logging.getLogger("cab")
    logger.setLevel(LOCAL_LOGGING_LEVEL)
    logger.propagate = False
    logger.addHandler(handler)
else:
    logging.basicConfig(
        format=LOGGING_FORMAT,
        datefmt=LOGGING_DT_FORMAT,
        level=GLOBAL_LOGGING_LEVEL,
    )
    logger = logging.getLogger("cab")
    logger.setLevel(LOCAL_LOGGING_LEVEL)


tracemalloc.start()


async def main():
    if not os.path.isdir("uploads"):
        # used for image submissions
        os.mkdir("uploads")

    logger.info("Validating locales...")
    locales.validate()
    logger.info("Locales validated")

    logger.info("Starting...")
    await database.init_db()
    cfg = config.init_config(logger)
    shared.config = cfg
    shared.drivers_bot = TelegramClient(
        "drivers_bot",
        cfg.api_id,
        cfg.api_hash,
        connection_retries=-1,
        retry_delay=5,
        auto_reconnect=True,
    )
    # noinspection PyUnresolvedReferences
    await shared.drivers_bot.start(bot_token=cfg.driver_bot_token)
    drivers_me = await shared.drivers_bot.get_me()
    shared.drivers_bot_username = drivers_me.username
    logger.info(f"Drivers bot started: {drivers_me.username}")
    shared.riders_bot = TelegramClient(
        "riders_bot",
        cfg.api_id,
        cfg.api_hash,
        connection_retries=-1,
        retry_delay=5,
        auto_reconnect=True,
    )
    # noinspection PyUnresolvedReferences
    await shared.riders_bot.start(bot_token=cfg.rider_bot_token)
    riders_me = await shared.riders_bot.get_me()
    shared.riders_bot_username = riders_me.username
    logger.info(f"Riders bot started: {riders_me.username}")
    await drivers_bot.init(shared.drivers_bot, logger)
    await riders_bot.init(shared.riders_bot, logger)
    await workers.init_workers(logger)
    logger.info("Everything initialized")
    await shared.drivers_bot.run_until_disconnected()


if __name__ == "__main__":
    exit_code = 0
    try:
        asyncio.run(main(),debug=True)
    except KeyboardInterrupt:
        logger.info("Exiting...")
    except Exception as e:
        logger.exception(e)
        # get exit code from exception
        exit_code = 1
    logging.basicConfig(level=logging.CRITICAL + 1)  # hide tortoise-orm logs

    asyncio.run(tortoise.Tortoise.close_connections())
    if shared.drivers_bot:
        asyncio.run(shared.drivers_bot.disconnect())
    if shared.riders_bot:
        asyncio.run(shared.riders_bot.disconnect())
    exit(exit_code)
