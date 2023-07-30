import typing

import tortoise
import datetime
import enum
from telethon.tl import types, alltlobjects
import pytz
import logging

from tortoise.expressions import Q

from .. import locales
import pickle

logger = logging.getLogger("database")


class User(tortoise.models.Model):
    """
    This is shared between 2 bots.
    """

    user_id = tortoise.fields.BigIntField(pk=True)
    lang_code = tortoise.fields.CharField(max_length=10, default="en")  # en,hi,kn
    blocked = tortoise.fields.BooleanField(default=False)

    #this name is the name of telegram account
    first_name = tortoise.fields.CharField(max_length=128, default="")
    last_name = tortoise.fields.CharField(max_length=128, default="", null=True)
    username = tortoise.fields.CharField(max_length=128, default="", null=True)

    #this is taken as input from rider
    phone_number = tortoise.fields.CharField(max_length=15,default="No Number")  # latest todo : new field created in db - phone,fullname
    full_name = tortoise.fields.CharField(max_length=128, default="")
    class Meta:
        table = "users"

    def __str__(self):
        return f"<User {self.user_id}>"

    def __repr__(self):
        return str(self)

    @property
    def loc(self) -> locales.En:
        return locales.locales.get(self.lang_code, locales.En)


    async def get_driver(self) -> "Driver":
        try:
            created, _ = await Driver.get_or_create(user=self)
        except Exception :
            created = await Driver.get(Q(user=self) & Q(is_vendor=True))
        return created

    async def get_state(self, bot_id):
        created, _ = await UserState.get_or_create(user=self, bot_id=bot_id)
        return created

    async def mb_update_data(self, user: typing.Awaitable[types.User]):
        if not isinstance(user, types.User):
            user = await user
        updated = False
        if user.first_name != self.first_name:
            self.first_name = user.first_name
            updated = True

        if user.last_name != self.last_name:
            self.last_name = user.last_name
            updated = True

        if user.username != self.username:
            self.username = user.username
            updated = True

        if updated:
            await self.save()


class PickledDictField(tortoise.fields.BinaryField):
    def to_db_value(self, value, instance):
        return super().to_db_value(pickle.dumps(value), instance)

    # noinspection PickleLoad
    def to_python_value(self, value):
        return pickle.loads(super().to_python_value(value))


class UserState(tortoise.models.Model):
    """
    State saves user's current step and data related to it.

    I prefer to use it instead of in-RAM storage (e.g. conversations in telethon or message.chat in aiogram)
    because it's more reliable and persistent, although significantly slower to write.

    It's also useful for debugging and analytics.

    `payload` represents current user state, and used when user is required to send a message.
    `value` stores some additional data, may be used both in message and non-message states (callback query).
    """

    user = tortoise.fields.ForeignKeyField("models.User", related_name="states")
    # bot_id is used to separate states between bots (drivers bot and riders bot)
    bot_id = tortoise.fields.BigIntField()

    payload = tortoise.fields.CharField(max_length=100, default="")
    value = PickledDictField(default=dict)

    # payment holds the value of ride_id between the payment screenshot is sent by rider and till the payment is approved admin.
    # Because if user fires /start or /order command then state.value will get cleared out
    # payment = PickledDictField(default=dict)

    class Meta:
        table = "user_states"
        unique_together = (("user", "bot_id"),)

    def __str__(self):
        return f"<UserState {self.user_id}@{self.bot_id}: {self.payload}, data: {self.value}>"

    def __repr__(self):
        return str(self)


class CabCategory(tortoise.models.Model):
    """
    I went for making it a database model instead of a config file because it's easier to manage
    and will let to disable/rename categories without breaking old data.

    cost_multiplier is used to calculate cost of a ride - formula: [distance in km * cost_multiplier]
    website_code_name is used to identify category when API request comes from website.
    """

    id = tortoise.fields.IntField(pk=True)

    # name is shown in the menus and etc
    name = tortoise.fields.CharField(max_length=128, default="")
    website_code_name = tortoise.fields.CharField(max_length=100, default="")
    description = tortoise.fields.CharField(max_length=100, default="")
    cost_multiplier = tortoise.fields.FloatField(default=1.0)
    enabled = tortoise.fields.BooleanField(default=True)

    class Meta:
        table = "cab_categories"
        indexes = (("website_code_name",),)

    def __str__(self):
        return f"<CabCategory {self.name} ({self.website_code_name})>"

    def __repr__(self):
        return str(self)


