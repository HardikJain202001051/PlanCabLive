import enum
import re
import pytz
import typing

from telethon.tl import patched
from telethon.hints import MarkupLike

from .. import database


tz = pytz.timezone("Asia/Kolkata")


class ResponseType(str, enum.Enum):
    TEXT = "text"
    PHOTO = "photo"
    LOCATION = "location"


class QuestionStep:
    def __init__(
        self,
        locales_attr: str,
        response_type: typing.Union[ResponseType, typing.List[ResponseType]],
        regex: str = None,
        textfmt: typing.Callable[[str], str] = None,
    ):
        """

        :param locales_attr: name of locale
        :param response_type: type of response
        :param regex: if exists, message.text must match this regex
        :param textfmt: if exists, get_text will return textfmt(x.locales_attr)
        :param buttons: if exists, will be used as buttons
        """
        self.locales_attr = locales_attr
        self.response_type = response_type
        self.regex = regex
        self.textfmt = textfmt

    def get_text(self, user: database.User):
        if self.textfmt:
            return self.textfmt(getattr(user.loc, self.locales_attr))
        return getattr(user.loc, self.locales_attr)

    def validate(self, message: patched.Message):
        to_check = (
            [self.response_type]
            if not isinstance(self.response_type, list)
            else self.response_type
        )
        for r_type in to_check:
            if r_type == ResponseType.TEXT:
                if not message.text:
                    continue
                if self.regex:
                    if re.match(self.regex, message.text):
                        return r_type
                    continue
                return r_type
            elif r_type == ResponseType.PHOTO:
                if not message.photo and not (
                    message.document and message.document.mime_type.startswith("image")
                ):
                    continue
                return r_type
            elif r_type == ResponseType.LOCATION:
                if not message.geo:
                    continue
                return r_type
            else:
                raise NotImplementedError
        return False
