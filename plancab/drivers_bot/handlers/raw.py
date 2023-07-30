import logging

from telethon import TelegramClient, events, types, utils, functions

from ... import database, locales, shared

logger = logging.getLogger("drivers.raw")


async def raw_handler(event: types.UpdateBotChatInviteRequester):
    peer_id = utils.get_peer_id(event.peer)
    if peer_id != shared.config.driver_group_id:
        return
    logger.debug(f"Got invite request from {event.user_id}")
    if not shared.config.driver_group_invite_link.startswith(
        (event.invite.link or "unknown").replace("...", "")
    ):
        logger.debug(f"Invite link is not mine, so ignoring.")
        return
    user = await database.User.get_or_none(user_id=event.user_id)
    can_be_let_in = False
    if user:
        driver = await user.get_driver()
        if driver.is_subscribed:
            can_be_let_in = True
    if not can_be_let_in:
        logger.debug(f"User {event.user_id} is not subscribed, not letting in.")
        await shared.drivers_bot(
            functions.messages.HideChatJoinRequestRequest(
                peer=event.peer, user_id=event.user_id, approved=False
            )
        )
        if user:
            loc = user.loc
        else:
            loc = locales.En
        # noinspection TryExceptPass,PyBroadException
        try:
            await shared.drivers_bot.send_message(
                event.user_id,
                loc.drivers_you_were_not_let_in_group_no_sub_text,
            )
        except Exception:
            pass
        return

    logger.debug(f"Approving invite request from {event.user_id} in {event.peer}.")
    await shared.drivers_bot(
        functions.messages.HideChatJoinRequestRequest(
            peer=event.peer, user_id=event.user_id, approved=True
        )
    )
    # noinspection TryExceptPass,PyBroadException
    try:
        await shared.drivers_bot.send_message(
            event.user_id,
            user.loc.drivers_you_were_let_in_group_has_sub_text,
        )
    except Exception:
        pass
    return


async def init_raw(bot: TelegramClient, parent_logger=None):
    global logger
    if parent_logger:
        logger = parent_logger.getChild("raw")
    bot.add_event_handler(
        raw_handler, events.Raw(types=[types.UpdateBotChatInviteRequester])
    )
    logger.info("Sett up raw handlers")
