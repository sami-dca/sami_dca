from __future__ import annotations

import logging as _logging
from functools import cached_property

import pydantic

from ...config import Identifier, settings
from ...objects import Node
from ...utils import get_id, hamming_distance
from ..hashing import hash_object

logger = _logging.getLogger("cryptography")


def get_expected_key_length(members: set[Node], identifier: Identifier) -> int:
    def get_designated(
        value: Identifier, possibilities: list[Identifier]
    ) -> Identifier:
        """
        Designate a member for creating the filling value part.
        """
        return sorted(
            possibilities,
            key=lambda i: hamming_distance(str(value), str(i)),  # FIXME
        )[0]

    identifiers = sorted(node.id for node in members)
    common_identifier = get_id(hash_object(identifiers))
    designated_member = get_designated(common_identifier, identifiers)

    remainder = settings.aes_keys_length % len(members)
    floor = settings.aes_keys_length // len(members)

    if designated_member == identifier:
        return remainder + floor
    else:
        return floor


class SymmetricKeyPart(pydantic.BaseModel):
    value: bytes
    author: Node
    # FIXME: probably needs a signature from the author
    #  Also, check it was actually generated for this conversation

    def __len__(self) -> int:
        return len(self.value)

    @cached_property
    def id(self) -> Identifier:
        return get_id(hash_object([self.value]))
