from telethon import types, utils, TelegramClient
import typing
import qrcode
from PIL import Image
import io
from urllib.parse import urlencode, quote
import aiohttp
import asyncio
import typing
import datetime
from .. import shared


class ExceptionWillReturnToUser(Exception):
    def __init__(self, code: str, *args):
        self.code = code
        super().__init__(f"Error code: {code}", *args)


async def get_drive_time_and_distance(
    from_lat: float,
    from_lng: float,
    to_lat: float,
    to_lng: float,
) -> typing.Tuple[int, int]:
    """

    :param from_lat: From latitude
    :param from_lng: From longitude
    :param to_lat: To latitude
    :param to_lng: To longitude
    :return: time in seconds, distance in meters
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://maps.googleapis.com/maps/api/directions/json",
            params={
                "origin": f"{from_lat},{from_lng}",
                "destination": f"{to_lat},{to_lng}",
                "key": shared.config.google_api_key,
                "mode": "driving",
            },
        ) as resp:
            data = await resp.json()
            if data["status"] == "OK":
                return (
                    data["routes"][0]["legs"][0]["duration"]["value"],
                    data["routes"][0]["legs"][0]["distance"]["value"],
                )
            else:
                if data["status"] == "ZERO_RESULTS" or data["status"] == "NOT_FOUND":
                    raise ExceptionWillReturnToUser(data["status"])
                raise Exception(f"google_api_error: {data['status']}")


async def get_coords_by_text_address(address: str) -> typing.Tuple[float, float]:
    """
    Search for coordinates by text address

    :param address: desired address
    :return: latitude and longitude
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": address,
                "key": shared.config.google_api_key,
            },
        ) as resp:
            data = await resp.json()
            if data["status"] == "OK":
                return (
                    data["results"][0]["geometry"]["location"]["lat"],
                    data["results"][0]["geometry"]["location"]["lng"],
                )
            else:
                if data["status"] == "ZERO_RESULTS" or data["status"] == "NOT_FOUND":
                    raise ExceptionWillReturnToUser(data["status"])
                raise Exception(f"google_api_error: {data['status']}")


async def get_text_address_by_coords(lat: float, lng: float) -> str:
    """
    Search for text address by coordinates

    :param lat: latitude
    :param lng: longitude
    :return: text address
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "latlng": f"{lat},{lng}",
                "key": shared.config.google_api_key,
            },
        ) as resp:
            data = await resp.json()
            if data["status"] == "OK":
                return data["results"][0]["formatted_address"]
            else:
                if data["status"] == "ZERO_RESULTS" or data["status"] == "NOT_FOUND":
                    raise ExceptionWillReturnToUser(data["status"])
                raise Exception(f"google_api_error: {data['status']}")


def get_max_user_info(
    user: types.User,
    full_user: typing.Optional[types.users.UserFull] = None,
) -> str:
    # if full_user is not provided, we'll assume we can link the user.
    # else check if the user has a private forward name
    can_link = full_user is None or not full_user.full_user.private_forward_name
    user_info = f"User id: `{user.id}` "
    if can_link:
        user_info += f"[link](tg://user?id={user.id}) "
    user_info += utils.get_display_name(user) + " "
    if user.username:
        user_info += f"(@{user.username}) "
    return user_info


def write_qr_code(data: str, file_handle: io.BufferedWriter):
    template_image = Image.open("qr_background.png")
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=17,
        border=1,
    )

    # Add data to the QR code
    qr.add_data(data)
    qr.make(fit=True)

    # Generate the QR code image
    qr_image = qr.make_image(fill_color=(34, 27, 45), back_color="white")

    x, y = 290, 1086

    # Paste the QR code onto the template image
    template_image.paste(qr_image, (x, y))

    template_image.save(file_handle, "PNG")
    template_image.close()
    qr_image.close()


def build_url(base: str, params: dict) -> str:
    encoded_params = "&".join(
        f"{key}={value}" for key, value in params.items()
    )
    return f"{base}?{encoded_params}" if encoded_params else base


def seconds_to_human_readable(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return (
        (f"{hours % 12}h " if hours else "")
        + (f"{minutes}m " if minutes else "")
        # + (f"{seconds}s" if seconds else "")
    ) or "0s"


async def send_user_to_privacy_share_group(
    via_bot: TelegramClient,
    user: typing.Union[typing.Awaitable[types.User], types.User],
):
    """
    Due to both bots needing to be able to send `tg://user?id=` links, we need to send the user to a shared chat,
    so telethon will cache the access_hash for the user.
    Else the other bot will not be able to send the link (it won't be clickable)

    This is usually called from payment step - so it won't be used too often,
    But will 100% be called before ordering a cab / enrolling as a driver.

    It also will be called on first /start of user
    """
    if not isinstance(user, types.User):
        user = await user
    user_info = get_max_user_info(user)
    await via_bot.send_message(
        shared.config.bot_shared_chat_for_privacy_id,
        f"{user_info}",
    )
