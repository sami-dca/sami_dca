from __future__ import annotations

import logging as _logging
from typing import List, Optional, Tuple

import numpy as np
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from ..config import Identifier, aes_keys_length, aes_mode, identifier_base
from ..database.base.models import KeyDBO, KeyPartDBO
from ..database.private import KeyPartsDatabase, KeysDatabase
from ..messages import Conversation
from ..nodes import Node
from ..nodes.own import MasterNode
from ..structures import KEPStructure
from ..utils import get_id, hamming_distance, switch_base
from .hashing import hash_object
from .serialization import (
    decode_bytes,
    deserialize_string,
    encode_string,
    serialize_bytes,
)

logger = _logging.getLogger("cryptography")


class KeyPart:

    """
    Attributes
    ----------

    id: int
        Unique key part identifier.

    conversation: Conversation
        Conversation this incomplete key is part of.

    """

    def __init__(self, key_part: bytes, conversation: Conversation):
        self._key_part = key_part
        self.conversation = conversation
        self.id = self._compute_id()

    @classmethod
    def new(cls, conversation: Conversation) -> KeyPart:
        """
        Constructs a new key.
        Adopts the appropriate length depending on the number of members in the
        conversation.
        """

        def get_designated(
            value: Identifier, possibilities: List[Identifier]
        ) -> Identifier:
            """
            Designate a member for creating the filling key part.
            """
            binary_target = switch_base(value, identifier_base, 2)
            distances = {
                possibility: hamming_distance(
                    binary_target,
                    switch_base(possibility, identifier_base, 2),
                )
                for possibility in possibilities
            }
            sorted_distances = dict(
                sorted(
                    distances,
                    key=lambda pair: pair[1],
                    reverse=False,
                )
            )
            # Even though there might be two keys with the same distance,
            # sorting is deterministic, so we will get the same choice
            # regardless.
            return list(sorted_distances.keys())[0]

        remainder = aes_keys_length % len(conversation.members)
        floor = aes_keys_length // len(conversation.members)

        identifiers = [node.id for node in conversation.members]
        identifiers.sort()
        identifier = get_id(hash_object(identifiers))

        designated_member = get_designated(identifier, identifiers)
        master_node = MasterNode()
        if designated_member == master_node.id:
            key_length = remainder + floor
        else:
            key_length = floor

        return cls(
            key_part=get_random_bytes(key_length),
            conversation=conversation,
        )

    @classmethod
    def from_id(cls, identifier: Identifier) -> Optional[KeyPart]:
        dbo = KeyPartsDatabase().get_incomplete_key(identifier)
        if dbo is None:
            return
        return cls.from_dbo(dbo)

    @classmethod
    def from_data(cls, key_part_data: KEPStructure) -> Optional[KeyPart]:
        """
        Takes a key part as an encrypted dictionary, and will try to decrypt it
        to return a KeyPart.
        If decryption fails, we return None.
        """
        enc_key_part = key_part_data.key_part
        part_hash = key_part_data.hash
        part_sig = key_part_data.sig

        members = [Node.from_data(member) for member in key_part_data.members]
        if any([member is None for member in members]):
            # At least one of the specified nodes is invalid
            return
        conversation = Conversation(members)

        author_node = Node.from_data(key_part_data.author)
        if author_node is None:
            # Node data is invalid
            return

        master_node = MasterNode()
        key_part_str = master_node.private_key.decrypt_asymmetric(enc_key_part)
        if key_part_str is None:
            # The key part is not meant for us
            return

        key_part_bytes = encode_string(key_part_str)
        h = hash_object(key_part_bytes)
        if h.hexdigest() != part_hash:
            # Hashes do not match
            return

        if not author_node.public_key.is_signature_valid(h, part_sig):
            # Signature is invalid
            return

        return KeyPart(
            key_part=encode_string(key_part_str),
            conversation=conversation,
        )

    @classmethod
    def from_dbo(cls, dbo: KeyPartDBO):
        se_en_half_key = dbo.key_part

        master_node = MasterNode()
        half_key = master_node.private_key.decrypt_asymmetric(se_en_half_key)

        return cls(
            key_part=deserialize_string(half_key),
            conversation=Conversation.from_id(dbo.conversation_id),
        )

    def to_dbo(self) -> KeyPartDBO:
        master_node: MasterNode = MasterNode()
        se_en_key_part = master_node.private_key.encrypt_asymmetric(
            serialize_bytes(self._key_part)
        )

        return KeyPartDBO(
            key_part=se_en_key_part,
            conversation_id=self.conversation.id,
        )

    def store(self) -> None:
        KeyPartsDatabase().store(self.to_dbo())

    def _compute_id(self) -> Identifier:
        return get_id(hash_object([self._key_part]))


class SymmetricKey:
    def __init__(self, key: bytes, nonce: bytes, conversation_id: Identifier):
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
        return hash_object(key).digest()[: aes_keys_length // 2]

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
        # TODO: first assert the length
        # Sort the parts based on the id
        # TODO: simplify
        parts = np.asarray(parts)
        parts_values = np.apply_along_axis(lambda x: x.id, axis=0, arr=parts)
        order = np.argsort(parts_values)
        key_parts_ordered = np.apply_along_axis(
            lambda x: x._key_part, axis=0, arr=parts[order]
        )
        # Concatenate parts
        new_key: bytes = b"".join(key_parts_ordered.to_list())
        assert len(new_key) == aes_keys_length

        # TODO: assert all the parts have the same conversation_id

        return cls(
            key=new_key,
            nonce=cls.derive_nonce_from_bytes(new_key),
            conversation_id=parts[0].conversation_id,
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
        se_en_key = master_node.private_key.encrypt_asymmetric(
            serialize_bytes(self._key)
        )
        se_en_nonce = master_node.private_key.encrypt_asymmetric(
            serialize_bytes(self._nonce)
        )

        return KeyDBO(
            uid=self.id,
            key=se_en_key,
            nonce=se_en_nonce,
            conversation_id=self.conversation_id,
        )

    def store(self) -> None:
        KeysDatabase().store(self.to_dbo())

    def _compute_id(self) -> Identifier:
        return get_id(
            hash_object(
                [
                    self._key,
                    self._nonce,
                ]
            )
        )


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
