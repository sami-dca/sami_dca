import json
import time

from datetime import datetime
from typing import List, Any, Union

from Crypto.Hash import SHA256

from ..config import Identifier, sami_start, max_base, valid_base_characters


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
    Returns the current time as a SAMI timestamp (seconds since the epoch,
    minus the UNIX timestamp of the Sami's birth).
    """
    return round(time.time(), None) - sami_start


def get_date_from_timestamp(timestamp: int) -> str:
    """
    Returns a readable date from a UNIX timestamp.
    """
    return datetime.utcfromtimestamp(timestamp).strftime("%X %x")


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
    value = int(str(value), from_base)

    final_value_parts: List[str] = []
    while value != 0:
        remainder = value % to_base
        remainder_translation = valid_base_characters[remainder]
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


def hamming_distance(first_string: str, second_string: str) -> int:
    """
    From https://en.wikipedia.org/wiki/Hamming_distance
    """
    usable_range = range(min([len(first_string), len(second_string)]))
    distance = 0
    for i in usable_range:
        if first_string[i] != second_string[i]:
            distance += 1
    return distance
