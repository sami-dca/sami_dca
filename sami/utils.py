from __future__ import annotations

import random
import time
import traceback
from abc import abstractmethod
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol, runtime_checkable

from Crypto.Hash import SHA256
from loguru import logger

from .config import Identifier, settings


@runtime_checkable
class SupportsComparison(Protocol):
    """An ABC with abstract methods for comparison."""

    __slots__ = ()

    @abstractmethod
    def __eq__(self, other: SupportsComparison) -> bool:
        pass

    @abstractmethod
    def __gt__(self, other: SupportsComparison) -> bool:
        pass

    @abstractmethod
    def __lt__(self, other: SupportsComparison) -> bool:
        pass


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


def switch_base(value: int | str, from_base: int, to_base: int) -> int | str:
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

    if from_base == to_base:
        return value

    # Convert the value to decimal
    # FIXME: using int only works for a limited base range
    value = int(str(value), from_base)

    final_value_parts: list[str] = []
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
    return Identifier(h.hexdigest(), 16)


def hamming_distance(first_object: str, second_object: str) -> int:
    """
    From https://en.wikipedia.org/wiki/Hamming_distance
    """
    usable_range = range(min(len(first_object), len(second_object)))
    distance = 0
    for i in usable_range:
        if first_object[i] != second_object[i]:
            distance += 1
    return distance


def iter_to_dict(iterable: Iterable, /, key: Callable) -> dict[Any, list[Any]]:
    """
    Takes an iterable, such as a list, and returns a dictionary mapping
    each value (the result of the function `value`) to an entry.

    Examples
    --------
    >>> iter_to_dict(["this", "is", "a", "test"], value=lambda val: len(val))
    {4: ["this", "test"], 2: ["is"], 1: ["a"]}
    >>> iter_to_dict(["1", "test", "5", "yes"], value=str.isnumeric)
    {True: ["1", "5"], False: ["test", "yes"]}
    """
    final = defaultdict(list)
    for value in iterable:
        final[key(value)].append(value)
    return dict(final)


def format_err(err: Exception):
    return f"{''.join(traceback.format_tb(err.__traceback__))}\n{str(err)}"


def shuffled(collection: set | list) -> set | list:
    copied = collection.copy()
    random.shuffle(copied)
    return copied


def update():
    # Updates the client using Git.
    try:
        import git

        g = git.cmd.Git(Path(__file__).parent.parent.parent)
        g.pull()
    except ImportError:
        logger.warning("Could not check for software updates.")
