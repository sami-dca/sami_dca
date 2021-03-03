# -*- coding: UTF8 -*-

import os
import random

from Crypto.PublicKey import RSA

from .config import Config
from .utils import encode_json
from .encryption import Encryption
from .lib.dictionary import dictionary
from .validation import is_valid_node, validate_export_structure


class Node:

    def __init__(self):
        # Initialize attributes.
        self.contacts = None  # Contacts database.
        self.rsa_public_key = None
        self._hash = None
        self._sig = None

        self.name = None
        self.id = None

    @classmethod
    def from_dict(cls, node_data: dict) -> object or None:
        """
        Takes node information as a dictionary and returns a Node object if they are valid.

        :param node_data: Node information as a dictionary. Must be valid.
        :return Node|None: A Node object or None.
        """
        if not is_valid_node(node_data):
            return
        new_node = cls()
        new_node.initialize(node_data)
        return new_node

    def initialize(self, node_data: dict) -> None:
        """
        Sets:
        - RSA public key
        - Instance's ID
        - Instance's name
        - Hash
        - Signature

        :param dict node_data: Node information as a dictionary. Must be valid.
        """
        if not is_valid_node(node_data):
            raise ValueError('Invalid node information')

        self.set_rsa_public_key(Encryption.construct_rsa_object(int(node_data["rsa_n"]), int(node_data["rsa_e"])))
        self.set_hash(node_data["hash"])
        self.set_signature(node_data["sig"])

        self.set_id()
        self.set_name()

    # ID section

    def set_id(self) -> None:
        """
        Sets Node's ID.
        This ID is derived from the RSA key.
        """
        assert self.rsa_public_key is not None
        self.id = Node.get_id_from_rsa_key(self.rsa_public_key)

    def get_id(self) -> str or None:
        """
        Returns the Node's ID.

        :return str|None: The Node's ID if set, None otherwise.
        """
        return self.id

    @staticmethod
    def get_id_from_rsa_key(rsa_key: RSA.RsaKey) -> str:
        """
        Returns an ID based on a RSA key.

        :param RSA.RsaKey rsa_key: A RSA key, private or public.
        :return str: An identifier.
        """
        hash_object = Encryption.hash_iterable([rsa_key.n, rsa_key.e])
        hex_digest = hash_object.hexdigest()
        return hex_digest[:Config.id_len]

    # Name section

    @staticmethod
    def derive_name(identifier: str) -> str:
        """
        Derive a name from an hexadecimal value.

        :param str identifier: Hexadecimal identifier.
        :return str: A name.
        """
        # Sets the random number generator's seed.
        random.seed(int(identifier, 16))

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

    def set_name(self) -> None:
        """
        Sets Node's name.
        It is can be accessed through the name attribute.
        """
        self.name = Node.derive_name(self.get_id())

    # RSA section

    def set_rsa_public_key(self, rsa_public_key) -> None:
        """
        Sets the instance attribute "self.rsa_public_key".

        :param rsa_public_key: A RSA public key.
        """
        self.rsa_public_key = rsa_public_key

    def get_rsa_public_key(self) -> RSA.RsaKey:
        """
        Returns the Node's RSA public key.
        The instance must have a valid "rsa_public_key" attribute.

        :return RSA.RsaKey: A RSA public key object.
        """
        return self.rsa_public_key

    def set_signature(self, signature: str) -> None:
        """
        Sets Node's signature.

        :param str signature: A signature, created from the node's hash.
        """
        self._sig = signature

    def get_signature(self) -> str:
        """
        Returns Node's signature.

        :return str: Node's signature.
        """
        return self._sig

    @staticmethod
    def export_rsa_public_key_to_file(rsa_public_key: RSA.RsaKey, location: str, passphrase: str = None) -> None:
        """
        Exports a RSA public key to a file.

        :param RSA.RsaKey rsa_public_key: A RSA private key.
        :param str location: Directory to which the public key should be exported to.
        :param str passphrase: A passphrase that will be used to encrypt the key.
        """
        identifier = Node.get_id_from_rsa_key(rsa_public_key)
        file_name = f"rsa_public_key-{identifier}.pem"
        path = os.path.join(location, file_name)
        with open(path, "wb") as fl:  # Might raise OSError, PermissionError, UnicodeError, FileNotFoundError
            fl.write(rsa_public_key.export_key(passphrase=passphrase))

    # Hash section

    def set_hash(self, hexdigest: str) -> None:
        """
        Sets the Node's hash.

        :param str hexdigest: A hexdigest as a string.
        """
        self._hash = hexdigest

    def get_hash(self) -> str:
        return self._hash

    # Export section

    @validate_export_structure('node_structure')
    def to_dict(self) -> dict:
        """
        Returns the Node's information as a dict.

        :return dict: The node information, as a dictionary.
        """
        return {
            "rsa_n": self.rsa_public_key.n,
            "rsa_e": self.rsa_public_key.e,
            "hash": self.get_hash(),
            "sig": self.get_signature()
        }

    def to_json(self) -> str:
        """
        Returns the Node's information as a JSON-encoded string.

        :return str: JSON string containing the information of the node.
        """
        return encode_json(self.to_dict())