class Driver(tortoise.models.Model):
    """
    Driver is a user who can accept rides.
    confirmed is KYC status.
    subscription_until shows when driver's subscription to group ends.
    """

    user = tortoise.fields.ForeignKeyField("models.User", related_name="drivers",null=True)

    # I have no idea why are `categories` asked, its not really used anywhere.
    categories = tortoise.fields.ManyToManyField(
        "models.CabCategory", related_name="drivers",null=True
    )
    full_name = tortoise.fields.CharField(max_length=256, default="")
    vehicle_number = tortoise.fields.CharField(max_length=100, default="")
    phone = tortoise.fields.CharField(max_length=100, default="")
    vehicle_name = tortoise.fields.CharField(max_length=100, default="")

    # confirmation is done manually by owner. If user is not confirmed, they can't be promoted to pay for subscription.
    confirmed = tortoise.fields.BooleanField(default=False)

    # whether a driver has pending confirmation (to prevent owner spam)
    pending = tortoise.fields.BooleanField(default=False)

    # user will get a notification when their subscription ends (and 24 hours before it ends)
    # user will automatically get removed from group when subscription ends
    # user can't accept rides when subscription ends
    subscription_until = tortoise.fields.DatetimeField(null=True)
    last_subscription_notification = tortoise.fields.DatetimeField(null=True)

    car_photo = tortoise.fields.CharField(max_length=256, default="")
    is_vendor = tortoise.fields.BooleanField(default=False)
    vendor_id = tortoise.fields.IntField(null=True)

    class Meta:
        table = "drivers"

    def __str__(self):
        return f"<Driver {self.full_name} ({self.user})>"

    def __repr__(self):
        return str(self)

    @property
    def is_subscribed(self):
        return (
                self.subscription_until is not None
                and self.subscription_until > datetime.datetime.now(tz=pytz.utc)
        )

    @property
    def subscription_until_tz_aw(self):
        from .. import common

        return (
            self.subscription_until.astimezone(common.tz)
            if self.subscription_until
            else None
        )

    async def set_subscribed(self):
        """
        If driver isn't subscribed, sets subscription_until to 30 days from now.
        Else, adds 30 days to subscription_until.
        """
        if self.subscription_until is None:
            self.subscription_until = datetime.datetime.utcnow() + datetime.timedelta(
                days=30
            )
        else:
            self.subscription_until += datetime.timedelta(days=30)
        await self.save()


class RideStatus(enum.StrEnum):
    CREATED = "created"  # initial state
    PAID_BY_USER = "paid_by_user"  # state after admin approves payment
    PAYMENT_FAILED = "payment_failed"  # state after admin rejects payment
    SENT_TO_DRIVERS = (
        "sent_to_drivers"  # state after it's automatically sent to drivers
    )
    WAITING_UPDATION = "waiting_updation"
    ACCEPTED_BY_DRIVER = "accepted_by_driver"  # state after driver accepts the ride


