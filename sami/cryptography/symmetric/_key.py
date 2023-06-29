from __future__ import annotations

import logging as _logging
from functools import cached_property

import pydantic
from Crypto.Cipher import AES

from ...config import Identifier, settings
from ...utils import get_id
from ..hashing import hash_object
from ..serialization import (
    decode_bytes,
    deserialize_string,
    encode_string,
    serialize_bytes,
)
from ._key_part import SymmetricKeyPart

logger = _logging.getLogger("cryptography")


class SymmetricKey(pydantic.BaseModel):
    value: bytes
    nonce: bytes

    class Config:
        allow_mutation = False

    @classmethod
    @pydantic.validator("value")
    def _check_key(cls, key: bytes):
        assert len(key) == settings.aes_keys_length, "Incorrect value length"
        return key

    @staticmethod
    def derive_nonce_from_key(key: bytes) -> bytes:
        return hash_object(key).digest()[: settings.aes_keys_length // 2]

    @classmethod
    def from_parts(cls, parts: set[SymmetricKeyPart]) -> SymmetricKey | None:
        """
        Takes the parts of a value, and reconstructs it.
        Returns None if one or more part is missing.
        """
        if not sum(len(part) for part in parts) == settings.aes_keys_length:
            # Missing part(s)
            return
        # Assemble the value parts
        value = b"".join(
            sorted(
                (part.value for part in parts),
                key=lambda key_part: key_part.id,
            )
        )
        return cls(
            value=value,
            nonce=cls.derive_nonce_from_key(value),
        )

    @cached_property
    def _aes(self):
        return AES.new(
            key=self.value,
            nonce=self.nonce,
            mode=settings.aes_mode,
        )

    @cached_property
    def id(self) -> Identifier:
        return get_id(hash_object([self.value, self.nonce]))


class EncryptionKey(SymmetricKey):
    """
    Stateful encrypting value.
    """

    @classmethod
    def from_key(cls, key: SymmetricKey) -> EncryptionKey:
        return cls(
            value=key.value,
            nonce=key.nonce,
        )

    def encrypt_raw(self, data: str) -> tuple[str, str]:
        """
        Encrypts and serializes data.
        Returns a tuple with (1) the serialized and encrypted data and
        (2) the tag.
        Must be reversible with decrypt_raw().
        """
        en_data, tag = self._aes.encrypt_and_digest(encode_string(data))
        se_en_data = serialize_bytes(en_data)
        se_tag = serialize_bytes(tag)
        return se_en_data, se_tag


class DecryptionKey(SymmetricKey):
    """
    Stateful decrypting value.
    """

    @classmethod
    def from_key(cls, key: SymmetricKey) -> DecryptionKey:
        return cls(
            value=key.value,
            nonce=key.nonce,
        )

    def decrypt_raw(self, se_en_data: str, se_tag: str) -> str:
        """
        Deserializes and decrypts data.
        Must be reversible with encrypt_raw().
        Returns None if we cannot decrypt.
        """
        en_data = deserialize_string(se_en_data)
        tag = deserialize_string(se_tag)
        data = self._aes.decrypt_and_verify(en_data, tag)
        return decode_bytes(data)
