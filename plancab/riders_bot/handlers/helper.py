import datetime
from ... import database, common, bot_utils
from telethon import Button, types
import copy
from ... import constants


# used in messages.py and callbacks.py

def generate_date_buttons(data_prefix: str, amount_of_days=15, per_row=3, days_ahead_from_today=0):
    if amount_of_days < 1:
        raise ValueError("amount_of_days must be greater than 0")
    if per_row < 1:
        raise ValueError("per_row must be greater than 0")
    buttons = [[]]
    amount_of_days += days_ahead_from_today
    for i in range(days_ahead_from_today, amount_of_days):
        if len(buttons[-1]) >= per_row:
            buttons.append([])
        dt = datetime.datetime.now(tz=common.tz) + datetime.timedelta(days=i)
        buttons[-1].append(
            Button.inline(
                dt.strftime("%d.%m"),
                data_prefix + dt.strftime("%d.%m.%Y"),
            )
        )
    if len(buttons[-1]) == 0:
        buttons.pop()
    return buttons


def generate_time_buttons(
        data_prefix: str,
        for_date: datetime.datetime,
        per_row=4,
        max_amount=48,
        interval_seconds=30 * 60,
        from_time: datetime.time = None
):
    """
    2 Cases:
    if date is from future - next day - all 24 from 00:00 to 23:30 will be available.
    if date is today - only available times will be shown.

    Aside from date __right now (which will show as it is)__
    all times should be :30 and :00, so current minute will be omitted
    Note: using from_time will cause conflict if for_date == datetime.today().date()
    """
    for_date_inner = copy.copy(for_date)  # so we don't modify the original

    if per_row < 1:
        raise ValueError("per_row must be greater than 0")
    if max_amount < 1:
        raise ValueError("max_amount must be greater than 0")

    buttons = [[]]
    now = datetime.datetime.now(tz=common.tz)
    if (for_date_inner.date() == now.date()):
        buttons[-1].append(
            Button.inline(
                (now + datetime.timedelta(hours=1)).strftime("%H:%M"),
                data_prefix + (now + datetime.timedelta(hours=1)).strftime("%H:%M"), #todo : hours changed to 1 from 3
            )
        )
        if now.minute < 30:
            now = now.replace(minute=30) + datetime.timedelta(hours=1)
        else:
            now = now.replace(minute=0) + datetime.timedelta(hours=2)

        # now add the rest of the times
        for i in range(max_amount):
            if len(buttons[-1]) >= per_row:
                buttons.append([])
            buttons[-1].append(
                Button.inline(
                    now.strftime("%H:%M"),
                    data_prefix + now.strftime("%H:%M"),
                )
            )
            now += datetime.timedelta(seconds=interval_seconds)
            if now.date() != for_date_inner.date():
                break
    elif from_time:
        for i in range(max_amount):
            if len(buttons[-1]) >= per_row:
                buttons.append([])
            time = from_time.strftime("%H:%M")
            buttons[-1].append(
                Button.inline(
                    time,
                    data_prefix + time,
                )
            )
            from_time += datetime.timedelta(seconds=interval_seconds)
            if time == '23:30':
                break
    else:
        # future
        for_date_inner = for_date_inner.replace(hour=0, minute=0)
        for i in range(max_amount):
            if len(buttons[-1]) >= per_row:
                buttons.append([])
            buttons[-1].append(
                Button.inline(
                    for_date_inner.strftime("%H:%M"),
                    data_prefix + for_date_inner.strftime("%H:%M"),
                )
            )
            for_date_inner += datetime.timedelta(seconds=interval_seconds)
    if len(buttons[-1]) == 0:
        buttons.pop()
    return buttons


async def date_text_handler(
        event,
        message,
        user: database.User,
        state: database.UserState,
        state_key,
):
    formats_to_try = [
        "%d.%m.%Y",
        "%d.%m.%y",
        "%d.%m",
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d/%m",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%d-%m",
        "%d %m %Y",
        "%d %m %y",
        "%d %m",
    ]
    for date_format in formats_to_try:
        try:
            date = datetime.datetime.strptime(message.text, date_format)
            # set timezone to IST
            date = common.tz.localize(date)
            break
        except ValueError:
            pass
    else:
        await event.respond(user.loc.riders_answer_incorrect_format_text)
        return 1
    min_today = datetime.datetime.now(tz=common.tz).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if date.year < 2000:  # most likely year is missing
        date = date.replace(year=min_today.year)
    if date.replace(hour=23, minute=59, second=59, microsecond=999) < min_today:
        await event.respond(user.loc.riders_please_provide_date_in_future_text)
        return 1
    state.value[state_key]["date"] = date


