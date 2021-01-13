# -*- coding: UTF8 -*-

import re
import json
import time
import socket
import logging
import datetime
import ipaddress

from urllib.request import urlopen


def encode_json(dictionary: dict) -> str:
    """
    Takes a dictionary and returns a JSON-encoded string.

    :param dict dictionary: A dictionary.
    :return str: A JSON-encoded string.
    """
    return json.JSONEncoder().encode(dictionary)


def decode_json(json_string: str) -> dict:
    """
    Takes a message as a JSON string and unpacks it to get a dictionary.

    :param str json_string: A message, as a JSON string.
    :return dict: An unverified dictionary. Do not trust this data.
    """
    return json.JSONDecoder().decode(json_string)


def get_timestamp() -> int:
    """
    Returns the actual time as a POSIX seconds timestamp.

    :return int: A timestamp, as POSIX seconds.
    """
    return int(time.time())


def get_date_from_timestamp(timestamp: int) -> str:
    """
    Returns a readable date from the timestamp.

    :param int timestamp: A timestamp, as POSIX seconds.
    :return str: A readable date.
    """
    return datetime.datetime.utcfromtimestamp(timestamp).strftime("%X %x")


def validate_fields(dictionary: dict, struct: dict) -> bool:
    """
    Takes a dictionary and an architecture and checks if the types and structure are valid.
    Recursive only in dictionaries. All other types are not iterated through (e.g. lists).

    Example arch: {"content": str, "meta": {"time_sent": int, "digest": str, "aes": str}}

    :param dict dictionary: A dictionary to check.
    :param dict struct: Dictionary containing the levels of architecture.
    :return bool: True if the fields are valid, False otherwise.
    """
    if not isinstance(dictionary, dict):
        return False
    if not isinstance(struct, dict):
        return False

    if len(dictionary) != len(struct):
        return False
    for field_name, field_value in struct.items():
        if type(field_value) is not type:
            if type(dictionary[field_name]) is not type(field_value):
                return False
            # Calls the function recursively when it stumbles upon a dictionary.
            if not validate_fields(struct[field_name], field_value):
                return False
        else:  # If the value is a type object.
            try:
                if type(field_value) == int:
                    if not is_int(dictionary[field_name]):
                        return False
                elif type(dictionary[field_name]) is not field_value:
                    return False
            except KeyError:
                return False
    return True


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


def is_network_port_valid(port: str) -> bool:
    """
    Tests if the port is valid.

    :param str port: An network port.
    :return bool: True if it is, False otherwise.
    """
    try:
        port = int(port)
    except ValueError:
        logging.debug(f'Could not cast {port!r} to integer.')
        return False

    if not 0 < port < 65536:
        logging.debug(f'Port out of range: {port}')
        return False  # The port is not in the acceptable range.

    return True


def get_local_ip_address(log_ip_addresses: bool = False) -> str:
    """
    Recovers the local address.

    :return str: An IP address (v4 or v6).

    TODO: Problem: Can gather an APIPA address
    """
    host_name = socket.gethostname()
    local_ip_address = socket.gethostbyname(host_name)
    if log_ip_addresses:
        logging.info(f'Gathered local IP address, got {local_ip_address}')
    return local_ip_address


def get_public_ip_address(log_ip_addresses: bool = False) -> str:
    """
    Recovers the public address.

    :return str: An IP address (v4 or v6) or a DNS name.
    """
    url = "http://checkip.dyndns.org"
    request = urlopen(url).read().decode("utf-8")
    # Get IPv4
    global_ip = re.findall(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", request)[0]
    log_msg = f'Requested public IP address to {url!r}'
    if log_ip_addresses:
        log_msg += f', got {global_ip!r}'
    logging.info(log_msg)
    return global_ip
