import re
import typing

import pytz
import copy

from ... import database, locales, shared, common, bot_utils
from telethon import TelegramClient, events, Button, types, utils, functions
from telethon.errors import rpcerrorlist
from .helper import time_text_handler, date_text_handler, address_text_handler, location_text_handler, \
    generate_date_buttons, generate_time_buttons, cost_calculators
from telethon.tl import patched
import logging
import datetime
import asyncio
import tempfile
import qrcode

logger = logging.getLogger("riders.messages")

get_info_steps: typing.Dict[str, common.QuestionStep] = {
    "full_name": common.QuestionStep("ride_step_full_name", common.ResponseType.TEXT),
    "phone": common.QuestionStep("ride_step_phone_number", common.ResponseType.TEXT),
}
intracity_order_steps: typing.Dict[str, common.QuestionStep | None] = {
    "no_of_hours": None,  # todo
    "date": common.QuestionStep(
        "ride_step_date",
        common.ResponseType.TEXT,
        regex=r"^\d{1,2}[,./ -]\d{1,2}[,./ -]?(?:\d{4}|\d{2})?$",
        textfmt=lambda x: x.format(
            date_now=datetime.datetime.now(tz=common.tz).strftime("%d.%m.%Y")
        ),
    ),
    "time": common.QuestionStep(
        "ride_step_time",
        common.ResponseType.TEXT,
        regex=r"^\d{1,2}:\d{2}$",
        textfmt=lambda x: x.format(
            time_now=datetime.datetime.now(tz=common.tz).strftime("%H:%M")
        ),
    ),
    "from": common.QuestionStep(
        "ride_step_from", [common.ResponseType.LOCATION, common.ResponseType.TEXT]
    ),
    "to": common.QuestionStep(
        "ride_step_to", [common.ResponseType.LOCATION, common.ResponseType.TEXT]
    ),
}
office_commute_order_steps: typing.Dict[str, common.QuestionStep | None] = {
    "office_commute|d": None,
    "office_commute|date": None,
    "drop_time|date": None,
    "drop_time|time": None,
    "office_commute_dt|time": None,
    "from": common.QuestionStep(
        "ride_step_from", [common.ResponseType.LOCATION, common.ResponseType.TEXT]
    ),
    "to": common.QuestionStep(
        "ride_step_to", [common.ResponseType.LOCATION, common.ResponseType.TEXT]
    ),
}

two_way_order_steps: typing.Dict[str, common.QuestionStep | None,] = {
    "first_trip|date": None,
    "first_trip|time": None,
    "round_trip|date": None,
    "round_trip|time": None,
    "from": common.QuestionStep(
        "ride_step_from", [common.ResponseType.LOCATION, common.ResponseType.TEXT]
    ),
    "to": common.QuestionStep(
        "ride_step_to", [common.ResponseType.LOCATION, common.ResponseType.TEXT]
    ),
}

ride_order_steps: typing.Dict[str, common.QuestionStep] = {

    "date": common.QuestionStep(
        "ride_step_date",
        common.ResponseType.TEXT,
        regex=r"^\d{1,2}[,./ -]\d{1,2}[,./ -]?(?:\d{4}|\d{2})?$",
        textfmt=lambda x: x.format(
            date_now=datetime.datetime.now(tz=common.tz).strftime("%d.%m.%Y")
        ),
    ),
    "time": common.QuestionStep(
        "ride_step_time",
        common.ResponseType.TEXT,
        regex=r"^\d{1,2}:\d{2}$",
        textfmt=lambda x: x.format(
            time_now=datetime.datetime.now(tz=common.tz).strftime("%H:%M")
        ),
    ),
    "from": common.QuestionStep(
        "ride_step_from", [common.ResponseType.LOCATION, common.ResponseType.TEXT]
    ),
    "to": common.QuestionStep(
        "ride_step_to", [common.ResponseType.LOCATION, common.ResponseType.TEXT]
    ),
}


class UserPayload:
    intracity = "intracity"
    info_step = "info_step"
    ride_step = "ride_step"
    two_way_step = "two_way_step"
    office_commute_step = "office_commute_step"
    payment_step = "payment_step"
    waiting_for_payment_confirmation = "waiting_for_payment_confirmation"
    feedback_comment = "feedback_comment"


user_payload_binds = {}


