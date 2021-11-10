from pathlib import Path
from typing import Optional

from ._base import Node
from ..utils import get_id
from ..design import Singleton
from ..config import Identifier
from ..cryptography.asymmetric import PrivateKey


class MasterNode(Node, Singleton):

    def __init__(self, private_key: PrivateKey):
        self.private_key: PrivateKey = private_key
        self.public_key = self.private_key.get_public_key()
        self._hash = self.public_key.get_public_key_hash()
        self.sig = self._compute_own_sig()
        super().__init__(self.public_key, self.sig)

    def _compute_own_sig(self) -> str:
        return self.private_key.get_signature(self._hash)

    def _compute_id(self) -> Identifier:
        return get_id(self._hash)

    def export_private_key(self, directory: Path,
                           passphrase: Optional[str] = None) -> None:
        file_path = directory / f"rsa_private_key-{self.id}.pem"
        self.private_key._to_file(file_path, passphrase)


def is_private_key_loaded() -> bool:
    """
    Checks whether the private key has been loaded.
    If this methods returns False, then private databases and cryptographic
    operations won't work.
    """
    try:
        MasterNode()
    except TypeError:
        # Catch "missing argument" errors
        return False
    else:
        return True
