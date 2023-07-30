import time
import typing

import pytz

from ... import database, common, shared, bot_utils, constants
from .messages import (
    ride_order_steps,
    office_commute_order_steps,
    two_way_order_steps,
    UserPayload,
    intracity_order_steps
)
from .helper import generate_date_buttons, generate_time_buttons, date_handler, time_handler, fetch_categories, \
    cost_calculators
from telethon import TelegramClient, events, Button, types, utils, functions
from telethon.errors import rpcerrorlist
from telethon.tl import patched
import logging
import datetime
import tempfile
import asyncio

logger = logging.getLogger("riders.callbacks")
callback_data_binds = {}
categories_buttons = []


def cb_handler(data: str):
    def decorator(
            func: typing.Callable[
                [events.CallbackQuery.Event, str, database.User], typing.Awaitable[None]
            ]
    ):
        global callback_data_binds
        callback_data_binds[data] = {"f": func}
        return func

    return decorator


@cb_handler("start")
async def cb_start_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    if "clear" in data:
        state = await user.get_state(await event.client.get_peer_id("me"))
        state.payload = ""
        state.value = {}
        await state.save()
    await event.edit(
        user.loc.riders_welcome_text.format(name=user.full_name),
        buttons=user.loc.riders_start_order_button,
    )


@cb_handler("lang")
async def cb_lang_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    user.lang_code = data.split("|")[1]
    await user.save()
    await cb_start_handler(event, data, user)