class Ride(tortoise.models.Model):
    """
    Ride is a request for a cab.

    user is a user who requested the ride. It may be null if cab was requested from
        website (it would be marked in from_website field).

    driver_id is a driver who accepted the ride. It may be null if no driver accepted it yet.

    (from_lat, from_lon) and (to_lat, to_lon) are coordinates of pickup and destination points.
    """

    id = tortoise.fields.IntField(pk=True)

    user = tortoise.fields.ForeignKeyField(
        "models.User", related_name="rides", null=True
    )
    driver = tortoise.fields.ForeignKeyField(
        "models.Driver", related_name="rides", null=True
    )

    category = tortoise.fields.ForeignKeyField(
        "models.CabCategory", related_name="rides"
    )

    from_lat = tortoise.fields.FloatField()
    from_lon = tortoise.fields.FloatField()
    to_lat = tortoise.fields.FloatField()
    to_lon = tortoise.fields.FloatField()
    from_text_address = tortoise.fields.CharField(max_length=300, default="")
    to_text_address = tortoise.fields.CharField(max_length=300, default="")

    # pickup scheduled time
    pickup_time_scheduled = tortoise.fields.DatetimeField(null=True)
    return_time_scheduled = tortoise.fields.DatetimeField(null=True)
    days_of_office_commute = tortoise.fields.CharField(max_length=300, default="")
    # time when ride was created
    created_at = tortoise.fields.DatetimeField(auto_now_add=True)

    # time when ride was last updated
    updated_at = tortoise.fields.DatetimeField(auto_now=True)

    # status of the ride
    status = tortoise.fields.CharEnumField(RideStatus, default=RideStatus.CREATED)

    # cost of the ride calculated by the following formula: [distance in km * category.cost_multiplier]
    cost = tortoise.fields.IntField(null=True)  # Warning: this is in cents!

    # distance calculated by google's API
    distance = tortoise.fields.IntField(null=True)  # Meters

    # expected duration calculated by google's API at the moment of ride creation
    duration = tortoise.fields.IntField(null=True)  # Seconds

    # whether the ride was requested from API
    from_website = tortoise.fields.BooleanField(default=False)

    # message id in group where ride was sent
    group_message_id = tortoise.fields.BigIntField(null=True)

    # for linking subsequent rides to the first ride(Used for two way and office commute where there are multiple rides)
    first_ride_id = tortoise.fields.IntField(null=True)

    # to check if next ride has been already created using ride.first_ride_id
    is_next_ride_created = tortoise.fields.BooleanField(
        default=False
    )

    # rider's details todo: remove phone and name from here and link directly to user table
    phone_number = tortoise.fields.CharField(max_length=100, null=True)
    full_name = tortoise.fields.CharField(max_length=100, null=True)

    last_ride_reminder = tortoise.fields.DatetimeField(
        null=True
    )  # for reminders 3 and 24 hours before ride
    after_ride_feedback_asked = tortoise.fields.BooleanField(
        default=False
    )  # ask for feedback after ride
    alert_admin_prompted = tortoise.fields.BooleanField(
        default=False
    )  # prompt rider with "alert admin" button

    booking_type = tortoise.fields.IntField(default=0)  # New field for booking type

    class Meta:
        table = "rides"
        indexes = (("user",), ("driver",), ("category",), ("status",))

    @property
    def google_maps_from_url(self):
        return f"https://www.google.com/maps/search/?api=1&query={self.from_lat},{self.from_lon}"

    @property
    def google_maps_to_url(self):
        return f"https://www.google.com/maps/search/?api=1&query={self.to_lat},{self.to_lon}"

    def __str__(self):
        return (
            f"Ride #{self.id}\n"
            f"From: `{self.from_text_address}` [link] {self.google_maps_from_url}\n"
            f"To: `{self.to_text_address}` [link] {self.google_maps_to_url}\n"
            f"Category: {self.category}\n"
            f"Status: {self.status}\n"
        )

    async def admin_info_initial(self):
        from .. import bot_utils
        temp = ""
        booking_type = ''
        if self.return_time_scheduled:
            temp = f"Return time: {self.return_time_scheduled_timezone_aware.strftime('%d.%m.%Y %I:%M %p')}\n\n "
            booking_type = ' | Two-Way'
            if self.days_of_office_commute != "":
                booking_type = ' | Office Commute'
                temp = temp[:13] + temp[-11:]
                days = self.days_of_office_commute.split('|')
                no_of_rides_left = days[-1]
                days = " ".join(days[:-1])
                temp = temp + f"Days: {days}\n\n" + f"Days Left : {no_of_rides_left}"
        elif self.booking_type == 4:
            booking_type = 'Pet Friendly'
        elif self.booking_type == 5:
            booking_type = 'Outstation'

        return (
                f"Ride #{self.id}\n\n"
                f"From: `{self.from_text_address}` [link]({self.google_maps_from_url})\n\n"
                f"To: `{self.to_text_address}` [link]({self.google_maps_to_url})\n\n"
                f"Category: {(await self.category).name} " + booking_type + "\n\n"
                                                                            f"Distance: {round(self.distance / 1000, 2)} KM\n\n"
                                                                            f"Duration: {bot_utils.seconds_to_human_readable(self.duration)}\n\n"
                                                                            f"Cost: {round(self.cost / 100, 2)}\n\n"
                                                                            f"Pickup time: {self.pickup_time_scheduled_timezone_aware.strftime('%d.%m.%Y %I:%M %p')}\n\n" + temp

        )

    async def full_admin_info(self):
        from .. import bot_utils
        temp = ""
        booking_type = ''
        if self.return_time_scheduled:
            booking_type = ' | Two-Way'
            temp = f"Return time: {self.return_time_scheduled_timezone_aware.strftime('%d.%m.%Y %I:%M %p')}\n\n "
            if self.days_of_office_commute != "":
                booking_type = ' | Office Commute'
                temp = f"Return time: {self.return_time_scheduled_timezone_aware.strftime('%I:%M %p')}\n\n"
                days = self.days_of_office_commute.split('|')
                no_of_rides_left = days[-1]
                days = " ".join(days[:-1])
                temp = temp + f"Days: {days}\n\n" + f"Days : {no_of_rides_left}\n\n"
        elif self.booking_type == 4:
            booking_type = 'Pet Friendly'
        elif self.booking_type == 5:
            booking_type = 'Outstation'
        return (
                f"Ride #`{self.id}`\n"
                f"From: `{self.from_text_address}` [link]({self.google_maps_from_url})\n\n"
                f"To: `{self.to_text_address}` [link]({self.google_maps_to_url})\n\n"
                f"Category: {(await self.category).name} " + booking_type + "\n\n"
                                                                            f"Distance: {round(self.distance / 1000, 2)} KM\n\n"
                                                                            f"Duration: {bot_utils.seconds_to_human_readable(self.duration)}\n\n "
                                                                            f"Cost: {round(self.cost / 100, 2)}\n\n"
                                                                            f"Pickup time: {self.pickup_time_scheduled_timezone_aware.strftime('%d.%m.%Y %I:%M %p')}\n\n" + temp +
                f"Status: {self.status}\n\n"
                f"Driver id: `{self.driver_id or 'no driver'}`\n\n"
                f"User id: `{self.user_id}`\n\n"
                f"Rider's phone number: `{self.phone_number}`\n\n"
                f"Rider's full name: `{self.full_name}`\n\n"
        )

    async def message_for_drivers_group(self):
        from .. import bot_utils
        temp = ""
        booking_type = ''
        if self.return_time_scheduled:
            temp = f"⏱ Return time: {self.return_time_scheduled_timezone_aware.strftime('%I:%M %p')}\n\n "
            booking_type = ' | Two-Way'
            if self.days_of_office_commute == "":
                temp = f"📆 Return date: {self.return_time_scheduled_timezone_aware.strftime('%d.%m.%Y')}\n" + temp
            else:
                booking_type = ' **| Office Commute**'
                days = self.days_of_office_commute.split('|')
                no_of_rides_left = days[-1]
                days = " ".join(days[:-1])
                temp = temp + f"🏢 Days: {days}\n" + f"🔢 Days : {no_of_rides_left}"
        elif self.booking_type == 4:
            booking_type = 'Pet Friendly'
        elif self.booking_type == 5:
            booking_type = 'Outstation'
        return (
                f"🆕 Ride #{self.id}\n\n"
                f"📍 From: `{self.from_text_address}` [link]({self.google_maps_from_url})\n\n"
                f"🏁 To: `{self.to_text_address}` [link]({self.google_maps_to_url})\n\n"
                f"**🚖 Category: {(await self.category).name} **" + booking_type + "\n\n"
                                                                                   f"🛣 Distance: {round(self.distance / 1000, 2)} KM\n\n"
                                                                                   f"⏳ Duration: {bot_utils.seconds_to_human_readable(self.duration)}**\n\n"
                                                                                   f"**💵 Cost: {round(self.cost / 100, 2)}\n\n"
                                                                                   f"📅 Pickup date: {self.pickup_time_scheduled_timezone_aware.strftime('%d.%m.%Y')}\n"
                                                                                   f"🕐 Pickup time: {self.pickup_time_scheduled_timezone_aware.strftime('%I:%M %p')}\n" + temp + "\n"
        )

    def __repr__(self):
        return str(self)

    @property
    def from_telegram(self):
        return not self.from_website

    @property
    def pickup_time_scheduled_timezone_aware(self):
        from .. import common

        return (
            self.pickup_time_scheduled.astimezone(common.tz)
            if self.pickup_time_scheduled
            else None
        )

    @property
    def return_time_scheduled_timezone_aware(self):
        from .. import common

        return (
            self.return_time_scheduled.astimezone(common.tz)
            if self.return_time_scheduled
            else None
        )

    @property
    def created_at_timezone_aware(self):
        from .. import common

        return (self.created_at.astimezone(common.tz)) if self.created_at else None

    @property
    def updated_at_timezone_aware(self):
        from .. import common

        return (self.updated_at.astimezone(common.tz)) if self.updated_at else None

    async def text_for_driver(self, driver: User):
        from .. import bot_utils

        temp = ""
        booking_type = ''
        if self.return_time_scheduled:
            booking_type = ' | Two-Way'
            temp = f"\n⏱ Return time: {self.return_time_scheduled_timezone_aware.strftime('%d.%m.%Y  %I:%M %p')}\n\n "
            if self.days_of_office_commute != "":
                booking_type = ' | Office Commute'
                temp = temp[:16] + temp[-11:]
                days = self.days_of_office_commute.split('|')
                no_of_rides_left = days[-1]
                days = " ".join(days[:-1])
                temp = temp + f"Days: {days}\n" + f"Days : {no_of_rides_left}"
        elif self.booking_type == 4:
            booking_type = 'Pet Friendly'
        elif self.booking_type == 5:
            booking_type = 'Outstation'

        return driver.loc.drivers_ride_details.format(
            id=self.id,
            text_from=self.from_text_address,
            text_to=self.to_text_address,
            google_maps_from_url=self.google_maps_from_url,
            google_maps_to_url=self.google_maps_to_url,
            category=(await self.category).name + ' ' + booking_type,
            distance=round(self.distance / 1000, 2),
            duration=bot_utils.seconds_to_human_readable(self.duration),
            cost=round(self.cost / 100, 2),
            pickup_time=self.pickup_time_scheduled_timezone_aware.strftime(
                "%d.%m.%Y %I:%M %p"
            ) + temp,
            phone_number=self.phone_number,
            full_name=self.full_name,
        )

    async def text_for_rider(self, rider: User):
        from .. import bot_utils

        driver: Driver = await self.driver

        temp = ""
        booking_type = ''
        if self.return_time_scheduled:
            booking_type = ' | Two-Way'
            temp = f"\n⏱ Return time: {self.return_time_scheduled_timezone_aware.strftime('%d.%m.%Y  %I:%M %p')}\n\n "
            if self.days_of_office_commute != "":
                booking_type = ' | Office Commute'
                temp = temp[:16] + temp[-11:]
                days = self.days_of_office_commute.split('|')
                no_of_rides_left = days[-1]
                days = " ".join(days[:-1])
                temp = temp + f"Days: {days}\n\n" + f"Days : {no_of_rides_left}\n"
        elif self.booking_type == 4:
            booking_type = 'Pet Friendly'
        elif self.booking_type == 5:
            booking_type = 'Outstation'

        return rider.loc.riders_ride_details_text.format(
            id=self.id,
            google_maps_from_url=self.google_maps_from_url,
            google_maps_to_url=self.google_maps_to_url,
            category=(await self.category).name + ' ' + booking_type,
            distance=round(self.distance / 1000, 2),
            duration=bot_utils.seconds_to_human_readable(self.duration),
            cost=round(self.cost / 100, 2),
            departure=self.pickup_time_scheduled_timezone_aware.strftime(
                "%d.%m.%Y %I:%M %p"
            ) + temp,
            driver_phone_number=driver.phone,
            driver_full_name=driver.full_name,
            driver_vehicle_name=driver.vehicle_name,
            driver_vehicle_number=driver.vehicle_number,
        )


