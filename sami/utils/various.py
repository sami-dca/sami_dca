import json
import time
import traceback
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Union

from Crypto.Hash import SHA256

from ..config import Identifier, settings


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
    return round(time.time(), None) - settings.sami_start


def get_date_from_timestamp(timestamp: int) -> str:
    """
    Returns a readable date from a UNIX timestamp.
    """
    return datetime.utcfromtimestamp(timestamp).strftime("%X %x")


def switch_base(
    value: Union[int, str], from_base: int, to_base: int
) -> Union[int, str]:
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
    assert 2 <= from_base <= settings.max_base
    assert 2 <= to_base <= settings.max_base

    # Convert the value to decimal
    # FIXME: using int only works for a limited base range
    value = int(str(value), from_base)

    final_value_parts: List[str] = []
    while value != 0:
        remainder = value % to_base
        remainder_translation = settings.valid_base_characters[remainder]
        final_value_parts.append(remainder_translation)
        value //= to_base

    final_value = "".join(reversed(final_value_parts))

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
        to_base=settings.max_base,
    )


def uncompress_id(compressed_id: str) -> Identifier:
    return switch_base(
        value=compressed_id,
        from_base=settings.max_base,
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


def iter_to_dict(iterable: Iterable, /, key: Callable) -> Dict[Any, List[Any]]:
    """
    Takes an iterable, such as a list, and returns a dictionary mapping
    each value (the result of the function `key`) to an entry.

    Examples
    --------
    >>> iter_to_dict(["this", "is", "a", "test"], key=lambda val: len(val))
    {4: ["this", "test"], 2: ["is"], 1: ["a"]}
    >>> iter_to_dict(["1", "test", "5", "yes"], key=str.isnumeric)
    {True: ["1", "5"], False: ["test", "yes"]}
    """
    final = defaultdict(list)
    for value in iterable:
        final[key(value)].append(value)
    return dict(final)


def format_err(err: Exception):
    return f"{''.join(traceback.format_tb(err.__traceback__))}\n{str(err)}"