class MasterNode(Node):

    def __init__(self):
        Node.__init__(self)
        self._rsa_private_key = None
        self.databases = None
        self._hash = None
        self._sig = None

    def set_databases(self, databases) -> None:
        """
        Sets the "databases" attribute, which is an object containing all available databases across the project.

        :param databases:
        :return:
        """
        self.databases = databases

    def initialize(self, rsa_private_key: RSA.RsaKey) -> None:
        """
        Sets:
        - RSA private key
        - RSA public key
        - Instance's ID
        - Instance's name
        - Databases instances
        - Hash
        - Signature
        - Name
        - ID

        :param RSA.RsaKey rsa_private_key: A RSA private key.
        """
        self.set_rsa_private_key(rsa_private_key)
        self.set_rsa_public_key(Encryption.get_public_key_from_private_key(rsa_private_key))
        self.set_id()
        self.set_name()
        self.databases.open_node_databases(self)
        self._hash = self.compute_own_hash().hexdigest()
        self._sig = Encryption.serialize_bytes(self.compute_own_sig())
        self.set_name()
        self.set_id()
        self.databases.nodes.add_node(self)

    # RSA section

    def set_rsa_private_key(self, rsa_private_key: RSA.RsaKey) -> None:
        """
        Sets attribute "self._rsa_private_key".

        :param RSA.RsaKey rsa_private_key: A RSA private key object.
        """
        self._rsa_private_key = rsa_private_key

    def get_rsa_private_key(self):
        # We shouldn't use this.
        # Ths RSA private key should stick to the master node, and stay private to this object.
        return self._rsa_private_key

    def compute_own_hash(self):
        """
        Computes the hash from this node's information.

        :return: A hash object.
        """
        return Encryption.get_public_key_hash(self.rsa_public_key)

    def compute_own_sig(self) -> bytes:
        return Encryption.get_rsa_signature(self._rsa_private_key, self.compute_own_hash())

    @staticmethod
    def export_rsa_private_key_to_file(rsa_private_key: RSA.RsaKey, location: str, passphrase: str = None):
        """
        Exports a RSA private key to a file.
        It can be encrypted, using the passed "passphrase".

        :param RSA.RsaKey rsa_private_key: A RSA private key.
        :param str location: Directory to which the private key should be exported to.
        :param str passphrase: Optional. A passphrase to encrypt the private key. Will be needed when importing it.
        """
        identifier = Node.get_id_from_rsa_key(rsa_private_key)
        file_name = f"rsa_private_key-{identifier}.pem"
        path = os.path.join(location, file_name)
        with open(path, "wb") as fl:  # Might raise OSError, PermissionError, UnicodeError ; TODO: handle
            fl.write(rsa_private_key.export_key(passphrase=passphrase))