class ReferralPoint(tortoise.models.Model):
    id = tortoise.fields.IntField(pk=True)
    referer = tortoise.fields.ForeignKeyField(
        "models.User", related_name="reffered_users"
    )
    referred = tortoise.fields.ForeignKeyField("models.User", related_name="referrals")
    # ride will be filled when referred user completes his first ride
    ride = tortoise.fields.ForeignKeyField(
        "models.Ride", related_name="referrals", null=True
    )
    created_at = tortoise.fields.DatetimeField(auto_now_add=True)
    point_used = tortoise.fields.BooleanField(default=False)

    class Meta:
        table = "referral_points"
        unique_together = (("referer", "referred"),)
        indexes = (("referer",), ("referred",))

    def __str__(self):
        return (
            f"Referral point #{self.id} referer: {self.referer} "
            f"referred: {self.referred} ride: {self.ride} point_used: {self.point_used}"
        )

    @classmethod
    async def mark_if_needed(cls, ride: Ride):
        rider: User = await ride.user
        referral_point = await cls.filter(referred=rider).first()
        if not referral_point:
            return
        if referral_point.ride:
            return
        referral_point.ride = ride
        await referral_point.save()

    @classmethod
    async def can_redeem_x_points(cls, user: User, x: int):
        points = await cls.filter(
            referer=user, ride_id__isnull=False, point_used=False
        ).count()
        return points >= x

    @classmethod
    async def redeem_x_points(cls, user: User, x: int):
        points = (
            await cls.filter(referer=user, ride_id__isnull=False, point_used=False)
                .order_by("-created_at")
                .limit(x)
        )
        if len(points) < x:
            raise ValueError("Not enough points to redeem")
        await cls.filter(id__in=[p.id for p in points]).update(point_used=True)


