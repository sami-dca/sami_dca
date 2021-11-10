import json
import time
import datetime

from typing import List, Dict, Any, Optional, Union

from Crypto.Hash import SHA256

from ..config import Identifier
from ..cryptography.hashing import hash_object


def encode_json(dictionary: dict) -> str:
    """
    Takes a dictionary and returns a JSON-encoded string.
    """
    return json.JSONEncoder().encode(dictionary)


def decode_json(json_string: str) -> dict:
    """
    Takes a message as a JSON string and unpacks it to get a dictionary.
    """
    return json.JSONDecoder().decode(json_string)


def get_time() -> int:
    """
    Returns the actual time as a UNIX timestamp.
    """
    # TODO: use SAMI timestamp (UNIX timestamp minus release date)
    #  time - 1577833200  (first january 2020)
    return round(time.time(), None)


def get_date_from_timestamp(timestamp: int) -> str:
    """
    Returns a readable date from a UNIX timestamp.
    """
    return datetime.datetime.utcfromtimestamp(timestamp).strftime("%X %x")


def object_transfer(src, dst,
                    additional_exclude_arguments: Optional[List[str]] = None):
    """
    Utility function used to translate attributes from an object
    instance to a different object.

    FIXME: deprecated, remove this
    """

    VarsType = Dict[str, Any]

    def filter_dunders(d: VarsType) -> VarsType:
        """
        Takes a dict of attributes and filters out dunders
        """
        return {
            k: v
            for k, v in d.items()
            if not any([k.startswith('_'), k.endswith('_')])
        }

    def remove_attributes(d: VarsType,
                          excluded_attrs: List[str]) -> VarsType:
        return {
            k: v
            for k, v in d.items()
            if k not in excluded_attrs
        }

    exclude_arguments = ['id']
    if additional_exclude_arguments:
        exclude_arguments.extend(additional_exclude_arguments)

    src_attributes: dict = vars(src)
    src_attributes = filter_dunders(src_attributes)
    src_attributes = remove_attributes(src_attributes, exclude_arguments)

    return dst(**src_attributes)


def is_int(value: Any) -> bool:
    try:
        int(value)
    except (ValueError, TypeError):
        return False
    else:
        return True


def is_float(value: Any) -> bool:
    try:
        float(value)
    except (ValueError, TypeError):
        return False
    else:
        return True


_valid_characters: str = (
    '0123456789'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '!"#$%&\'()*+,-./:;<=>?[\\]^_`{|}~'
)
max_base = len(_valid_characters) + 1


def switch_base(value: Union[int, str], from_base: int,
                to_base: int) -> Union[int, str]:
    """
    Takes a value, and converts it from one base to another.
    Raises ValueError if the value is not in bounds of its indicated base.

    Warning: this is a completely custom base-to-base converter, it might work
    with other converters for bases between 2 and 36, but it is generally not
    advised to use it anyway.

    To get the maximum base available, use the global variable `max_base`.
    Minimal base is always 2.

    :returns: The value, in the target base.
              Type int if `to_base <= 10`, str otherwise.
    :raises ValueError: If the value is not in bounds of its indicated base.
    :raises AssertionError: If either `from_base` or `to_base` is unsupported.
    """
    assert 2 <= from_base <= max_base
    assert 2 <= to_base <= max_base

    # Convert the value to decimal
    # FIXME: using int only works for a limited base range
    value = int(value, from_base)

    final_value_parts: List[str] = []
    while value != 0:
        remainder = value % to_base
        remainder_translation = _valid_characters[remainder]
        final_value_parts.append(remainder_translation)
        value //= to_base

    final_value = ''.join(reversed(final_value_parts))

    if to_base <= 10:
        return int(final_value)
    else:
        return final_value


def get_id(h: SHA256.SHA256Hash) -> Identifier:
    return h.hexdigest()


def compress_id(identifier: Identifier) -> str:
    return switch_base(
        value=identifier,
        from_base=16,
        to_base=max_base,
    )


def uncompress_id(compressed_id: str) -> Identifier:
    return switch_base(
        value=compressed_id,
        from_base=max_base,
        to_base=16,
    )