# used in messages.py
async def time_text_handler(
        event,
        message,
        user: database.User,
        state: database.UserState,
        state_key,
):
    hours, minutes = message.text.split(":")
    hours = int(hours)
    minutes = int(minutes)
    new_date = state.value[state_key]["date"] + datetime.timedelta(
        hours=hours, minutes=minutes
    )
    min_today = datetime.datetime.now(tz=common.tz).replace(
        second=0, microsecond=0
    )
    if new_date < min_today:
        await event.respond(user.loc.riders_please_provide_time_in_future_text)
        return 1
    state.value[state_key]["time"] = new_date


async def address_text_handler(
        event,
        question_key,
        message,
        user: database.User,
        state: database.UserState,
):
    try:
        lat, lon = await bot_utils.get_coords_by_text_address(message.text)
    except bot_utils.ExceptionWillReturnToUser as e:
        if e.code == "ZERO_RESULTS":
            await event.respond(
                user.loc.place_not_found_please_specify_better_text,
            )
            return 1
        elif e.code == "NOT_FOUND":
            await event.respond(
                user.loc.place_not_found_please_specify_better_text,
            )
            return 1
        else:
            raise e
    await event.respond(
        file=types.MessageMediaGeo(
            geo=types.GeoPoint(
                lat=lat,
                long=lon,
                access_hash=0,
            ),
        ),
    )

    address = await bot_utils.get_text_address_by_coords(lat, lon)
    if question_key == "from":
        await event.respond(
            user.loc.please_validate_departure_place_text.format(
                departure=address
            )
        )
        state.value["order_data"]["departure_text"] = address
    elif question_key == "to":
        await event.respond(
            user.loc.please_validate_destination_place_text.format(
                destination=address
            )
        )

    state.value["order_data"][question_key] = {
        "lat": lat,
        "lon": lon,
        "text": address,
    }


async def location_text_handler(
        message,
        question_key,
        event,
        user,
        state
):
    address = await bot_utils.get_text_address_by_coords(
        message.geo.lat, message.geo.long
    )
    if question_key == "from":
        await event.respond(
            user.loc.please_validate_departure_place_text.format(departure=address)
        )
    elif question_key == "to":
        await event.respond(
            user.loc.please_validate_destination_place_text.format(
                destination=address
            )
        )
    state.value["order_data"][question_key] = {
        "lat": message.geo.lat,
        "lon": message.geo.long,
        "text": address,
    }


# Used in callbacks.py
async def cost_calculators(seater, booking_type, distance_meters_or_hours, time=None, pack=None):
    cost_multiplier = constants.Constants.ride_fare[seater][booking_type]
    discount,discount_str = 1 , ''
    if booking_type == 1:
        discount ,discount_str= 0.95 , '5%'
    elif booking_type == 2:
        discount , discount_str = constants.Constants.discount_for_office_commute[pack]
    price = (distance_meters_or_hours / 1000.0) * cost_multiplier * discount
    price = int(price * 100)  # in cents

    return price #, discount_str


async def time_handler(user, event, state, answer, state_key, ):
    hours, minutes = answer.split(":")
    hours = int(hours)
    minutes = int(minutes)
    new_date = state.value[state_key]["date"] + datetime.timedelta(
        hours=hours, minutes=minutes
    )
    min_today = datetime.datetime.now(tz=common.tz).replace(second=0, microsecond=0)
    if new_date < min_today:
        await event.respond(user.loc.riders_please_provide_time_in_future_text)
        return
    state.value[state_key]["time"] = new_date
    await state.save()


async def date_handler(state, answer, state_key):
    date = common.tz.localize(datetime.datetime.strptime(answer, "%d.%m.%Y"))
    state.value[state_key]["date"] = date
    await state.save()


async def fetch_categories():
    all_categories = await database.CabCategory.filter(enabled=True)
    categories_buttons = []
    for category in all_categories:
        categories_buttons.append(

            Button.inline(
                category.name,
                data=f"order_category|{category.id}",
            )

        )
    return categories_buttons


if __name__ == "__main__":
    pass
