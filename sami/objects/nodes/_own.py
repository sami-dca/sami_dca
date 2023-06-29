from __future__ import annotations

from functools import cached_property
from pathlib import Path

from ...cryptography.asymmetric import PrivateKey
from ...design import Singleton
from ._base import Node


class MasterNode(Node, Singleton):
    private_key: PrivateKey

    def __enter__(self) -> MasterNode:
        return self

    def __exit__(self) -> None:
        pass

    @cached_property
    def public_key(self):
        return self.private_key.get_public_key()

    @cached_property
    def sig(self) -> str:
        return self.private_key.get_signature(self.public_key.hash)

    @property
    def pattern(self):
        pass

    def export_private_key(
        self, directory: Path, passphrase: str | None = None
    ) -> None:
        file_path = directory / f"private_key-{self.id}.pem"
        self.private_key._to_file(file_path, passphrase)


def is_private_key_loaded() -> bool:
    """
    Checks whether the private value has been loaded.
    If this method returns False, then private databases and cryptographic
    operations won't work.
    """
    try:
        MasterNode()
    except TypeError:
        # Catches "missing argument" errors, which indicates this is
        # the first time the MasterNode is instantiated, and therefore
        # that the private value has not been loaded!
        return False
    else:
        return True