class Review(tortoise.models.Model):
    """
    A review with:
    * 1-5 stars
    * text
    * from_user
    * to_user
    * ride
    * by side (driver or rider)
    """

    id = tortoise.fields.IntField(pk=True)
    stars = tortoise.fields.IntField(min_value=1, max_value=5)
    text = tortoise.fields.TextField()
    from_user = tortoise.fields.ForeignKeyField("models.User", related_name="reviews")
    to_user = tortoise.fields.ForeignKeyField(
        "models.User", related_name="received_reviews"
    )
    ride = tortoise.fields.ForeignKeyField("models.Ride", related_name="reviews")
    by_driver = tortoise.fields.BooleanField()
    created_at = tortoise.fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "reviews"
        indexes = (("from_user",), ("to_user",), ("ride",))

    @property
    def by_rider(self):
        return not self.by_driver

    def __str__(self):
        return (
            f"Review #{self.id} from_user: {self.from_user} "
            f"to_user: {self.to_user} ride: {self.ride} "
            f"by_driver: {self.by_driver} stars: {self.stars} text: {self.text}"
        )


async def init_db(parent_logger: logging.Logger = None):
    global logger
    if parent_logger:
        logger = parent_logger.getChild("database")
    logger.info("Initializing database")
    await tortoise.Tortoise.init(
        db_url="sqlite://db.sqlite3", modules={"models": ["plancab.database"]}
    )
    await tortoise.Tortoise.generate_schemas()
    logger.info("Database initialized")
