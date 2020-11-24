# -*- coding: UTF8 -*-

from dataclasses import dataclass

from .utils import Utils
from .config import Config
from .encryption import Encryption
from .structures import Structures


@dataclass
class Contact:
    address: str  # An address, IP or DNS name.
    port: int  # A network port.
    last_seen: int  # A timestamp, as POSIX seconds.

    # Validation section

    @staticmethod
    def is_valid(contact_data: dict) -> bool:
        """
        Checks if the dictionary passed contains valid contact information.

        :param dict contact_data: A contact, as a dictionary.
        :return bool: True if it is valid, False otherwise.
        """
        if not Utils._validate_fields(contact_data, Structures.simple_contact_structure):
            return False

        # Validate address and port.
        address: list = contact_data["address"].split(':')

        if len(address) != 2:
            return False

        ip_address, port = address

        if not Utils.is_address_valid(ip_address):
            return False
        if not Utils.is_network_port_valid(port):
            return False

        # Validate last_seen.
        #try:
        #    if int(contact_data["last_seen"]) not in range(0, Utils.get_timestamp() + 1):
        #        return False  # Node is from the future ! Ask him about WW3 !
        #except ValueError:
        #    return False  # last_seen in not an integer, therefore not a valid timestamp.

        return True

    # Class methods section

    @classmethod
    def from_dict(cls, contact_data: dict, last_seen: int = None):
        """
        Creates a new object of this class from a contact information.

        :param dict contact_data: Contact data, as a dictionary.
        :param int last_seen: Optional.
        :return: A new object (instance) of this class.
        """
        address, port = contact_data["address"].split(":")
        if last_seen is None:
            try:
                last_seen = contact_data["last_seen"]
            except KeyError:
                last_seen = Utils.get_timestamp()
        return cls(address, port, last_seen)

    @classmethod
    def from_raw_address(cls, raw_address: str):
        address, port = raw_address.split(":")
        return cls(address, port, 0)  # 0 ??!!!

    # Information section

    def get_id(self) -> str:
        """
        Get own ID.

        :return str: An ID, as a string. Its length is defined by Config.id_len
        """
        h = Encryption.hash_iterable(":".join([self.address, self.port]))
        return h.hexdigest()[:Config.id_len]

    def get_address(self) -> str or None:
        """
        Gets the contact's address.

        :return str|None: The address if set, None otherwise.
        """
        return self.address

    def get_port(self) -> int or None:
        """
        Gets the contact's network port.

        :return int|None: The network port if set, None otherwise.
        """
        return self.port

    # Last seen section

    def set_last_seen(self) -> None:
        """
        Defines the attribute "last_seen".
        We set it to be right now, because this function must be called when creating a new instance
        (unless a manual timestamp is being passed in the __init__).
        """
        self.last_seen = Utils.get_timestamp()

    def get_last_seen(self) -> int:
        """
        Returns instance's last_seen.

        :return:
        """
        return self.last_seen

    # Export section

    def to_dict(self) -> dict:
        """
        Returns the instance's attributes as a dictionary.
        This dictionary is valid for network communication and database storage.

        :return dict: A contact, as a dictionary.
        """
        return {
            "address": ":".join([self.address, self.port])
        }


class OwnContact:
    def __init__(self):
        self.address = Config.local_ip_address
        self.port = Config.port

    def to_dict(self) -> dict:
        """
        Returns the instance's attributes as a dictionary.
        This dictionary is valid for network communication and database storage.

        :return dict: Our contact, as a dictionary.
        """
        return {
            "address": ":".join([self.address, self.port])
        }
