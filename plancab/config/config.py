"""
Static data will be saved within config rather than database.
This is because it's not expected to change often.
"""


import os
import json
import logging

logger = logging.getLogger(os.path.basename(__file__).split(".")[0])


class Config:
    def __init__(self, file_path):
        self.file_path = file_path
        self._owner_id = None
        self._api_id = None
        self._api_hash = None
        self._driver_bot_token = None
        self._rider_bot_token = None
        self._driver_group_id = None
        self._driver_group_invite_link = None
        self._sms_api_token = None
        self._google_api_key = None
        self._upi_id = None
        self._upi_name = None
        self._upi_mode = None
        self._upi_purpose = None
        self._bot_shared_chat_for_privacy_id = None

        self.__validate_and_load_file()

    @staticmethod
    def __example_file():
        return {
            "owner_id": 0,
            "api_id": 0,
            "api_hash": "",
            "driver_bot_token": "",
            "rider_bot_token": "",
            "driver_group_id": 0,
            "driver_group_invite_link": "",
            "sms_api_token": "",
            "google_api_key": "",
            "upi_id": "",
            "upi_name": "",
            "upi_mode": "",
            "upi_purpose": "",
            "bot_shared_chat_for_privacy_id": 0,
        }

    def __load(self):
        with open(self.file_path, "r") as f:
            data = json.load(f)
            self._owner_id = data.get("owner_id", 0)
            self._api_id = data.get("api_id", 0)
            self._api_hash = data.get("api_hash", "")
            self._driver_bot_token = data.get("driver_bot_token", "")
            self._rider_bot_token = data.get("rider_bot_token", "")
            self._driver_group_id = data.get("driver_group_id", 0)
            self._driver_group_invite_link = data.get("driver_group_invite_link", "")
            self._sms_api_token = data.get("sms_api_token", "")
            self._google_api_key = data.get("google_api_key", "")
            self._upi_id = data.get("upi_id", "")
            self._upi_name = data.get("upi_name", "")
            self._upi_mode = data.get("upi_mode", "")
            self._upi_purpose = data.get("upi_purpose", "")
            self._bot_shared_chat_for_privacy_id = data.get(
                "bot_shared_chat_for_privacy_id", 0
            )

    def __validate_and_load_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump(self.__example_file(), f)
            raise FileNotFoundError(
                f"Config file not found: {self.file_path}. Generated example file."
            )
        if not os.path.isfile(self.file_path):
            raise NotADirectoryError(f"Config file is not a file: {self.file_path}")
        self.__load()
        logger.info(f"Loaded config file: {self.file_path}")

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(
                {
                    "owner_id": self._owner_id,
                    "api_id": self._api_id,
                    "api_hash": self._api_hash,
                    "driver_bot_token": self._driver_bot_token,
                    "rider_bot_token": self._rider_bot_token,
                    "driver_group_id": self._driver_group_id,
                    "driver_group_invite_link": self._driver_group_invite_link,
                    "sms_api_token": self._sms_api_token,
                    "google_api_key": self._google_api_key,
                    "upi_id": self._upi_id,
                    "upi_name": self._upi_name,
                    "upi_mode": self._upi_mode,
                    "upi_purpose": self._upi_purpose,
                    "bot_shared_chat_for_privacy_id": self._bot_shared_chat_for_privacy_id,
                },
                f,
                indent=4,
                separators=(",", ": "),
            )

    @property
    def owner_id(self) -> int:
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value: int):
        self._owner_id = value
        self.save()

    @property
    def api_id(self) -> int:
        return self._api_id

    @api_id.setter
    def api_id(self, value: int):
        self._api_id = value
        self.save()

    @property
    def api_hash(self) -> str:
        return self._api_hash

    @api_hash.setter
    def api_hash(self, value: str):
        self._api_hash = value
        self.save()

    @property
    def driver_bot_token(self) -> str:
        return self._driver_bot_token

    @driver_bot_token.setter
    def driver_bot_token(self, value: str):
        self._driver_bot_token = value
        self.save()

    @property
    def rider_bot_token(self) -> str:
        return self._rider_bot_token

    @rider_bot_token.setter
    def rider_bot_token(self, value: str):
        self._rider_bot_token = value
        self.save()

    @property
    def driver_group_id(self) -> int:
        return self._driver_group_id

    @driver_group_id.setter
    def driver_group_id(self, value: int):
        self._driver_group_id = value
        self.save()

    @property
    def driver_group_invite_link(self) -> str:
        return self._driver_group_invite_link

    @driver_group_invite_link.setter
    def driver_group_invite_link(self, value: str):
        self._driver_group_invite_link = value
        self.save()

    @property
    def sms_api_token(self) -> str:
        return self._sms_api_token

    @sms_api_token.setter
    def sms_api_token(self, value: str):
        self._sms_api_token = value
        self.save()

    @property
    def google_api_key(self) -> str:
        return self._google_api_key

    @google_api_key.setter
    def google_api_key(self, value: str):
        self._google_api_key = value
        self.save()

    @property
    def upi_id(self) -> str:
        return self._upi_id

    @upi_id.setter
    def upi_id(self, value: str):
        self._upi_id = value
        self.save()

    @property
    def upi_name(self) -> str:
        return self._upi_name

    @upi_name.setter
    def upi_name(self, value: str):
        self._upi_name = value
        self.save()

    @property
    def upi_mode(self) -> str:
        return self._upi_mode

    @upi_mode.setter
    def upi_mode(self, value: str):
        self._upi_mode = value
        self.save()

    @property
    def upi_purpose(self) -> str:
        return self._upi_purpose

    @upi_purpose.setter
    def upi_purpose(self, value: str):
        self._upi_purpose = value
        self.save()

    @property
    def bot_shared_chat_for_privacy_id(self) -> int:
        return self._bot_shared_chat_for_privacy_id

    @bot_shared_chat_for_privacy_id.setter
    def bot_shared_chat_for_privacy_id(self, value: int):
        self._bot_shared_chat_for_privacy_id = value
        self.save()


def init_config(parent_logger=None) -> Config:
    global logger
    if parent_logger:
        logger = parent_logger.getChild("config")

    logger.info("Initializing config")
    cfg = Config("config.json")
    logger.info("Loaded config")
    return cfg
