import typing
from .. import database, locales, shared, bot_utils, common
from telethon import TelegramClient, events, Button, types, utils, functions
from telethon.errors import rpcerrorlist
from telethon.tl import patched
import logging
import enum
import re
import pytz
import datetime
import asyncio
import os
import tortoise
from tortoise import functions as tfunc
from tortoise.queryset import Q, F

logger = logging.getLogger("workers")


async def drivers_kicker():
    """
    This function fetches drivers group members and kicks those who are not subscribed. (excluding admins and bots)
    I won't use iter_participants because it yields users instead of Participant objects (helps with admins)
    """
    full_channel = await shared.drivers_bot(
        functions.channels.GetFullChannelRequest(shared.config.driver_group_id)
    )
    cnt = full_channel.full_chat.participants_count
    for i in range(0, cnt, 100):
        participants = await shared.drivers_bot(
            functions.channels.GetParticipantsRequest(
                shared.config.driver_group_id,
                filter=types.ChannelParticipantsSearch(""),
                offset=i,
                limit=100,
                hash=0,
            )
        )
        users = {user.id: user for user in participants.users}
        for participant in participants.participants:
            if isinstance(
                    participant,
                    (types.ChannelParticipantCreator, types.ChannelParticipantAdmin),
            ):
                continue
            if users[participant.user_id].bot:
                continue
            user = await database.User.get_or_none(user_id=participant.user_id)
            can_stay = False
            loc = locales.En
            if user:
                loc = user.loc
                driver = await user.get_driver()
                if driver.is_subscribed:
                    can_stay = True

            if not can_stay:
                logger.info(f"Kicking {participant.user_id}")
                await shared.drivers_bot.kick_participant(
                    shared.config.driver_group_id, participant.user_id
                )

                # noinspection TryExceptPass,PyBroadException
                try:
                    await shared.drivers_bot.send_message(
                        participant.user_id,
                        loc.drivers_you_were_kicked_group_no_sub_text,
                    )
                except Exception:
                    pass


async def drivers_kicker_worker():
    while not shared.config.driver_group_id:
        await asyncio.sleep(1)
    while True:
        try:
            await drivers_kicker()
        except Exception as e:
            logger.exception(e)
        await asyncio.sleep(60 * 10)


async def drivers_sub_end_notifier():
    """
    Notifies drivers when they have 24 hours and 1 hour left of their subscription.
    Makes use of Driver.last_subscription_notification in order to not spam users.
    """
    all_with_sub = await database.Driver.filter(
        subscription_until__gte=datetime.datetime.utcnow()
    )
    for driver in all_with_sub:
        expires_in = driver.subscription_until - datetime.datetime.now(tz=pytz.utc)
        last_notified = (
            (driver.last_subscription_notification - datetime.datetime.now(tz=pytz.utc))
            if driver.last_subscription_notification
            else datetime.timedelta(hours=100)
        )

        if expires_in < datetime.timedelta(hours=24) and (
                not last_notified or last_notified > datetime.timedelta(hours=24)
        ):
            user: database.User = await driver.user
            # noinspection TryExceptPass,PyBroadException
            try:
                await shared.drivers_bot.send_message(
                    user.user_id,
                    user.loc.drivers_subscription_24_hours_left_notification_text,
                    buttons=user.loc.drivers_begin_payment_button,
                )
            except Exception:
                pass
            driver.last_subscription_notification = datetime.datetime.utcnow()
            await driver.save()
        elif expires_in < datetime.timedelta(hours=1) and (
                not last_notified or last_notified > datetime.timedelta(hours=1)
        ):
            user: database.User = await driver.user
            # noinspection TryExceptPass,PyBroadException
            try:
                await shared.drivers_bot.send_message(
                    user.user_id,
                    user.loc.drivers_subscription_1_hour_left_notification_text,
                    buttons=user.loc.drivers_begin_payment_button,
                )
            except Exception:
                pass
            driver.last_subscription_notification = datetime.datetime.utcnow()
            await driver.save()


