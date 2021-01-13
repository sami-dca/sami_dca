# -*- coding: UTF8 -*-

import logging

from .config import Config
from .encryption import Encryption
from .utils import get_timestamp, encode_json
from .validation import validate_export_structure
from .utils import get_local_ip_address, get_public_ip_address


class Contact:
    def __init__(self, address: str, port: int, last_seen: int = None):
        self.address: str = address  # An address, IP or DNS name.
        self.port: int = port  # A network port.
        self.last_seen: int = last_seen  # A timestamp, as POSIX seconds.

    # Class methods section

    @classmethod
    def from_dict(cls, contact_data: dict, last_seen: int = None):
        """
        Creates a new instance of this class from a contact information.
        Data must be validated beforehand.

        :param dict contact_data: Contact data, as a dictionary.
        :param int last_seen: Optional.
        :return: A new object (instance) of this class.
        """
        address, port = contact_data["address"].split(Config.contact_delimiter)
        if not last_seen:
            try:
                last_seen = contact_data["last_seen"]
            except KeyError:
                pass
        return cls(address, int(port), last_seen)

    @classmethod
    def from_raw_address(cls, raw_address: str):
        """
        Creates a new instance of this class from an IP address.

        :param str raw_address:
        :return: A new object (instance) of this class.
        """
        logging.debug(f'Trying to create a new contact object from raw address: {raw_address}')
        address, port = raw_address.split(Config.contact_delimiter)
        return cls(address, int(port))

    # Information section

    def get_id(self) -> str:
        """
        :return str: An ID, as a string. Its length is defined by Config.id_len
        """
        h = Encryption.hash_iterable(Config.contact_delimiter.join([self.address, str(self.port)]))
        return h.hexdigest()[:Config.id_len]

    def get_address(self) -> str or None:
        """
        :return str|None: The address if set, None otherwise.
        """
        return self.address

    def get_port(self) -> int or None:
        """
        :return int|None: The network port if set, None otherwise.
        """
        return self.port

    # Last seen section

    def set_last_seen(self, last_seen: int = None) -> None:
        """
        Sets contact's last seen information.
        If no argument ``last_seen`` is passed, the current timestamp is used.
        """
        if last_seen:
            if self.validate_last_seen(last_seen):
                self.last_seen = last_seen
            else:
                return
        else:
            self.last_seen = get_timestamp()

    def get_last_seen(self) -> int or None:
        """
        Returns instance's last_seen.
        """
        return self.last_seen

    @staticmethod
    def validate_last_seen(last_seen: int) -> bool:
        try:
            if int(last_seen) not in range(0, get_timestamp()):
                return False  # Node is from the future !
        except ValueError:
            return False  # last_seen in not an integer, therefore not a valid timestamp.

    # Export section

    @validate_export_structure('simple_contact_structure')
    def to_dict(self) -> dict:
        return {
            "address": Config.contact_delimiter.join([self.get_address(), str(self.get_port())])
        }

    def to_json(self) -> str:
        return encode_json(self.to_dict())


class OwnContact:
    def __init__(self, n_type: str):
        if n_type == 'private':
            self.address: str = get_local_ip_address()
        elif n_type == 'public':
            self.address: str = get_public_ip_address()
        else:
            logging.error(f'Invalid IP type: {n_type!r}')
        self.port: int = Config.port_receive

    def get_address(self) -> str:
        return self.address

    def get_port(self) -> int:
        return self.port

    def get_id(self) -> str:
        return Contact.get_id(self)  # Dirty hack

    @validate_export_structure('simple_contact_structure')
    def to_dict(self) -> dict:
        return {
            "address": Config.contact_delimiter.join([self.get_address(), str(self.get_port())])
        }

    def to_json(self) -> str:
        return encode_json(self.to_dict())


class Beacon(Contact):
    """
    Placeholder
    """
    pass