def msg_payload_handler(data: str):
    def decorator(
            func: typing.Callable[
                [events.NewMessage.Event, database.User, database.UserState],
                typing.Awaitable[None],
            ]
    ):
        global user_payload_binds
        user_payload_binds[data] = {"f": func}
        return func

    return decorator


commands_binds = {}


def command_handler(
        command: str,
        set_command=False,
        description_en: str = None,
        description_hi: str = None,
        description_kn: str = None,
        owner_only=False,
):
    def decorator(
            func: typing.Callable[
                [events.NewMessage.Event, database.User, bool, database.UserState],
                typing.Awaitable[None],
            ]
    ):
        global commands_binds
        commands_binds[command] = {
            "f": func,
            "set": set_command,
            "d_en": description_en,
            "d_hi": description_hi,
            "d_kn": description_kn,
            "owner_only": owner_only,
        }
        return func

    return decorator


@command_handler(
    "start",
    set_command=True,
    description_en="Main menu, order a ride",
    description_hi="मुख्य मेनू, राइड आर्डर करें",
    description_kn="ಮುಖ್ಯ ಮೆನು, ರೈಡ್ ಆರ್ಡರ್ ಮಾಡಿ",
)
async def start_handler(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = ""
    state.value = {}
    await state.save()
    await event.respond(file="driver_welcome.gif")
    if is_new_user:
        asyncio.create_task(
            bot_utils.send_user_to_privacy_share_group(event.client, event.get_sender())
        )
    if ref := re.findall(r"start r(\d+)", event.raw_text):
        ref_by = int(ref[0])
        if ref_by != user.user_id:
            referer = await database.User.get_or_none(user_id=ref_by)
            referred = user
            if referer:
                exists = await database.ReferralPoint.get_or_none(
                    referer=referer, referred=referred
                )
                if not exists:
                    await database.ReferralPoint.create(
                        referer=referer,
                        referred=referred,
                    )

    if is_new_user:
        state.payload = UserPayload.info_step
        state.value["info_step"] = 'name'
        await state.save()
        await event.message.respond(get_info_steps["full_name"].get_text(user))
        return
    await event.respond(
        user.loc.riders_welcome_text.format(name=user.full_name),
        buttons=user.loc.riders_start_order_button,
    )


@command_handler(
    "info",
    set_command=True,
    description_en="Change your name and phone number",
    description_hi="Change your name and phone number",  # todo : change
    description_kn="Change your name and phone number",
)
@msg_payload_handler(UserPayload.info_step)
async def info_handler(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    if state.payload == "":
        state.payload = UserPayload.info_step
        state.value["info_step"] = 'name'
        await state.save()
        await event.message.respond(get_info_steps["full_name"].get_text(user))
    elif state.value["info_step"] == 'name':
        user.full_name = event.message.text
        await user.save()
        state.value["info_step"] = 'number'
        await state.save()
        await event.respond(get_info_steps["phone"].get_text(user))
    elif state.value["info_step"] == 'number':
        number = event.message.text
        user.phone_number = number
        await user.save()
        state.payload = ""
        state.value["info_step"] = None
        await state.save()
        await event.respond("Your details have been successfully saved ✔️")
        await event.respond(
            user.loc.please_select_language_text,
            buttons=user.loc.select_language_buttons,
        )


@command_handler(
    "help",
    set_command=True,
    description_en="See help",
    description_hi="See help",
    description_kn="See help",
)
async def help_command(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    await event.respond(user.loc.help)


@command_handler(
    "rides",
    set_command=False,
    description_en="See rides",
    description_hi="See rides",
    description_kn="See rides",
)
async def see_rides_status(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    rides = await database.Ride.filter(user=user).all()

    if not rides:
        await event.respond("You have no rides.")
        return

    response = "Here are your ride details:\n\n"
    for ride in rides:
        pickup_time_scheduled = ride.pickup_time_scheduled_timezone_aware
        pickup_time_scheduled_in_str = pickup_time_scheduled.strftime("%Y-%m-%d %H:%M:%S")
        # return_time_scheduled = ride.return_time_scheduled_timezone_aware.strftime(
        #    "%Y-%m-%d %H:%M:%S") if ride.return_time_scheduled_timezone_aware else "Not scheduled"
        now = datetime.datetime.now()
        if ride.days_of_office_commute == '' and pickup_time_scheduled > now:
            continue
        category = await ride.category
        id = ride.id
        from_text_address = ride.from_text_address
        to_text_address = ride.to_text_address
        days_of_office_commute = ride.days_of_office_commute
        status = ride.status
        cost = ride.cost
        days_and_rides_left = 'Days of Office Commute: ' + ' '.join(
            ride.days_of_office_commute.split('|')[:-1]) + '\nRides : ' + \
                              ride.days_of_office_commute.split('|')[-1]
        response += f"Ride #{id}\n"
        response += f"Category: {category.name}\n"
        # response += f"From: {from_text_address}\n"
        # response += f"To: {to_text_address}\n"
        response += f"Pickup Time: {pickup_time_scheduled_in_str}\n"
        response += f"{days_and_rides_left}\n"
        # response += f"Status: {status}\n"
        # response += f"Fare: {cost}\n\n"
        response += "@#$"

    response = response.split('@#$')[:-1]
    for i in response:
        await event.respond(i)


@command_handler(
    "language",
    set_command=True,
    description_en="Select language",
    description_hi="भाषा चुनें",
    description_kn="ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
)
async def language_handler(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    # show a language selection menu
    await event.respond(
        user.loc.please_select_language_text,
        buttons=user.loc.select_language_buttons,
    )


@command_handler(
    "order",
    set_command=True,
    description_en="Order a ride",
    description_hi="राइड आर्डर करें",
    description_kn="ರೈಡ್ ಆರ್ಡರ್ ಮಾಡಿ",
)
async def order_handler(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    if is_new_user:
        # show a language selection menu
        await event.respond(
            user.loc.please_select_language_text,
            buttons=user.loc.select_language_buttons,
        )
        return
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = ""
    state.value = {}
    await state.save()

    await event.respond(
        user.loc.riders_please_select_booking_type_text,
        buttons=user.loc.riders_booking_type_btns,
    )

    """
    all_categories = await database.CabCategory.filter(enabled=True)
    buttons = []
    for category in all_categories:
        buttons.append(
            [
                Button.inline(
                    category.name,
                    data=f"order_category|{category.id}",
                )
            ]
        )
    buttons = [Button.inline("5 seater",data="order_category|5"),Button.inline("7 seater",data="order_category|7")]
    await event.respond(
        user.loc.riders_please_select_category_text,
        buttons=buttons,
    )
    """


@command_handler(
    "referral",
    set_command=True,
    description_en="Refer a friend",
    description_hi="दोस्त को रेफर करें",
    description_kn="ಸ್ನೇಹಿತರಿಗೆ ಸೂಚಿಸಿ",
)
async def referral_handler(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    link = f"https://t.me/{shared.riders_bot_username}?start=r{user.user_id}"
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        qr = qrcode.make(link)
        qr.save(tmp, "PNG")
        tmp.seek(0)
        uploaded = await event.client.upload_file(tmp, file_name="qr.png")

    await event.respond(
        user.loc.riders_referrals_info_text.format(
            referral_link=link,
            referral_count=await database.ReferralPoint.filter(referer=user).count(),
            redeemable_amount=await database.ReferralPoint.filter(
                referer=user, ride_id__isnull=False, point_used=False
            ).count(),
        ),
        file=uploaded,
    )


@msg_payload_handler(UserPayload.ride_step)
async def ride_step_handler(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    message: patched.Message = event.message
    question_key = state.value["order_step"]
    question_data: common.QuestionStep = ride_order_steps[question_key]
    answer_type = question_data.validate(message)
    if not answer_type:
        await event.respond(user.loc.riders_answer_incorrect_format_text)
        return
    if answer_type == common.ResponseType.TEXT:
        if question_key == "from" or question_key == "to":
            return_flag = await address_text_handler(event, question_key, message, user, state)
            if return_flag:
                return
        elif question_key == "time":
            return_flag = await time_text_handler(event, message, user, state,
                                                  state_key="order_data")
            if return_flag:
                return
        elif question_key == "date":
            return_flag = await date_text_handler(event, message, user, state,
                                                  state_key="order_data")
            if return_flag:
                return
    elif answer_type == common.ResponseType.LOCATION:
        await location_text_handler(message, question_key, event, user, state)
    else:
        raise NotImplementedError

    ride_steps_keys = list(ride_order_steps.keys())
    is_last = question_key == ride_steps_keys[-1]

    prev_question_button = Button.inline(
        user.loc.prev_step_btntext,
        data=f"order_goto_step_for_message|" + question_key,
    )
    if is_last:
        # state.payload = ""
        # state.value["stack"] = state.value["stack"][:]
        await state.save()
        m = await event.respond(user.loc.please_wait_text)
        try:
            time_seconds, distance_meters = await bot_utils.get_drive_time_and_distance(
                from_lat=state.value["order_data"]["from"]["lat"],
                from_lng=state.value["order_data"]["from"]["lon"],
                to_lat=state.value["order_data"]["to"]["lat"],
                to_lng=state.value["order_data"]["to"]["lon"],
            )
        except bot_utils.ExceptionWillReturnToUser as e:
            if e.code == "ZERO_RESULTS":
                await m.edit(
                    user.loc.riders_no_route_found_text,
                    buttons=[[prev_question_button]],
                )
                return
            elif e.code == "NOT_FOUND":
                await m.edit(
                    user.loc.riders_location_not_found_text,
                    buttons=[[prev_question_button]],
                )
                return
            else:
                raise e

        state.value["order_data"]["time_seconds"] = time_seconds
        state.value["order_data"]["distance_meters"] = distance_meters
        await state.save()

        category = await database.CabCategory.get(
            id=state.value["order_data"]["category"]
        )
        bookingType = state.value["order_data"]["booking_type"]

        state.value["order_data"]["full_name"] = user.full_name
        state.value["order_data"]["phone"] = user.phone_number

        await state.save()
        if bookingType == 1:
            price = await cost_calculators(category.id, bookingType, distance_meters)
            bookingType = "Two-Way"
            state.value["order_data"]["price"] = price
            await state.save()
            dt = state.value["order_data"]["time"]
            dt_r = state.value["round_trip"]["time"]
            await m.edit(
                user.loc.riders_ride_data_preview_text.format(
                    datetime=dt.strftime("%d.%m.%Y %H:%M") + '\n🔙 Return time: ' + dt_r.strftime("%d.%m.%Y %H:%M"),
                    full_name=state.value["order_data"]["full_name"],
                    phone_number=state.value["order_data"]["phone"],
                    distance=round(distance_meters / 1000.0, 2),
                    duration=bot_utils.seconds_to_human_readable(time_seconds),
                    price=round(price / 100.0, 2),
                    category=category.name + ' | ' + bookingType + '\n💸Discount: 5%\n',
                ),
                buttons=[
                    [
                        Button.inline(
                            user.loc.riders_confirm_order_btntext, data="confirm_order"
                        )
                    ],
                    [prev_question_button],
                    [Button.inline(user.loc.cancel_btntext, data="start|clear")],
                ],
            )
        elif bookingType == 2:

            def find_nearest_date(pc, weekdays):
                counter = -1
                while True:
                    # Increment the counter by 1 for each iteration
                    counter += 1
                    date = pc + datetime.timedelta(days=counter)
                    if date.strftime('%a') in weekdays:
                        return date

            no_of_rides = int(state.value["commute_info"]["no_of_rides"][:-1])

            temp = state.value["commute_info"]['days_of_week']
            days = []
            for i in temp:
                days.append(user.loc.days[int(i)])

            days = sorted(days, key=lambda x: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].index(x))
            state.value["commute_info"]["days_of_week"] = days
            pc = find_nearest_date(state.value['order_data']['time'], days)
            state.value["order_data"]["time"] = pc
            rc = find_nearest_date(state.value['commute_info']['drop_time'], days)
            state.value["commute_info"]["drop_time"] = rc

            total_days = 0
            for i in range(no_of_rides):
                current_date = pc + datetime.timedelta(days=i)
                if current_date.strftime('%a') in days:
                    total_days += 1
            ds = 0

            price = await cost_calculators(category.id, bookingType, distance_meters, pack=no_of_rides) * total_days
            state.value["order_data"]["price"] = price
            await state.save()
            bookingType = "Office Commute"
            days = " ".join(days)
            await m.edit(
                user.loc.riders_ride_data_preview_text.format(
                    datetime=pc.strftime("%d.%m.%Y %H:%M") + '\n🔙 Return time: ' + rc.strftime(
                        "%H:%M") + '\n📆 Days: ' + days + '\n🔢Pack Selected: ' +
                             str(no_of_rides) + '\n',
                    full_name=state.value["order_data"]["full_name"],
                    phone_number=state.value["order_data"]["phone"],
                    distance=round(distance_meters / 1000.0, 2),
                    duration=bot_utils.seconds_to_human_readable(time_seconds),
                    price=round(price / 100.0, 2),
                    category=category.name + ' | ' + bookingType + '\n💸Discount: ' + str(ds) + '%\n',
                ),
                buttons=[
                    [
                        Button.inline(
                            user.loc.riders_confirm_order_btntext, data="confirm_order"
                        )
                    ],
                    # [prev_question_button], todo:
                    [Button.inline(user.loc.cancel_btntext, data="start|clear")],
                ]
            )
        else:
            price = await cost_calculators(category.id, bookingType, distance_meters)
            state.value["order_data"]["price"] = price
            if bookingType == 4:
                bookingType = 'Outstation'
            elif bookingType == 5:
                bookingType = 'Pet Friendly'
            else:
                bookingType = 'One-Way'
            await state.save()
            dt = state.value["order_data"]["time"]
            await m.edit(
                user.loc.riders_ride_data_preview_text.format(
                    datetime=dt.strftime("%d.%m.%Y %H:%M"),
                    full_name=state.value["order_data"]["full_name"],
                    phone_number=state.value["order_data"]["phone"],
                    distance=round(distance_meters / 1000.0, 2),
                    duration=bot_utils.seconds_to_human_readable(time_seconds),
                    price=round(price / 100.0, 2),
                    category=category.name + ' | ' + bookingType,
                ),
                buttons=[
                    [
                        Button.inline(
                            user.loc.riders_confirm_order_btntext, data="confirm_order"
                        )
                    ],
                    [prev_question_button],
                    [Button.inline(user.loc.cancel_btntext, data="start|clear")],
                ]
            )

        return

    next_step_key = ride_steps_keys[ride_steps_keys.index(question_key) + 1]
    state.value["order_step"] = next_step_key
    next_step_data: common.QuestionStep = ride_order_steps[next_step_key]
    buttons = []
    if next_step_key == "date":
        buttons = generate_date_buttons(
            "order_answer|date|",
        )
    elif next_step_key == "time":
        buttons = generate_time_buttons(
            "order_answer|time|",
            for_date=state.value["order_data"]["date"],
        )
    buttons += [
        [prev_question_button],
        user.loc.cancel_btn,
    ]
    await state.save()
    await event.respond(
        next_step_data.get_text(user),
        buttons=buttons,
    )


@msg_payload_handler(UserPayload.waiting_for_payment_confirmation)
async def waiting_for_payment_confirmation_handler(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    message: patched.Message = event.message
    if not (
            message.photo
            or (message.document and message.document.mime_type.startswith("image/"))
    ):
        await event.respond(user.loc.drivers_please_send_a_valid_image_text)
        return

    rid = state.value["ride_id"]
    ride = await database.Ride.get(id=rid)
    await shared.riders_bot.send_message(
        shared.config.owner_id,
        f"New ride payment from {bot_utils.get_max_user_info(await event.get_sender())}\n"
        f"Ride info:\n{await ride.admin_info_initial()}",
        file=message.media,
        buttons=[
            Button.inline(
                "✅ Accept",
                data=f"accept_ride_payment|{ride.id}|{message.id}",
            ),
            Button.inline(
                "❌ Reject",
                data=f"reject_ride_payment|{ride.id}|{message.id}",
            ),
        ],
    )
    state.payload = ""
    state.value = {}
    await state.save()
    await event.respond(user.loc.riders_thanks_for_payment_text)


@msg_payload_handler(UserPayload.feedback_comment)
async def feedback_comment_handler(
        event: events.NewMessage.Event,
        user: database.User,
        is_new_user: bool,
        state: database.UserState,
):
    message: patched.Message = event.message
    ride_id = state.value["feedback_ride_id"]
    ride = await database.Ride.get(id=ride_id)
    rating = state.value["feedback_rating"]
    await database.Review.create(
        stars=rating,
        text=message.text or "",
        from_user=user,
        to_user=await (await ride.driver).user,
        ride=ride,
        by_driver=False,
    )
    asyncio.create_task(event.client.delete_messages(event.chat_id, state.value["feedback_delete_msg"]))
    state.payload = ""
    state.value = {}
    await state.save()
    await event.respond(user.loc.thanks_for_feedback_text)


async def message_handler(event: events.NewMessage.Event):
    global user_payload_binds, commands_binds
    user, is_new_user = await database.User.get_or_create(user_id=event.sender_id)
    asyncio.create_task(user.mb_update_data(event.message.get_sender()))
    if user.blocked:
        await event.respond(user.loc.you_are_blocked)
        raise events.StopPropagation
    if is_new_user:
        user_entity: types.User = await event.client.get_entity(event.sender_id)
        if user_entity.lang_code in locales.locales:
            logger.debug(
                f"Setting language for {user.user_id} to {user_entity.lang_code} - thanks telegram!"
            )
            user.lang_code = user_entity.lang_code
            await user.save()
    bot_id = await event.client.get_peer_id("me")
    state, _ = await database.UserState.get_or_create(user=user, bot_id=bot_id)
    text = event.raw_text
    logger.debug(
        f"Text query [u {user.user_id}] {{{state}}}: {text or type(event.message.media)}"
    )
    if text.startswith("/"):
        command = text.split(" ")[0][1:].split("@")[0]
        if command in commands_binds:
            if (
                    commands_binds[command]["owner_only"]
                    and user.user_id != shared.config.owner_id
            ):
                logger.info(f"User {user.user_id} tried to use admin command {command}")
                return
            try:
                await commands_binds[command]["f"](event, user, is_new_user, state)
            except Exception as e:
                logger.exception(e)
                await event.respond(user.loc.an_error_occurred)
        else:
            if not state.payload:
                logger.warning(f"Unknown command: {command}")
                await event.respond(user.loc.unknown_command)
    else:
        if state.payload:
            if state.payload in user_payload_binds:
                try:
                    await user_payload_binds[state.payload]["f"](
                        event, user, is_new_user, state
                    )
                except Exception as e:
                    logger.exception(e)
                    await event.respond(user.loc.an_error_occurred)
            else:
                logger.error(f"Unknown payload: {state.payload}")
                await event.respond(user.loc.unknown_payload)


async def set_commands(bot: TelegramClient):
    global commands_binds
    commands = {
        "en": [],
        "hi": [],
        "kn": [],
    }
    owner_only_commands = {
        "en": [],
        "hi": [],
        "kn": [],
    }

    for command, data in commands_binds.items():
        if not data["set"]:
            continue
        if data["d_en"]:
            owner_only_commands["en"].append(
                types.BotCommand(
                    command=command,
                    description=data["d_en"],
                )
            )
        if data["d_hi"]:
            owner_only_commands["hi"].append(
                types.BotCommand(
                    command=command,
                    description=data["d_hi"],
                )
            )
        if data["d_kn"]:
            owner_only_commands["kn"].append(
                types.BotCommand(
                    command=command,
                    description=data["d_kn"],
                )
            )
        if not data["owner_only"]:
            if data["d_en"]:
                commands["en"].append(
                    types.BotCommand(
                        command=command,
                        description=data["d_en"],
                    )
                )
            if data["d_hi"]:
                commands["hi"].append(
                    types.BotCommand(
                        command=command,
                        description=data["d_hi"],
                    )
                )
            if data["d_kn"]:
                commands["kn"].append(
                    types.BotCommand(
                        command=command,
                        description=data["d_kn"],
                    )
                )

    async def set_cmds(lc, com, scope, message):
        try:
            await bot(
                functions.bots.SetBotCommandsRequest(
                    commands=com,
                    scope=scope,
                    lang_code=lc,
                )
            )
        except Exception as e:
            logger.exception(e)
        logger.info(message)

    for lang_code, cmds in commands.items():
        if not cmds:
            continue
        asyncio.create_task(
            set_cmds(
                lang_code,
                cmds,
                types.BotCommandScopeUsers(),
                f"Set {len(cmds)} commands for {lang_code}",
            )
        )

    try:
        owner_peer = await bot.get_input_entity(shared.config.owner_id)
    except ValueError:
        logger.warning("Owner peer not found")
        return
    for lang_code, cmds in owner_only_commands.items():
        if not cmds:
            continue
        asyncio.create_task(
            set_cmds(
                lang_code,
                cmds,
                types.BotCommandScopePeer(peer=owner_peer),
                f"Set {len(cmds)} owner only commands for {lang_code}",
            )
        )


async def init_msg(bot: TelegramClient, parent_logger=None):
    global logger
    if parent_logger:
        logger = parent_logger.getChild("messages")
    logger.info("Setting up messages handler")
    bot.add_event_handler(message_handler, events.NewMessage(func=lambda e: e.is_private))
    logger.info("Setting up commands")
    await set_commands(bot)
    logger.info("Messages handler setup complete")
