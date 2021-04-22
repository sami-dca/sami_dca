# -*- coding: UTF8 -*-

import re
import copy
import json
import time
import socket
import logging
import datetime

from typing import Set
from difflib import get_close_matches

from urllib.request import urlopen

from .config import Config


def resettable(f):
    # From https://stackoverflow.com/a/4866695/9084059

    def __init_and_copy__(self, *args, **kwargs):
        f(self, *args, **kwargs)
        self.__original_dict__ = copy.deepcopy(self.__dict__)

        def reset(o=self):
            o.__dict__ = o.__original_dict__

        self.reset = reset

    return __init_and_copy__


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


def is_int(value) -> bool:
    """
    Tests a value to check if it is an integer or not.
    "value" can be of any type, as long as it can be converted to int.
    Note: `is_int(None)` will raise TypeError.
    """
    try:
        int(value)
    except ValueError:
        return False
    else:
        return True


###################
# Network section #
###################


def get_public_ip_address() -> str:
    """
    Recovers the public address.

    :return str: An IP address (v4 or v6) or a DNS name.
    """
    url = "http://checkip.dyndns.org"
    request = urlopen(url).read().decode("utf-8")
    # Get IPv4
    global_ip = re.findall(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", request)[0]
    if Config.log_ip_addresses and Config.log_utils:
        logging.debug(f'Requested public IP address to {url!r}, got {global_ip!r}')
    return global_ip


def get_all_local_ip_addresses() -> Set[str]:
    """
    Gets all addresses assigned on our network interfaces (virtual and physical).
    """
    host_name, aliases, local_ip_addresses = socket.gethostbyname_ex(socket.gethostname())
    local_ip_addresses = set(local_ip_addresses)
    log_msg = 'Requested all local IPs'
    if Config.log_ip_addresses:
        log_msg += f', got {local_ip_addresses}'
    if Config.log_utils:
        logging.info(log_msg)
    return local_ip_addresses


def get_primary_local_ip_address() -> str:
    """
    Gets default IP address, as returned by ``socket.gethostbyname()``.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = socket.gethostbyname(socket.gethostname())
    finally:
        s.close()

    if Config.log_ip_addresses and Config.log_utils:
        logging.debug(f'Requested primary local IP, got {ip_address!r}')
    return ip_address


def get_local_ip_address_from_address(neighbor_address: str) -> str:
    """
    Gets the local ip address, depending on the IP we try to contact.
    We make a diff between the neighbor_address and the addresses we gather from the local system,
    and select the closest one.

    :param str neighbor_address: A valid IP address.
    :return str: An IP address (v4 or v6).

    TODO: Problem: Can gather an APIPA address
    """
    # TODO: Add validation for local/public IPs.

    local_ip_addresses = get_all_local_ip_addresses()
    ip = None
    cutoff = 1.0
    if not local_ip_addresses:
        raise ProcessLookupError("Couldn't find a local ip address.")
    else:
        while not ip:
            try:
                ip = get_close_matches(neighbor_address, local_ip_addresses, n=1)[0]
            except IndexError:
                cutoff -= 0.1
                continue
        if Config.log_ip_addresses and Config.log_utils:
            logging.debug(f'Request local IP address depending on another IP, got {ip} ({cutoff=})')
        return ip


def is_own_local_ip(ip_address: str) -> bool:
    return ip_address in get_all_local_ip_addresses()