async def drivers_sub_end_notifier_worker():
    while True:
        try:
            await drivers_sub_end_notifier()
        except Exception as e:
            logger.exception(e)
        await asyncio.sleep(5)


async def notify_about_upcoming_ride():

    """
    This function is used to fetch rides which require an alert reminder.

    It performs the following filters:
    - The ride status should be 'accepted_by_driver'.
    - The last_ride_reminder field should be null, meaning no reminder has been sent yet.
    - The pickup_time_scheduled should be 3 hours or 24 hours from the current time (with 10 minutes of tolerance).
    - If the ride was created less than 3 hours before pickup_time_scheduled, it should not be alerted.

    It returns two lists of Ride instances, the first for 3 hours alert and the second for 24 hours alert.
    """
    now = datetime.datetime.utcnow()

    # Calculate time ranges for 3 hours and 24 hours from now
    three_hours_from_now = now + datetime.timedelta(hours=3)
    twenty_four_hours_from_now = now + datetime.timedelta(hours=24)

    # 10 minutes of tolerance for the reminders
    tolerance = datetime.timedelta(minutes=10)

    all_active_and_within_3_hours = database.Ride.filter(
        Q(last_ride_reminder=None) | Q(last_ride_reminder__lte=now - (tolerance * 2)),
        status=database.RideStatus.ACCEPTED_BY_DRIVER,
        pickup_time_scheduled__gte=three_hours_from_now - tolerance,
        pickup_time_scheduled__lte=three_hours_from_now + tolerance,
        # created_at__lte=now - datetime.timedelta(hours=3),
    )
    # logger.debug(all_active_and_within_3_hours.as_query())
    all_active_and_within_3_hours = await all_active_and_within_3_hours

    for ride in all_active_and_within_3_hours:
        ride.last_ride_reminder = now
        await ride.save()
        driver: database.Driver = await ride.driver
        driver_user: database.User = await driver.user
        rider_user: database.User = await ride.user
        ride_info_for_driver = await ride.text_for_driver(driver_user)
        ride_info_for_rider = await ride.text_for_rider(rider_user)
        # noinspection TryExceptPass,PyBroadException
        try:
            await shared.drivers_bot.send_message(
                driver_user.user_id,
                driver_user.loc.drivers_planned_drive_alert_text.format(
                    time_left=bot_utils.seconds_to_human_readable(
                        (
                                ride.pickup_time_scheduled
                                - datetime.datetime.now(tz=pytz.utc)
                        ).seconds
                    ),
                    ride_info=ride_info_for_driver,
                ),
            )
        except Exception as e:
            logger.warning(f"Cant send message to driver {driver_user.user_id}: {e}")
        # noinspection TryExceptPass,PyBroadException
        try:
            await shared.riders_bot.send_message(
                rider_user.user_id,
                rider_user.loc.riders_planned_drive_alert_text.format(
                    time_left=bot_utils.seconds_to_human_readable(
                        (
                                ride.pickup_time_scheduled
                                - datetime.datetime.now(tz=pytz.utc)
                        ).seconds
                    ),
                    ride_info=ride_info_for_rider,
                ),
            )
        except Exception as e:
            logger.warning(f"Cant send message to rider {rider_user.user_id}: {e}")

        # using first_ride_id and is_next_ride_created to create subsequent rides for two-way and office commute
        flag = ride.is_next_ride_created
        bt = ride.booking_type
        if not flag and bt == 1:
            new_ride = await database.Ride.create(
                user=rider_user,
                category_id=ride.category_id,
                booking_type=ride.booking_type,
                from_lat=ride.to_lat,
                from_lon=ride.to_lon,
                to_lat=ride.from_lat,
                to_lon=ride.from_lon,
                from_text_address=ride.to_text_address,
                to_text_address=ride.from_text_address,
                pickup_time_scheduled=ride.return_time_scheduled,
                status=ride.status,
                group_message_id=ride.group_message_id,
                cost=ride.cost,
                distance=ride.distance,
                duration=ride.duration,
                phone_number=ride.phone_number,
                full_name=ride.full_name,
                return_time_scheduled=None,
                days_of_office_commute='',
                is_next_ride_created=True,
                driver_id=ride.driver_id,
                first_ride_id=ride.first_ride_id
            )
            ride.is_next_ride_created = True
            await ride.save()

        elif not flag and bt == 2:

            pickup_time_scheduled = ride.pickup_time_scheduled
            days = ride.days_of_office_commute.split('|')
            no_of_days = int(days[-1])
            days_of_week = days[:-1]
            target_timezone = pytz.timezone('Asia/Kolkata')

            #firstRide = await database.Ride.get(id = ride.first_ride_id)
            #end_date = firstRide.pickup_time_scheduled.astimezone(target_timezone)
            #end_date += datetime.timedelta(days=no_of_days)


            def find_nearest_date(pc, weekdays):
                counter = 0
                pc = pc.astimezone(target_timezone)
                while True:
                    # Increment the counter by 1 for each iteration
                    counter += 1
                    date = pc + datetime.timedelta(days=counter)
                    if date.strftime('%a') in weekdays:
                        return date


            new_pickup_time_scheduled = find_nearest_date(pickup_time_scheduled, days_of_week)
            pickup_time_scheduled = pickup_time_scheduled.astimezone(target_timezone)
            decrement_in_days  = (new_pickup_time_scheduled.date() - pickup_time_scheduled.date()).days
            no_of_days_new = no_of_days - decrement_in_days
            if no_of_days_new<=0:
                return
            days_of_week.append(str(no_of_days_new))
            days_of_week = '|'.join(days_of_week)
            await database.Ride.create(
                user=rider_user,
                category_id=ride.category_id,
                booking_type=ride.booking_type,
                from_lat=ride.from_lat,
                from_lon=ride.from_lon,
                to_lat=ride.to_lat,
                to_lon=ride.to_lon,
                from_text_address=ride.from_text_address,
                to_text_address=ride.to_text_address,
                pickup_time_scheduled=new_pickup_time_scheduled,
                status=ride.status,
                group_message_id=ride.group_message_id,
                cost=ride.cost,
                distance=ride.distance,
                duration=ride.duration,
                phone_number=ride.phone_number,
                full_name=ride.full_name,
                return_time_scheduled=ride.return_time_scheduled,
                days_of_office_commute=days_of_week,
                is_next_ride_created=False,
                driver_id=ride.driver_id,
                first_ride_id=ride.first_ride_id
            )
            ride.is_next_ride_created = True
            await ride.save()


