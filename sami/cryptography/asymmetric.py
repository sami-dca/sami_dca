from __future__ import annotations

from pathlib import Path
from typing import Optional

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15

from .hashing import hash_object
from ..config import rsa_keys_length
from ..database.base.models import KeyDBO
from .serialization import deserialize_string, serialize_bytes, \
    encode_string, decode_bytes

import logging as _logging
logger = _logging.getLogger('cryptography')


class PublicKey:

    """
    Asymmetric public encryption key.

    Instantiate with available classmethods to load an existing key.
    To create a new pair, use `PrivateKey.new()`.
    """

    def __init__(self, public_key: RSA.RsaKey):
        self._rsa = public_key

    @staticmethod
    def get_key_from_components(n: int, e: int) -> Optional[RSA.RsaKey]:
        try:
            public_key = RSA.construct((n, e), consistency_check=True)
        except ValueError:
            logger.error('Could not construct RSA public key.')
            return
        else:
            return public_key

    @classmethod
    def from_dbo(cls, dbo: KeyDBO) -> PublicKey:
        pass

    @classmethod
    def from_components(cls, n: int, e: int) -> Optional[PublicKey]:
        public_key = PublicKey.get_key_from_components(n, e)
        if public_key is None:
            return
        else:
            return cls(public_key)

    def _to_file(self, file: Path) -> None:
        """
        Takes this key and writes it to a file.
        Use Node.export_public_key.
        """
        with file.open(mode='wb') as f:
            f.write(self._rsa.export_key(format='DER'))

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

    def encrypt_asymmetric(self, data: str) -> str:
        """
        Asymmetrically encrypts and serializes data.
        Must be reversible with `decrypt_asymmetric()`.
        """

        en_data = PKCS1_OAEP.new(self._rsa).encrypt(encode_string(data))
        se_en_data = serialize_bytes(en_data)
        return se_en_data

    def is_signature_valid(self, hash_object: SHA256.SHA256Hash,
                           sig: str) -> bool:
        """
        Takes a signature and checks whether it is valid.
        """
        try:
            pkcs1_15.new(self._rsa).verify(hash_object,
                                           deserialize_string(sig))
        except (ValueError, TypeError):
            return False
        return True

    def get_key(self) -> RSA.RsaKey:
        return self._rsa

    def get_public_key_hash(self) -> SHA256.SHA256Hash:
        """
        Returns a hash of the public key.
        """
        return hash_object([
            self._rsa.n,
            self._rsa.e,
        ])


class PrivateKey(PublicKey):

    """
    Asymmetric private encryption key.

    Instantiate with `new` to get a brand new key pair.
    Instantiate with other classmethods to load an existing key.
    """

    def __init__(self, private_key: RSA.RsaKey):
        super().__init__(private_key.public_key())

        # Override public key with private one
        self._rsa = private_key

    @classmethod
    def new(cls) -> PrivateKey:
        key = RSA.generate(rsa_keys_length)
        return cls(key)

    @staticmethod
    def get_key_from_components(n: int, e: int, d: int, p: int,
                                q: int) -> Optional[RSA.RsaKey]:
        try:
            private_key = RSA.construct((n, e, d, p, q), consistency_check=True)
        except ValueError:
            logger.error('Could not construct RSA private key.')
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
    def from_components(cls, n: int, e: int, d: int, p: int,
                        q: int) -> Optional[PublicKey]:
        private_key = PrivateKey.get_key_from_components(n, e, d, p, q)
        if private_key is None:
            return
        else:
            return cls(private_key)

    @classmethod
    def from_file(cls, file: Path,
                  passphrase: Optional[str] = None) -> Optional[PrivateKey]:
        with file.open(mode="rb") as k:
            try:
                private_key = RSA.import_key(k.read(), passphrase=passphrase)
            except (ValueError, IndexError, TypeError):
                logger.warning(f"Couldn't read private key from {file!s}")
                return

        if private_key.has_private():
            return cls(private_key)

    def _to_file(self, file: Path, passphrase: Optional[str] = None) -> None:
        """
        See PublicKey._to_file
        """
        with file.open(mode='wb') as f:
            f.write(self._rsa.export_key(format='DER', passphrase=passphrase))

    def get_public_key(self) -> PublicKey:
        return PublicKey.from_components(
            n=self._rsa.n,
            e=self._rsa.e,
        )

    def decrypt_asymmetric(self, se_en_data: str) -> Optional[str]:
        """
        Deserializes and decrypts data.
        Returns None if we cannot decrypt.
        """
        en_data = deserialize_string(se_en_data)
        data = PKCS1_OAEP.new(self._rsa).decrypt(en_data)
        return decode_bytes(data)

    def get_signature(self, hash_object: SHA256.SHA256Hash) -> str:
        """
        Sign a hash using a RSA private key.
        """
        return serialize_bytes(pkcs1_15.new(self._rsa).sign(hash_object))

    def get_private_key_hash(self) -> SHA256.SHA256Hash:
        """
        Returns a hash of the private key.
        """
        return hash_object([
            self._rsa.n,
            self._rsa.e,
            self._rsa.d,
            self._rsa.p,
            self._rsa.q,
        ])
