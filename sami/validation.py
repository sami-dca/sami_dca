# -*- coding: UTF8 -*-

import re
import logging
import ipaddress

from functools import wraps

from .utils import is_int
from .config import Config
from .encryption import Encryption
from .structures import Structures


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
        if Config.log_validation:
            logging.error(f"Expected dict as argument 'dictionary', got {type(dictionary)}: {dictionary!r}")
        return False
    if not isinstance(struct, dict):
        if Config.log_validation:
            logging.error(f"Excepted dict as argument 'struct', got {type(struct)}: {struct}")
        return False

    if len(dictionary) != len(struct):
        if Config.log_validation:
            log_msg = f'Lengths do not match: passed dict is {len(dictionary)}, expected {len(struct)}'
            if Config.verbose:
                log_msg += f' (passed {dictionary}, expected {struct})'
            logging.error(log_msg)
        return False

    for key, struct_value in struct.items():
        try:
            dict_value = dictionary[key]
        except KeyError:
            if Config.log_validation:
                logging.error(f"Couldn't find field {key!r} in passed dictionary")
            return False
        if isinstance(struct_value, type):
            # If value is a type object, we want to check that the value from the dict is of this type.
            if not isinstance(dict_value, struct_value):
                if Config.log_validation:
                    logging.error(f'Expected {struct_value} for {key!r}, got {type(dict_value)}')
                return False
            if struct_value is int:
                if not is_int(dict_value):
                    if Config.log_validation:
                        logging.error(f"Couldn't cast to int: {key!r}: {dict_value!r}")
                    return False
        elif isinstance(struct_value, dict):
            # If value is a dict, we want to call this function recursively.
            if not validate_fields(dict_value, struct_value):
                return False
    return True


def verify_received_aes_key(key: dict, rsa_public_key) -> bool:
    """
    Verifies the AES key received as a dict and passed here is valid.

    :param dict key: An AES key, as a dictionary.
    :param rsa_public_key: The RSA public key of the author.
    :return bool: True if the information is a valid AES key, False otherwise.
    """
    if not validate_fields(key, Structures.aes_key_structure):
        return False
    value = key["value"]
    h_str = key["hash"]
    sig = Encryption.deserialize_string(key["sig"])
    h = Encryption.hash_iterable(value)
    expected_digest = h.hexdigest()
    if h_str != expected_digest:
        if Config.log_validation:
            logging.error(f'Failed to validate key: indicated digest ({h_str!r}) '
                          f'is different from the one computed ({expected_digest})')
        return False
    if not Encryption.is_signature_valid(rsa_public_key, h, sig):
        return False
    return True


def is_valid_request(request: dict) -> bool:
    """
    Takes a request as a JSON-encoded string and checks it is valid.
    Valid does not mean trustworthy.

    :param str request: A JSON-encoded dictionary.
    """
    if not validate_fields(request, Structures.request_standard_structure):
        return False
    return True


def is_valid_contact(contact_data: dict) -> bool:
    """
    Checks if the dictionary passed contains valid contact information.

    :param dict contact_data: A contact, as a dictionary.
    :return bool: True if it is valid, False otherwise.
    """
    if not validate_fields(contact_data, Structures.simple_contact_structure):
        return False

    # Validate address and port.
    address: list = contact_data["address"].split(Config.contact_delimiter)

    if len(address) != 2:
        if Config.log_validation:
            logging.error(f'Splitting expected 2 values, got {len(address)}: {address!r}')
        return False

    ip_address, port = address

    if not is_address_valid(ip_address):
        if Config.log_validation:
            logging.error(f'Invalid address: {ip_address!r}')
        return False
    if not is_network_port_valid(port):
        if Config.log_validation:
            logging.error(f'Invalid port: {port!r}')
        return False

    return True


def is_valid_node(node_data: dict) -> bool:
    """
    Validates all the fields of a node.

    :param dict node_data: The dict containing the information to validate.
    :return bool: True if the node information is correct, False otherwise.
    """
    if not validate_fields(node_data, Structures.node_structure):
        return False

    # Verify the RSA pubkey
    try:
        node_pubkey = Encryption.construct_rsa_object(node_data['rsa_n'], node_data['rsa_e'])
    except ValueError:
        return False  # Invalid modulus and/or exponent -> invalid RSA key.

    # Verify that the pubkey RSA modulus length is corresponding to the expected key length.
    # Note : with L being the key length in bits, 2**(L-1) <= N < 2**L
    if node_pubkey.size_in_bits() != Config.rsa_keys_length:
        return False  # RSA keys are not the correct size.

    # Create a hash of the node's information.
    hash_object = Encryption.get_public_key_hash(node_pubkey)

    # Verify hash
    if hash_object.hexdigest() != node_data['hash']:
        return False  # Hash is incorrect.

    # Verify signature
    if not Encryption.is_signature_valid(node_pubkey, hash_object, Encryption.deserialize_string(node_data['sig'])):
        return False  # Signature is invalid

    return True


def is_valid_received_message(message_data: dict) -> bool:
    """
    Performs tests on the data passed to check messages we receive are correct.
    AFAIK, it's not possible to verify the digest without decrypting the message,
    that's why we don't perform this test here.

    :param dict message_data: A message, as a dict.
    :return bool: True if it is, False otherwise.
    """
    if not validate_fields(message_data, Structures.received_message_structure):
        return False

    if not is_valid_node(message_data["author"]):
        return False

    return True


def validate_export_structure(*struct_name):
    """
    Decorator used to validate a `to_dict` method returns the expected values.
    See `structures.py` for all structures and the string to structure mapping.
    """

    if len(list(struct_name)) != 1:
        msg = "Invalid arguments passed to the decorator."
        logging.critical(msg)
        raise Exception(msg)

    m = struct_name[0]

    struct = Structures.mapping(m)
    if not struct:
        msg = f"Invalid struct name: {m!r}."
        logging.critical(msg)
        raise Exception(msg)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            dic = func(*args, **kwargs)
            if validate_fields(dic, struct):
                return dic
            else:
                msg = "Invalid export structure."
                logging.critical(msg)
                raise ValueError(msg)
        return wrapper

    return decorator


###################
# Network section #
###################


def is_ip_address_valid(address: str) -> bool:
    try:
        ipaddress.ip_address(address)
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

        #  Split hostname into a list of DNS labels
        labels = hostname.split('.')

        #  Define pattern of DNS label
        #  Can begin and end with a number or letter only
        #  Can contain hyphens, a-z, A-Z, 0-9
        #  1 - 63 chars allowed
        fqdn = re.compile(r'^[a-z0-9]([a-z-0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)

        # Check that all labels match that pattern.
        return all(fqdn.match(label) for label in labels)
    # End of function is_fqdn().

    if not is_ip_address_valid(address):
        # Try to check if it can be a DNS name.
        if not is_fqdn(address):
            return False

    return True


def is_network_port_valid(port: str) -> bool:
    """
    Tests if the port is valid.

    :param str port: A network port.
    :return bool: True if it is, False otherwise.
    """
    try:
        port = int(port)
    except ValueError:
        if Config.log_validation:
            logging.debug(f'Could not cast port {port!r} to integer.')
        return False

    if not 0 < port < 65536:
        if Config.log_validation:
            logging.debug(f'Port out of range: {port}')
        return False

    return True