async def ride_notifier_worker():
    while True:
        try:
            await notify_about_upcoming_ride()
        except Exception as e:
            logger.exception(e)
        await asyncio.sleep(5)


async def on_drive_start_notify_user():
    """
    This function sends a message to a user when the ride starts.
    `alert_admin_prompted` indicates whether the message is already sent to the user.
    """

    to_notify = await database.Ride.filter(
        status=database.RideStatus.ACCEPTED_BY_DRIVER,
        alert_admin_prompted=False,
        pickup_time_scheduled__lte=datetime.datetime.utcnow(),
    )
    for ride in to_notify:
        ride.alert_admin_prompted = True
        await ride.save()
        user = await ride.user

        try:
            await shared.riders_bot.send_message(
                user.user_id,
                user.loc.drive_should_have_started_mb_alert_text.format(id=ride.id),
                buttons=[
                    [
                        Button.inline(
                            user.loc.drive_should_have_started_mb_alert_btn_text,
                            f"alert|{ride.id}",
                        )
                    ]
                ],
            )
        except Exception as e:
            logger.warning(f"Cant send message to rider {ride.user.user_id}: {e}")


async def drive_start_notifier_worker():
    while True:
        try:
            await on_drive_start_notify_user()
        except Exception as e:
            logger.exception(e)
        await asyncio.sleep(5)


