from __future__ import annotations

import logging as _logging
import random
from pathlib import Path
from typing import Optional

from ..config import Identifier
from ..cryptography.asymmetric import PublicKey
from ..database.base.models import NodeDBO
from ..lib.dictionary import dictionary
from ..structures import NodeStructure
from ..utils import get_id

logger = _logging.getLogger("objects")


class Node:
    def __init__(self, public_key: PublicKey, sig: str):
        # Initialize attributes.
        self.public_key = public_key
        self._hash = self.public_key.get_public_key_hash()
        self._sig = sig

        self.id = self._compute_id()
        self.name = self._compute_name()

    @classmethod
    def from_id(cls, node_id: Identifier) -> Optional[Node]:
        from ..database.private import NodesDatabase

        node_dbo = NodesDatabase().get_node(node_id)
        if node_dbo is None:
            return
        else:
            cls.from_dbo(node_dbo)

    @classmethod
    def from_data(cls, node_data: NodeStructure) -> Optional[Node]:
        public_key = PublicKey.from_components(node_data.rsa_n, node_data.rsa_e)
        sig = node_data.sig
        return cls(
            public_key=public_key,
            sig=sig,
        )

    @classmethod
    def from_dbo(cls, dbo: NodeDBO) -> Node:
        return cls(
            public_key=PublicKey.from_components(dbo.rsa_n, dbo.rsa_e),
            sig=dbo.sig,
        )

    def to_dbo(self) -> NodeDBO:
        return NodeDBO(
            uid=self.id,
            rsa_n=self.public_key._rsa.n,
            rsa_e=self.public_key._rsa.e,
            hash=self._hash.hexdigest(),
            sig=self._sig,
        )

    def to_data(self) -> NodeStructure:
        return NodeStructure(
            rsa_n=self.public_key._rsa.n,
            rsa_e=self.public_key._rsa.e,
            hash=self._hash.hexdigest(),
            sig=self._sig,
        )

    def _compute_id(self) -> Identifier:
        return get_id(self._hash)

    def _compute_name(self) -> str:
        """
        Compute the name of this node.
        """
        # Sets the random number generator's seed.
        random.seed(int(self.id, 16))

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
