from __future__ import annotations

import numpy as np

from typing import Tuple, List, Optional

from Crypto.Cipher import AES

from ...utils import get_id
from ...config import Identifier
from ..hashing import hash_object
from ...nodes.own import MasterNode
from ...database.base.models import KeyDBO
from ...database.private import KeysDatabase
from ...config import aes_keys_length, aes_mode
from ..serialization import serialize_bytes, deserialize_string, \
    encode_string, decode_bytes

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ._key_part import KeyPart

import logging as _logging
logger = _logging.getLogger('cryptography')


class SymmetricKey:

    def __init__(self, key: bytes, nonce: bytes,
                 conversation_id: Identifier):
        self._key = key
        self._aes = AES.new(
            key=self._key,
            nonce=nonce,
            mode=aes_mode,
        )
        self._nonce = nonce
        self.conversation_id = conversation_id
        self.id = self._compute_id()

    @staticmethod
    def derive_nonce_from_bytes(key: bytes) -> bytes:
        return hash_object(key).digest()[:aes_keys_length // 2]

    @classmethod
    def from_id(cls, identifier: Identifier) -> Optional[SymmetricKey]:
        dbo = KeysDatabase().get_symmetric_key(identifier)
        if dbo is None:
            return
        return cls.from_dbo(dbo)

    @classmethod
    def from_parts(cls, parts: List[KeyPart]) -> Optional[SymmetricKey]:
        """
        Takes parts of a key, and reconstructs it.
        Returns None if one or more part is missing.
        """
        key_length = sum([len(part) for part in parts])
        if key_length != aes_keys_length:
            # Missing key parts, or invalid part
            return
        # Sort the parts based on the id
        # TODO: simplify
        parts = np.asarray(parts)
        parts_values = np.apply_along_axis(lambda x: x.id, axis=0, arr=parts)
        order = np.argsort(parts_values)
        key_parts_ordered = np.apply_along_axis(lambda x: x._key_part,
                                                axis=0, arr=parts[order])
        # Concatenate parts
        new_key: bytes = b''.join(key_parts_ordered.to_list())
        assert len(new_key) == aes_keys_length

        conv_id = parts[0].conversation_id
        if not all([part.conversation_id == conv_id for part in parts]):
            # At least one of the key part has an invalid conversation id.
            return

        return cls(
            key=new_key,
            nonce=cls.derive_nonce_from_bytes(new_key),
            conversation_id=conv_id,
        )

    @classmethod
    def from_dbo(cls, dbo: KeyDBO) -> SymmetricKey:
        se_en_key = dbo.key
        se_en_nonce = dbo.nonce

        master_node: MasterNode = MasterNode()
        key = master_node.private_key.decrypt_asymmetric(se_en_key)
        nonce = master_node.private_key.decrypt_asymmetric(se_en_nonce)

        return cls(
            key=deserialize_string(key),
            nonce=deserialize_string(nonce),
            conversation_id=dbo.conversation_id,
        )

    def to_dbo(self) -> KeyDBO:
        master_node: MasterNode = MasterNode()
        se_en_key = master_node.private_key.encrypt_asymmetric(serialize_bytes(self._key))
        se_en_nonce = master_node.private_key.encrypt_asymmetric(serialize_bytes(self._nonce))

        return KeyDBO(
            uid=self.id,
            key=se_en_key,
            nonce=se_en_nonce,
            conversation_id=self.conversation_id,
        )

    def store(self) -> None:
        KeysDatabase().store(self.to_dbo())

    def _compute_id(self) -> Identifier:
        return get_id(hash_object([
            self._key,
            self._nonce,
        ]))


class EncryptionKey(SymmetricKey):
    """
    Stateful encrypting key.
    """

    def encrypt_symmetric(self, data: str) -> Tuple[str, str]:
        """
        Encrypts and serializes data.
        Returns a tuple with (1) the serialized and encrypted data and
        (2) the tag.
        Must be reversible with decrypt_symmetric().
        """
        en_data, tag = self._aes.encrypt_and_digest(encode_string(data))
        se_en_data = serialize_bytes(en_data)
        se_tag = serialize_bytes(tag)
        return se_en_data, se_tag


class DecryptionKey(SymmetricKey):
    """
    Stateful decrypting key.
    """

    def decrypt_symmetric(self, se_en_data: str, se_tag: str) -> Optional[str]:
        """
        Deserializes and decrypts data.
        Must be reversible with encrypt_symmetric().
        Returns None if we cannot decrypt.
        """
        en_data = deserialize_string(se_en_data)
        tag = deserialize_string(se_tag)
        data = self._aes.decrypt_and_verify(en_data, tag)
        return decode_bytes(data)
