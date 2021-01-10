# -*- coding: UTF8 -*-

import logging

from functools import wraps

from .config import Config
from .encryption import Encryption
from .structures import Structures
from .utils import validate_fields, is_address_valid, is_network_port_valid


def is_valid_request(request: dict) -> bool:
    """
    Takes a request as a JSON-encoded request and checks it is valid.
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
        logging.debug(f'Splitting returned {len(address)} values instead of expected 2: {address!r}')
        return False

    ip_address, port = address

    if not is_address_valid(ip_address):
        logging.debug(f'Invalid address: {ip_address!r}')
        return False
    if not is_network_port_valid(port):
        logging.debug(f'Invalid port: {port!r}')
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
    Performs tests on the data passed to check if the message we just received is correct.

    :param dict message_data: A message, as a dict.
    :return bool: True if it is, False otherwise.

    TODO: Verify digest
    """
    if not validate_fields(message_data, Structures.received_message_structure):
        return False

    if not is_valid_node(message_data["author"]):
        return False

    return True


def validate_export_structure(*struct_name):
    if len(list(struct_name)) != 1:
        raise Exception('Invalid arguments passed to the decorator.')

    m = struct_name[0]

    struct = Structures.mapping(m)
    if not struct:
        raise Exception(f'Invalid struct name: {m!r}.')

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            dic = func(*args, **kwargs)
            if validate_fields(dic, struct):
                return dic
            else:
                raise ValueError("Invalid export structure.")
        return wrapper

    return decorator