async def after_drive_end_review_ask():
    """
    This function sends a message to driver and rider to ask for feedback.
    `after_ride_feedback_asked` indicates whether the message is already sent to the user.
    We should consider the ride as ended when (Ride.duration * 1.2) has passed after planned pickup time.
    (duration is expected ride duration in seconds)
    """

    now = datetime.datetime.utcnow()
    rides = await database.Ride.filter(
        Q(after_ride_feedback_asked=False)
        & Q(pickup_time_scheduled__isnull=False)
        & Q(duration__isnull=False)
        & Q(status=database.RideStatus.ACCEPTED_BY_DRIVER)
        & Q(pickup_time_scheduled__lte=now)
    )

    now_tz_aware = now.replace(tzinfo=pytz.utc)

    rides_to_ask_review = []
    for ride in rides:
        ride_end_time = ride.pickup_time_scheduled + datetime.timedelta(
            seconds=ride.duration * 1.2
        )
        if ride_end_time <= now_tz_aware:
            rides_to_ask_review.append(ride)

    for ride in rides_to_ask_review:
        ride.after_ride_feedback_asked = True
        await ride.save()
        driver: database.Driver = await ride.driver
        driver_user: database.User = await driver.user
        rider: database.User = await ride.user

        try:
            await shared.drivers_bot.send_message(
                driver_user.user_id,
                driver_user.loc.did_you_have_a_ride.format(
                    id=ride.id,
                    google_maps_from_url=ride.google_maps_from_url,
                    google_maps_to_url=ride.google_maps_to_url,
                    departure=ride.pickup_time_scheduled_timezone_aware.strftime(
                        "%d.%m.%Y %I:%M %p"
                    ),
                    driver_full_name=driver.full_name,
                    rider_full_name=ride.full_name,
                ),
                buttons=[
                    [
                        Button.inline(
                            driver_user.loc.yes_btntext,
                            f"feedback|{ride.id}",
                        ),
                        Button.inline(
                            driver_user.loc.no_btntext,
                            f"no_feedback|{ride.id}",
                        ),
                    ]
                ],
            )
        except Exception as e:
            logger.warning(f"Cant send message to driver {driver.user_id}: {e}")

        try:
            await shared.riders_bot.send_message(
                rider.user_id,
                rider.loc.did_you_have_a_ride.format(
                    id=ride.id,
                    google_maps_from_url=ride.google_maps_from_url,
                    google_maps_to_url=ride.google_maps_to_url,
                    departure=ride.pickup_time_scheduled_timezone_aware.strftime(
                        "%d.%m.%Y %I:%M %p"
                    ),
                    driver_full_name=driver.full_name,
                    rider_full_name=ride.full_name,
                ),
                buttons=[
                    [
                        Button.inline(
                            rider.loc.yes_btntext,
                            f"feedback|{ride.id}",
                        ),
                        Button.inline(
                            rider.loc.no_btntext,
                            f"no_feedback|{ride.id}",
                        ),
                    ]
                ],
            )
        except Exception as e:
            logger.warning(f"Cant send message to rider {rider.user_id}: {e}")


async def after_drive_end_review_ask_worker():
    while True:
        try:
            await after_drive_end_review_ask()
        except Exception as e:
            logger.exception(e)
        await asyncio.sleep(5)


async def init_workers(parent_logger=None):
    global logger
    if parent_logger:
        logger = parent_logger.getChild("workers")
    asyncio.create_task(drivers_kicker_worker())
    asyncio.create_task(drivers_sub_end_notifier_worker())
    asyncio.create_task(ride_notifier_worker())
    asyncio.create_task(drive_start_notifier_worker())
    asyncio.create_task(after_drive_end_review_ask_worker())
    logger.info("Initialized workers")
