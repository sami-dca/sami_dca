# -*- coding: UTF8 -*-

import re
import json
import time
import socket
import datetime
import ipaddress

from urllib.request import urlopen

from .config import Config
from .request import Request
from .encryption import Encryption


class Utils:

    @staticmethod
    def encode_json(dictionary: dict) -> str:
        """
        Takes a dictionary and returns a JSON-encoded string.

        :param dict dictionary: A dictionary.
        :return str: A JSON-encoded string.
        """
        return json.JSONEncoder().encode(dictionary)

    @staticmethod
    def decode_json(json_string: str) -> dict:
        """
        Takes a message as a JSON string and unpacks it to get a dictionary.

        :param str json_string: A message, as a JSON string.
        :return dict: An unverified dictionary. Do not trust this data.
        """
        return json.JSONDecoder().decode(json_string)

    @staticmethod
    def get_timestamp() -> int:
        """
        Returns the actual time as a POSIX seconds timestamp.

        :return int: A timestamp, as POSIX seconds.
        """
        return int(time.time())

    @staticmethod
    def get_date_from_timestamp(timestamp: int) -> str:
        """
        Returns a readable date from the timestamp.

        :param int timestamp: A timestamp, as POSIX seconds.
        :return str: A readable date.
        """
        return datetime.datetime.utcfromtimestamp(timestamp).strftime("%X %x")

    @staticmethod
    def _validate_fields(dictionary: dict, arch: dict) -> bool:
        """
        Takes a dictionary and an architecture and checks if the types and structure are valid.
        Recursive only in dictionaries. All other types are not iterated through (e.g. lists).

        Example arch: {"content": str, "meta": {"time_sent": int, "digest": str, "aes": str}}

        :param dict dictionary: A dictionary to check.
        :param dict arch: Dictionary containing the levels of architecture.
        :return bool: True if the fields are valid, False otherwise.
        """
        if len(dictionary) != len(arch):
            return False
        for field_name, field_value in arch.items():
            if type(field_value) is not type:
                if type(dictionary[field_name]) is not type(field_value):
                    return False
                # Calls the function recursively when it stumbles upon a dictionary.
                if not Utils._validate_fields(arch[field_name], field_value):
                    return False
            else:  # If the value is a type object.
                try:
                    if type(field_value) == int:
                        if not Utils.is_int(dictionary[field_name]):
                            return False
                    elif type(dictionary[field_name]) is not field_value:
                        return False
                except KeyError:
                    return False
        return True

    @staticmethod
    def is_int(value) -> bool:
        """
        Tests a value to check if it is an integer or not.
        "value" can be of any type, as long as it can be converted to int.
        """
        try:
            int(value)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def is_address_valid(address: str) -> bool:
        """
        Tests if an IP address is valid.

        :param str address: An IP address.
        :return bool: True if it is, False otherwise.
        """

        def is_fqdn(hostname: str) -> bool:
            """
            https://en.m.wikipedia.org/wiki/Fully_qualified_domain_name
            """
            if not 1 < len(hostname) < 253:
                return False

            # Remove trailing dot
            if hostname.endswith('.'):
                hostname = hostname[0:-1]

            #  Split hostname into list of DNS labels
            labels = hostname.split('.')

            #  Define pattern of DNS label
            #  Can begin and end with a number or letter only
            #  Can contain hyphens, a-z, A-Z, 0-9
            #  1 - 63 chars allowed
            fqdn = re.compile(r'^[a-z0-9]([a-z-0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)

            # Check that all labels match that pattern.
            return all(fqdn.match(label) for label in labels)
        # End of function is_fqdn().

        # Tries to convert the first part to an IP address.
        try:
            ipaddress.ip_address(address)
        except ValueError:
            # If it doesn't work, tries to check if it can be a DNS name.
            if not is_fqdn(address):
                return False

        return True

    @staticmethod
    def is_network_port_valid(port: str) -> bool:
        """
        Tests if the port is valid.

        :param str port: An network port.
        :return bool: True if it is, False otherwise.
        """
        try:
            port = int(port)
        except ValueError:
            return False

        if 0 < port < 65536:
            return False  # The port is not in the acceptable range.

        return True

    @staticmethod
    def compute_pow(request: Request) -> Request:
        """
        Takes a request and returns the same with an additional nonce.
        This nonce is computed with a Proof-of-Work algorithm.

        :param Request request:
        :return Request:
        """
        difficulty = Config.pow_difficulty
        limit = 10 * (difficulty + 1)
        # We limit the PoW iterations.
        # If we reach this limit (next "else" loop),
        # we issue an error.
        for n in range(10 * limit):
            request.set_nonce(n)
            j: str = request.to_json()
            h = Encryption.hash_iterable(j)
            hx = h.hexdigest
            if hx[0:difficulty] == "0" * difficulty:
                break
        else:
            raise ValueError("Could not compute Proof-of-Work.")
        return request

    @staticmethod
    def get_local_ip_address() -> str:
        """
        Recovers the local address.

        :return str: An IP address (v4 or v6).
        """
        host_name = socket.gethostname()
        local_ip_address = socket.gethostbyname(host_name)
        return local_ip_address

    @staticmethod
    def get_public_ip_address() -> str:
        """
        Recovers the public address.

        :return str: An IP address (v4 or v6) or a DNS name.
        """
        url = "http://checkip.dyndns.org"
        request = urlopen(url).read().decode("utf-8")
        # Get IPv4
        global_ip = re.findall(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", request)[0]
        return global_ip