@cb_handler("start_order")
async def cb_choose_booking_type(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    await event.edit(
        user.loc.riders_please_select_booking_type_text,
        buttons=user.loc.riders_booking_type_btns,
    )


@cb_handler("drop_time")
async def drop_time_commute(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    question_key, answer = data.split("|")[1:]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["stack"].append(data)
    if question_key == "date":
        state_key = "order_data"
        await date_handler(state, answer, state_key)
        await event.edit(
            user.loc.rider_enter_picktime_for_commute + ride_order_steps["time"].get_text(user),
            buttons=generate_time_buttons(
                "drop_time|time|", for_date=state.value[state_key]["date"]
            )
                    + [user.loc.prev_question_button, user.loc.cancel_btn],
        )
        return
    elif question_key == "time":
        state_key = "order_data"
        await time_handler(user, event, state, answer, state_key)
        await event.edit(
            user.loc.rider_enter_droptime_for_commute + ride_order_steps["time"].get_text(user),
            buttons=generate_time_buttons(
                "office_commute_dt|time|", for_date=state.value["order_data"]["date"],
                from_time=state.value["order_data"]["time"]
            )
                    + [user.loc.prev_question_button, user.loc.cancel_btn],
        )
        return


@cb_handler("office_commute_dt")
async def cb_office_commute_dt(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["stack"].append(data)
    question_key, answer = data.split("|")[1:]
    hours, minutes = answer.split(":")
    hours = int(hours)
    minutes = int(minutes)
    new_date = state.value["order_data"]["date"] + datetime.timedelta(
        hours=hours, minutes=minutes
    )
    min_today = datetime.datetime.now(tz=common.tz).replace(second=0, microsecond=0)
    if new_date < min_today:
        await event.respond(user.loc.riders_please_provide_time_in_future_text)
        return
    state.value["commute_info"]["drop_time"] = new_date
    ride_steps_keys = list(ride_order_steps.keys())

    next_step_key = ride_steps_keys[ride_steps_keys.index(question_key) + 1]
    state.value["order_step"] = next_step_key
    state.payload = UserPayload.ride_step

    await state.save()
    next_step_data: common.QuestionStep = ride_order_steps[next_step_key]
    buttons = []
    buttons += [user.loc.prev_question_button, user.loc.cancel_btn]
    await event.edit(next_step_data.get_text(user), buttons=buttons, )


@cb_handler("office_commute")
async def cb_commuteDays(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    end = data.split('|')[-1]
    state = await user.get_state(await event.client.get_peer_id("me"))
    if 'd' in end:
        # no_of_rides has been changed to number of days(7,15,30) but the identifier has not been changed everywhere
        state.value["commute_info"] = {"no_of_rides": end, "days_of_week": []}
    elif end == 'Date':
        state.value["stack"].append(data)
        await state.save()
        first_question_key, first_question = list(ride_order_steps.items())[0]
        await event.edit("Enter the date to **start from**" +
                         first_question.get_text(user),
                         buttons=generate_date_buttons(
                             "drop_time|date|", days_ahead_from_today=1
                         )
                                 + [user.loc.prev_question_button, user.loc.cancel_btn],
                         )
        return
    else:
        if end in state.value["commute_info"]["days_of_week"]:
            state.value["commute_info"]["days_of_week"].remove(end)
        else:
            state.value["commute_info"]["days_of_week"].append(end)
    await state.save()
    i = 0
    btns = []
    for day in range(7):
        btns.append(
            Button.inline(
                (
                    "➕ "
                    if str(day) not in state.value["commute_info"]["days_of_week"]
                    else "☑ "
                )
                + user.loc.days[day],
                data=f"office_commute|days_of_week|" + str(i),
            )
        )
        i += 1
    if len(state.value["commute_info"]["days_of_week"]) > 0:
        btns.append(
            Button.inline(
                "✅ Finish",
                data="office_commute|Date",
            )
        )
    else:
        btns += user.loc.cancel_btn
    btns = [btns[:4], btns[4:]]
    print(btns)
    await event.edit(user.loc.riders_enter_commute_days, buttons=btns)


@cb_handler("cabcategory")
async def cb_start_order_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    booking_type = int(data.split("|")[1])
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value = {
        "order_data": {
            "category": None,
            "booking_type": booking_type,
        },
        "order_step": None,
        "stack": [data],
    }
    await state.save()
    buttons = categories_buttons
    description_of_chosen_booking_type = ''
    if booking_type == 0:
        description_of_chosen_booking_type = user.loc.description[0]
    elif booking_type == 1:
        description_of_chosen_booking_type = user.loc.description[1]
    elif booking_type == 2:
        buttons = [buttons[0]]
        description_of_chosen_booking_type = user.loc.description[4]
    elif booking_type == 3:
        description_of_chosen_booking_type = user.loc.description[5]
    elif booking_type == 4:
        description_of_chosen_booking_type = user.loc.description[3]
    elif booking_type == 5:
        description_of_chosen_booking_type = user.loc.description[2]

    buttons = [buttons, [Button.inline(user.loc.cancel_btntext, data="start|clear")]]
    await event.edit(description_of_chosen_booking_type +
                     user.loc.riders_please_select_category_text,
                     buttons=buttons,
                     )


@cb_handler("first_trip")
async def cb_first_trip_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    question_key, answer = data.split("|")[1:]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["stack"].append(data)
    if question_key == "date":
        await date_handler(state, answer, state_key="order_data")
        await event.edit(user.loc.rider_enter_picktime_for_commute + ride_order_steps["time"].get_text(user),
                         buttons=generate_time_buttons(
                             "first_trip|time|",
                             for_date=state.value["order_data"]["date"],
                         ) + [user.loc.prev_question_button, user.loc.cancel_btn])
    elif question_key == "time":
        await time_handler(user, event, state, answer, state_key="order_data")
        first_question_key, first_question = list(ride_order_steps.items())[0]
        await event.edit(user.loc.rider_enter_droptime_for_commute +
                         first_question.get_text(user),
                         buttons=generate_date_buttons(
                             "round_trip|date|",
                         )
                                 + [user.loc.prev_question_button, user.loc.cancel_btn],
                         )


@cb_handler("round_trip")
async def cb_round_trip_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    question_key, answer = data.split("|")[1:]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["stack"].append(data)
    if question_key == "date":
        state.value["round_trip"] = {question_key: ""}
        await date_handler(state, answer, state_key="round_trip")
    elif question_key == "time":
        await time_handler(user, event, state, answer, state_key="round_trip")
    else:
        state.value["order_data"][question_key] = answer

    ride_steps_keys = list(
        ride_order_steps.keys())  #
    is_last = question_key == ride_steps_keys[-1]

    if is_last:
        # it actually won't be here as last, that is only used for date and time.
        raise NotImplementedError

    next_step_key = ride_steps_keys[ride_steps_keys.index(question_key) + 1]
    state.value["order_step"] = next_step_key
    next_step_data: common.QuestionStep = ride_order_steps[next_step_key]
    buttons = []
    d = ''
    if next_step_key == "date":
        buttons = generate_date_buttons(
            "round_trip|date|",
        )
    elif next_step_key == "time":
        d = "Enter time for **return journey**"
        buttons = generate_time_buttons(
            "round_trip|time|",
            for_date=state.value["order_data"]["date"],
        )
    buttons += [user.loc.prev_question_button, user.loc.cancel_btn]
    state.payload = UserPayload.ride_step  # TODO CHANGE
    await state.save()
    await event.edit(d +
                     next_step_data.get_text(user),
                     buttons=buttons,
                     )


@cb_handler("order_category")
async def cb_order_category_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    category = data.split("|")[1]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["stack"].append(data)
    booking_type = state.value["order_data"]["booking_type"]
    if booking_type == 1:
        first_question_key, first_question = list(two_way_order_steps.items())[0]

        state.value["order_data"]["category"] = int(category)
        state.value["order_step"] = first_question_key
        state.payload = UserPayload.two_way_step
        await state.save()
        await event.edit(user.loc.rider_enter_picktime_for_commute + ride_order_steps["date"].get_text(user),
                         buttons=generate_date_buttons("first_trip|date|") + [user.loc.prev_question_button,
                                                                              user.loc.cancel_btn])
    elif booking_type == 2:
        first_question_key, first_question = list(office_commute_order_steps.items())[0]
        state.value["order_data"]["category"] = int(category)
        state.value["order_step"] = first_question_key
        state.payload = UserPayload.office_commute_step

        await state.save()
        btns = [[Button.inline("7 days", data="office_commute|7d"),
                 Button.inline("15 days", data="office_commute|15d"),
                 Button.inline("30 days", data="office_commute|30d")],
                user.loc.cancel_btn]
        await event.edit(
            user.loc.riders_enter_commute_days,
            buttons=btns,
        )
    elif booking_type == 3:
        first_question_key, first_question = list(intracity_order_steps.items())[0]
        state.value["order_data"]["category"] = int(category)
        state.value["order_step"] = first_question_key
        state.payload = UserPayload.intracity

        await state.save()
        btns = user.loc.hours_buttons_for_intracity
        await event.edit(
            user.loc.enter_no_of_hours,
            buttons=btns,
        )
    else:
        first_question_key, first_question = list(ride_order_steps.items())[0]
        state.value["order_data"]["category"] = int(category)
        state.value["order_step"] = first_question_key
        state.payload = UserPayload.ride_step
        await state.save()
        await event.edit(
            first_question.get_text(user),
            buttons=generate_date_buttons(
                "order_answer|date|",
            )
                    + [user.loc.prev_question_button, user.loc.cancel_btn],
        )


@cb_handler("intracity")
async def intracity_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    # todo
    question_key, answer = data.split("|")[1:]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["stack"].append(data)
    if question_key == 'hours':
        state.value["order_data"]["time_seconds"] = int(answer)
        state.value["order_step"] = 'date'
        next_step_key = 'date'
        await state.save()
        buttons = generate_date_buttons(data_prefix="intracity|date|") + [user.loc.prev_question_button]
    elif question_key == 'date':
        state.value["order_step"] = 'time'
        next_step_key = 'time'
        await date_handler(state, answer, state_key='order_data')
        buttons = generate_time_buttons("intracity|time|", for_date=state.value['order_data']["date"]) + [
            user.loc.prev_question_button]
    elif question_key == 'time':
        await time_handler(user, event, state, answer, 'order_data')

        category = await database.CabCategory.get(
            id=state.value["order_data"]["category"]
        )
        hours = state.value['order_data']['time_seconds']
        state.value['order_data']['time_seconds'] = hours*3600
        price = await cost_calculators(seater=category.id, booking_type=3, distance_meters_or_hours=hours * 1000, )
        dt = state.value["order_data"]["time"]
        state.value["order_data"]["from"] = \
            state.value["order_data"]["to"] = {'from': "", 'lat': '0', 'lon': '0', 'text': ""}
        state.value["order_data"]["price"] = round(price / 100.0, 2)
        state.value["order_data"]["distance_meters"] = hours * 10000
        state.value["order_data"]["full_name"] = user.full_name
        state.value["order_data"]["phone"] = user.phone_number
        await state.save()
        await event.edit(
            user.loc.riders_ride_data_preview_text.format(
                datetime=dt.strftime("%d.%m.%Y %H:%M"),
                full_name=state.value["order_data"]["full_name"],
                phone_number=state.value["order_data"]["phone"],
                distance=str(hours*10),
                duration=str(hours) + ' hours',
                price=state.value["order_data"]["price"],
                category=category.name + ' | IntraCity',
            ),
            buttons=[
                [
                    Button.inline(
                        user.loc.riders_confirm_order_btntext, data="confirm_order"
                    )
                ],
                user.loc.prev_question_button,
                [Button.inline(user.loc.cancel_btntext, data="start|clear")],
            ],
        )
        return
    next_step_data: common.QuestionStep = ride_order_steps[next_step_key]
    await event.edit(
        next_step_data.get_text(user),
        buttons=buttons + [user.loc.cancel_btn],
    )


@cb_handler("order_answer")
async def cb_order_answer_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    question_key, answer = data.split("|")[1:]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["stack"].append(data)
    state_key = 'order_data'
    if question_key == "date":
        await date_handler(state, answer, state_key)
    elif question_key == "time":
        await time_handler(user, event, state, answer, state_key)

    ride_steps_keys = list(ride_order_steps.keys())
    is_last = question_key == ride_steps_keys[-1]

    if is_last:
        # it actually won't be here as last, that is only used for date and time.
        raise NotImplementedError

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
    buttons += [user.loc.prev_question_button, user.loc.cancel_btn]

    await state.save()
    await event.edit(
        next_step_data.get_text(user),
        buttons=buttons,
    )


@cb_handler("order_goto_step")
async def cb_order_goto_step_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    state = await user.get_state(await event.client.get_peer_id("me"))
    stack = state.value["stack"]
    stack.pop()
    data = stack.pop()
    state.value["stack"] = stack
    await state.save()
    data_payload = data.split('|')[0]
    await callback_data_binds[data_payload]["f"](event, data, user)


@cb_handler("order_goto_step_for_message")
async def cb_order_goto_step_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    state = await user.get_state(await event.client.get_peer_id("me"))
    question_key = data.split("|")[1]
    question = ride_order_steps[question_key]
    state.payload = UserPayload.ride_step
    state.value["order_step"] = question_key
    await state.save()
    order_steps_keys = list(ride_order_steps.keys())
    is_first = question_key == order_steps_keys[0]

    buttons = []
    """
    if question_key == "date":
        buttons = generate_date_buttons(
            "order_answer|date|",
        )
    elif question_key == "time":
        buttons = generate_time_buttons(
            "order_answer|time|",
            for_date=state.value["order_data"]["date"],
        )
    

    if not is_first:
        buttons.append(
            [
                Button.inline(
                    user.loc.prev_step_btntext,
                    data=f"order_goto_step_for_message|"
                         + order_steps_keys[order_steps_keys.index(question_key) - 1],
                )
            ]
        )
    """
    buttons.append([Button.inline(user.loc.cancel_btntext, data="start|clear")])

    await event.edit(
        question.get_text(user),
        buttons=buttons,
    )


@cb_handler("confirm_order")
async def cb_confirm_order_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    state = await user.get_state(await event.client.get_peer_id("me"))
    return_time_scheduled, days_of_office_commute = None, ""
    booking_type = state.value["order_data"]["booking_type"]
    if booking_type == 1:
        return_time_scheduled = state.value["round_trip"]['time']
    elif booking_type == 2:
        return_time_scheduled = state.value["commute_info"]['drop_time']
        days_of_office_commute = state.value["commute_info"]['days_of_week']
        days_of_office_commute = "|".join(days_of_office_commute)
        days_of_office_commute = days_of_office_commute + '|' + state.value["commute_info"]["no_of_rides"][:-1]

    created_ride = await database.Ride.create(
        user=user,
        category=await database.CabCategory.get(
            id=state.value["order_data"]["category"]
        ),
        booking_type=booking_type,
        from_lat=state.value["order_data"]["from"]["lat"],
        from_lon=state.value["order_data"]["from"]["lon"],
        to_lat=state.value["order_data"]["to"]["lat"],
        to_lon=state.value["order_data"]["to"]["lon"],
        from_text_address=state.value["order_data"]["from"]["text"],
        to_text_address=state.value["order_data"]["to"]["text"],
        pickup_time_scheduled=state.value["order_data"]["time"],
        cost=state.value["order_data"]["price"],
        distance=state.value["order_data"]["distance_meters"],
        duration=state.value["order_data"]["time_seconds"],
        phone_number=state.value["order_data"]["phone"],
        full_name=state.value["order_data"]["full_name"],
        return_time_scheduled=return_time_scheduled,
        days_of_office_commute=days_of_office_commute,
        # status is "created" by default
    )

    if booking_type == 2:
        return_ride = await database.Ride.create(
            user=user,
            category=await database.CabCategory.get(
                id=state.value["order_data"]["category"]
            ),
            booking_type=booking_type,
            from_lat=state.value["order_data"]["to"]["lat"],
            from_lon=state.value["order_data"]["to"]["lon"],
            to_lat=state.value["order_data"]["from"]["lat"],
            to_lon=state.value["order_data"]["from"]["lon"],
            from_text_address=state.value["order_data"]["to"]["text"],
            to_text_address=state.value["order_data"]["from"]["text"],
            pickup_time_scheduled=state.value["commute_info"]['drop_time'],
            cost=state.value["order_data"]["price"],
            distance=state.value["order_data"]["distance_meters"],
            duration=state.value["order_data"]["time_seconds"],
            phone_number=state.value["order_data"]["phone"],
            full_name=state.value["order_data"]["full_name"],
            return_time_scheduled=state.value["order_data"]["time"],
            days_of_office_commute=days_of_office_commute,
            first_ride_id=created_ride.id
            # status is "created" by default
        )
    created_ride.first_ride_id = created_ride.id
    await created_ride.save()
    await event.edit(buttons=None)
    state.payload = ""
    state.value = {}
    await shared.drivers_bot.send_message(shared.config.driver_group_id,
                                          " New PlanCab booking might come soon 😁, please be ready!")
    await state.save()
    enough_referral_points = await database.ReferralPoint.can_redeem_x_points(
        user, constants.Constants.referrals_for_free_ride
    )
    if not enough_referral_points:
        await event.respond(
            user.loc.riders_please_pay_for_reservation_text,
            buttons=Button.inline(
                user.loc.riders_pay_btntext, data=f"start_pay|{created_ride.id}"
            ),
        )
        return
    await event.respond(
        user.loc.riders_please_pay_for_reservation_text
        + user.loc.riders_you_can_pay_with_referral_add_text,
        buttons=[
            [
                Button.inline(
                    user.loc.riders_pay_btntext, data=f"start_pay|{created_ride.id}"
                )
            ],
            [
                Button.inline(
                    user.loc.riders_pay_with_referral_btntext,
                    data=f"pay_with_referral|{created_ride.id}",
                )
            ],
        ],
    )


@cb_handler("start_pay")
async def cb_start_pay_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    asyncio.create_task(event.delete())
    ride_id = data.split("|")[1]

    with tempfile.TemporaryFile(suffix=".png") as f:
        uri = bot_utils.build_url(
            "upi://pay",
            {
                "pa": shared.config.upi_id,
                "pn": shared.config.upi_name,
                "am": constants.Constants.ride_order_cost,
                "cu": "INR",
                "tn": f"Ride-{ride_id}",
            },
        )
        bot_utils.write_qr_code(uri, f)
        f.seek(0)

        uploaded = await shared.riders_bot.upload_file(
            f,
            file_name="qr.png",
        )
        await shared.riders_bot.send_file(
            user.user_id,
            caption=user.loc.riders_here_is_payment_qr_text,
            file=uploaded,
            attributes=[types.DocumentAttributeFilename("qr.png")],
            buttons=Button.inline(
                user.loc.riders_payed_btntext, data=f"check_payment|{ride_id}"
            ),
        )


@cb_handler("check_payment")
async def cb_check_payment_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    asyncio.create_task(
        bot_utils.send_user_to_privacy_share_group(event.client, event.get_sender())
    )
    asyncio.create_task(event.delete())
    ride_id = data.split("|")[1]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = UserPayload.waiting_for_payment_confirmation
    state.value = {"ride_id": ride_id}
    await state.save()
    await event.respond(user.loc.riders_please_send_screen_of_payment_text)


@cb_handler("reject_ride_payment")
async def cb_reject_ride_payment_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    ride_id, reply_to_msg_id = (int(x) for x in data.split("|")[1:])
    ride = await database.Ride.get(id=ride_id)
    ride.status = database.RideStatus.PAYMENT_FAILED
    await ride.save()
    await event.edit(buttons=None)
    await event.reply("Payment rejected")
    await shared.riders_bot.send_message(
        ride.user_id,
        user.loc.riders_payment_rejected_text,
        reply_to=reply_to_msg_id,
    )


@cb_handler("accept_ride_payment")
async def cb_accept_ride_payment_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    ride_id, reply_to_msg_id = (int(x) for x in data.split("|")[1:])
    ride = await database.Ride.get(id=ride_id)
    ride.status = database.RideStatus.PAID_BY_USER
    await ride.save()
    await event.edit(buttons=None)
    await event.reply("Payment accepted")

    group_message = await shared.drivers_bot.send_message(
        shared.config.driver_group_id,
        await ride.message_for_drivers_group(),
        buttons=Button.inline(
            "Accept",
            data=f"accept_ride|{ride.id}",
        ),
    )
    ride.group_message_id = group_message.id
    ride.status = database.RideStatus.SENT_TO_DRIVERS
    await ride.save()
    await shared.riders_bot.send_message(
        (await ride.user).user_id,
        user.loc.riders_payment_accepted_text.format(drive_id=ride.id),
        reply_to=reply_to_msg_id,
    )


@cb_handler("pay_with_referral")
async def cb_pay_with_referral_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    await database.ReferralPoint.redeem_x_points(
        user, constants.Constants.referrals_for_free_ride
    )
    ride_id = data.split("|")[1]
    ride = await database.Ride.get(id=ride_id)
    group_message = await shared.drivers_bot.send_message(
        shared.config.driver_group_id,
        await ride.message_for_drivers_group(),
        buttons=Button.inline(
            "Accept",
            data=f"accept_ride|{ride.id}",
        ),
    )
    ride.group_message_id = group_message.id
    ride.status = database.RideStatus.SENT_TO_DRIVERS
    await ride.save()
    await event.edit(buttons=None)
    await event.reply(user.loc.riders_payment_accepted_text.format(drive_id=ride.id))


@cb_handler("alert")
async def cb_alert_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    await event.answer(
        user.loc.drive_should_have_started_mb_alert_sent_text, alert=True
    )
    await event.edit(buttons=None)
    ride = await database.Ride.get(id=int(data.split("|")[1]))
    await shared.drivers_bot.send_message(
        shared.config.owner_id,
        f"User `{user.user_id}` has sent an alert for ride `{ride.id}`!\n\nRide info:\n"
        f"{await ride.full_admin_info()}",
    )


@cb_handler("no_feedback")
async def cb_no_feedback_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    await event.edit(buttons=None)


@cb_handler("feedback")
async def cb_feedback_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    await event.edit(buttons=None)
    ride_id = int(data.split("|")[1])
    await event.reply(
        user.loc.please_select_rating_text,
        buttons=[
            [
                Button.inline("⭐️", data=f"feedback_rating|{ride_id}|1"),
                Button.inline("⭐️⭐️", data=f"feedback_rating|{ride_id}|2"),
            ],
            [
                Button.inline("⭐️⭐️⭐️", data=f"feedback_rating|{ride_id}|3"),
                Button.inline("⭐️⭐️⭐️⭐️", data=f"feedback_rating|{ride_id}|4"),
            ],
            [Button.inline("⭐️⭐️⭐️⭐️⭐️", data=f"feedback_rating|{ride_id}|5")],
        ],
    )


@cb_handler("feedback_rating")
async def cb_feedback_rating_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    ride_id = int(data.split("|")[1])
    rating = int(data.split("|")[2])
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["feedback_rating"] = rating
    state.value["feedback_ride_id"] = ride_id
    state.value["feedback_delete_msg"] = event.message_id
    state.payload = UserPayload.feedback_comment
    await state.save()
    await event.edit(
        user.loc.please_send_comment_text,
        buttons=Button.inline(
            user.loc.skip_btntext, data=f"skip_feedback_comment|{ride_id}|{rating}"
        ),
    )


@cb_handler("skip_feedback_comment")
async def cb_skip_feedback_comment_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    ride_id = int(data.split("|")[1])
    ride = await database.Ride.get(id=ride_id)

    rating = int(data.split("|")[2])
    await database.Review.create(
        stars=rating,
        text="",
        from_user=user,
        to_user=await (await ride.driver).user,
        ride=ride,
        by_driver=False,
    )
    await event.edit(user.loc.thanks_for_feedback_text, buttons=None)


async def cb_main_handler(event: events.CallbackQuery.Event):
    global callback_data_binds
    user, _ = await database.User.get_or_create(user_id=event.sender_id)
    asyncio.create_task(user.mb_update_data(event.get_sender()))
    if user.blocked:
        await event.respond(user.loc.you_are_blocked)
        raise events.StopPropagation
    data = event.data.decode("utf-8")
    data_payload = data.split("|")[0]

    # I want to patch event.edit to auto-do event.send_message on "errors.rpcerrorlist.MessageIdInvalidError", because
    # this error occurs when the message is too old to be edited, and I want to send a new message instead of editing.
    # it is easier to patch the event.edit function than to implement it in the code

    original_edit = event.edit

    async def edit_wrapper(*args, **kwargs):
        try:
            await original_edit(*args, **kwargs)
        except rpcerrorlist.MessageIdInvalidError:
            await event.respond(*args, **kwargs)

    event.edit = edit_wrapper

    if data_payload in callback_data_binds:
        try:
            state = await user.get_state(await event.client.get_peer_id("me"))
            print(state.value)
            logger.debug(f"Call query [u {user.user_id}]: {data}")
            await callback_data_binds[data_payload]["f"](event, data, user)
        except events.StopPropagation:
            pass
        except Exception as e:
            logger.exception(e)
            # noinspection PyProtectedMember
            if event._answered:
                await event.reply(user.loc.an_error_occurred)
            else:
                await event.answer(user.loc.an_error_occurred)
    else:
        await event.answer(user.loc.an_error_occurred)
        logger.error(f"Unknown callback query: {data}")


async def init_cb(bot: TelegramClient, parent_logger=None):
    global logger
    if parent_logger:
        logger = parent_logger.getChild("callbacks")
    global categories_buttons
    categories_buttons = await fetch_categories()
    bot.add_event_handler(cb_main_handler, events.CallbackQuery())
    logger.info("Set up callback handler")
