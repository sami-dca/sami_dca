from __future__ import annotations

import logging as _logging
from functools import cached_property
from pathlib import Path

import pydantic
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from ..config import settings
from .hashing import hash_object
from .serialization import (
    decode_bytes,
    deserialize_string,
    encode_string,
    serialize_bytes,
)

logger = _logging.getLogger("cryptography")


class PublicKey(pydantic.BaseModel):

    """
    Asymmetric public encryption key.

    Instantiate with available classmethods to load an existing key.
    To create a new pair, use `PrivateKey.new()`.
    """

    n: int
    e: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rsa = RSA.construct((self.n, self.e), consistency_check=False)

    @classmethod
    @pydantic.root_validator()
    def _rsa_consistency_check(cls, values):
        RSA.construct((values["n"], values["e"]), consistency_check=True)

    @classmethod
    def from_rsa(cls, public_key: RSA.RsaKey):
        return cls(n=public_key.n, e=public_key.e)

    def _to_file(self, file: Path) -> None:
        """
        Takes this key and writes it to a file.
        Use Node.export_public_key.
        """
        with file.open(mode="wb") as f:
            f.write(self._rsa.export_key(format="DER"))

    def get_max_rsa_enc_msg_length(self, sha_len_bits: int = 256) -> int:
        """
        Returns the maximum message length we can encrypt using RSA.
        """
        # Gets the keys length in bytes.
        keys_length = self._rsa.size_in_bytes()
        sha_length = sha_len_bits // 8
        return keys_length - (2 + sha_length * 2)

    def is_private(self) -> bool:
        return self._rsa.has_private()

    def encrypt_asymmetric_raw(self, data: bytes) -> bytes:
        return PKCS1_OAEP.new(self._rsa).encrypt(data)

    def encrypt_asymmetric(self, data: str) -> str:
        """
        Asymmetrically encrypts and serializes data.
        Must be reversible with `decrypt_asymmetric()`.
        """
        return serialize_bytes(self.encrypt_asymmetric_raw(encode_string(data)))

    def is_signature_valid(self, hash_obj: SHA256.SHA256Hash, sig: str) -> bool:
        """
        Takes a signature and checks whether it is valid.
        """
        try:
            pkcs1_15.new(self._rsa).verify(hash_obj, deserialize_string(sig))
        except (ValueError, TypeError):
            return False
        return True

    @cached_property
    def hash(self) -> SHA256.SHA256Hash:
        """
        Returns a hash of the public key.
        """
        return hash_object([self._rsa.n, self._rsa.e])


class PrivateKey(pydantic.BaseModel, PublicKey):

    """
    Asymmetric private encryption key.

    Instantiate with `new` to get a brand-new key pair.
    Instantiate with other classmethods to load an existing key.
    """

    n: int
    e: int
    d: int
    p: int
    q: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rsa = RSA.construct(
            (self.n, self.e, self.d, self.p, self.q), consistency_check=False
        )

    @classmethod
    @pydantic.root_validator()
    def _rsa_consistency_check(cls, values):
        RSA.construct(
            (values["n"], values["e"], values["d"], values["p"], values["q"]),
            consistency_check=True,
        )

    @classmethod
    def from_rsa(cls, private_key: RSA.RsaKey):
        return cls(
            n=private_key.n,
            e=private_key.e,
            d=private_key.d,
            p=private_key.p,
            q=private_key.q,
        )

    @classmethod
    def new(cls) -> PrivateKey:
        key = RSA.generate(settings.rsa_keys_length)
        return cls.from_rsa(key)

    @staticmethod
    def get_key_from_components(
        n: int, e: int, d: int, p: int, q: int
    ) -> RSA.RsaKey | None:
        try:
            private_key = RSA.construct((n, e, d, p, q), consistency_check=True)
        except ValueError:
            logger.error("Could not construct RSA private key.")
            return
        else:
            return private_key

    @classmethod
    def from_dbo(cls, dbo) -> None:
        raise NotImplementedError(
            "Loading private key from database object forbidden: "
            "its information should not be saved in a database, "
            "but in an encrypted file. Use `from_file` instead."
        )

    @classmethod
    def from_file(cls, file: Path, passphrase: str | None = None) -> PrivateKey | None:
        with file.open(mode="rb") as k:
            try:
                private_key = RSA.import_key(k.read(), passphrase=passphrase)
            except (ValueError, IndexError, TypeError):
                logger.warning(f"Couldn't read private key from {file!s}")
                return

        if private_key.has_private():
            return cls.from_rsa(private_key)

    def _to_file(self, file: Path, passphrase: str | None = None) -> None:
        """
        See PublicKey._to_file
        """
        with file.open(mode="wb") as f:
            f.write(self._rsa.export_key(format="DER", passphrase=passphrase))

    def get_public_key(self) -> PublicKey:
        return PublicKey(
            n=self._rsa.n,
            e=self._rsa.e,
        )

    def decrypt_asymmetric_raw(self, en_data: bytes) -> bytes:
        return PKCS1_OAEP.new(self._rsa).decrypt(en_data)

    def decrypt_asymmetric(self, se_en_data: str) -> str | None:
        """
        Deserializes and decrypts data.
        Returns None if we cannot decrypt.
        """
        en_data = deserialize_string(se_en_data)
        return decode_bytes(self.decrypt_asymmetric_raw(en_data))

    def get_signature(self, hash_obj: SHA256.SHA256Hash) -> str:
        """
        Sign a hash using an RSA private key.
        """
        return serialize_bytes(pkcs1_15.new(self._rsa).sign(hash_obj))
