from __future__ import annotations

import logging as _logging
import random
from functools import cached_property
from pathlib import Path

from ...config import Identifier
from ...cryptography.asymmetric import PublicKey
from ...lib.dictionary import dictionary
from ...objects import StoredSamiObject
from ...utils import get_id
from ._pattern import Pattern

logger = _logging.getLogger("objects")


class Node(StoredSamiObject):
    __table_name__ = "nodes"
    __node_specific__ = False

    public_key: PublicKey
    sig: str
    pattern: Pattern

    class Config:
        allow_mutation = False

    @cached_property
    def id(self) -> Identifier:
        return get_id(self.public_key.hash)

    @cached_property
    def name(self) -> str:
        """
        Compute the name of this node.
        """
        # Sets the random number generator's seed.
        random.seed(self.id)

        name_parts = []

        adjectives = dictionary["adjectives"]
        animals = dictionary["animals"]

        # First word, choose an adjective.
        adjective = random.choice(adjectives).capitalize()
        name_parts.append(adjective)

        # Second word, an animal name.
        animal = random.choice(animals).capitalize()
        name_parts.append(animal)

        return "".join(name_parts)

    def export_public_key(self, directory: Path) -> None:
        path = directory / f"rsa_public_key-{self.id}.pem"
        self.public_key._to_file(path)
