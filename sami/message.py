# -*- coding: UTF8 -*-

from dataclasses import dataclass

from .node import Node
from .utils import Utils
from .encryption import Encryption
from .structures import Structures


@dataclass
class Meta:
    time_sent: int = None
    time_received: int = None
    digest: str = None
    identifier: str = None


class Message:

    def __init__(self):
        """
        Instantiate a new empty object.
        Use the methods to set its values.
        """
        self.content: str = None
        self.meta = Meta()
        self.author: Node = None

    # Validation section

    @staticmethod
    def is_received_message_valid(message_data: dict) -> bool:
        """
        Performs tests on the data passed to check if the message we just received is correct.

        :param dict message_data: A message, as a dict.
        :return bool: True if it is, False otherwise.
        """

        if type(message_data) is not dict:
            return False

        if not Utils._validate_fields(message_data, Structures.received_message_structure):
            return False

        if not Node.is_valid(message_data["author"]):
            return False

        return True

    @staticmethod
    def is_message_valid_for_raw_storage(message_data: dict) -> bool:
        """
        Performs tests on the object to see if it is valid for storage in the "raw_messages" database.

        :param dict message_data: A message, as a dict.
        :return bool: True if it is, False otherwise.
        """

        if type(message_data) is not dict:
            return False

        if not Utils._validate_fields(message_data, Structures.stored_message_structure):
            return False

        return True

    # Encryption section

    @staticmethod
    def encrypt_message(aes_key: bytes, nonce: bytes, message: dict) -> dict:
        """
        Encrypts a message using the AES information passed.

        :param bytes aes_key: An AES key.
        :param nonce: The nonce linked to the AES key.
        :param message: A valid message, as a dictionary.
        :return dict: The message, with the sensitive information encrypted.
        """
        aes = Encryption.construct_aes_object(aes_key, nonce)
        encrypted_message, tag = Encryption.encrypt_symmetric(aes, message["content"])
        message["content"] = encrypted_message
        message["meta"]["digest"] = tag
        return message

    @staticmethod
    def decrypt_message(aes_key: bytes, nonce: bytes, message: dict) -> dict:
        """
        Takes a valid message as a dictionary and returns its content decrypted using passed AES and nonce.

        :param bytes aes_key: An AES key.
        :param bytes nonce: The nonce linked to the AES key.
        :param dict message: A valid message, as a dictionary.
        :return dict: The message, with the sensitive information decrypted.
        """
        aes = Encryption.construct_aes_object(aes_key, nonce)
        decrypted_message = Encryption.decrypt_symmetric(aes, message["content"], message["meta"]["digest"])
        message["content"] = Encryption.decode_bytes(decrypted_message)
        return message

    # Class methods section

    @classmethod
    def from_dict_encrypted(cls, aes_key: bytes, nonce: bytes, message_data: dict) -> object or None:
        """
        Creates and returns a new object instance created from the dictionary "message_data".
        The data must be checked to be valid beforehand.

        :param bytes aes_key: An AES key.
        :param bytes nonce: The AES nonce.
        :param dict message_data: A message information, as a dictionary.
        :return object|None: A message object or None.
        """
        aes = Encryption.construct_aes_object(aes_key, nonce)
        try:
            content = Encryption.decrypt_symmetric(aes, message_data["content"], message_data["meta"]["digest"])
            # Content is now a bytes object, unless the decryption failed.
        except (ValueError, KeyError):
            return
        # Convert content to a string.
        content = Encryption.decode_bytes(content)

        message_data["content"] = content

        return cls.from_dict(message_data)

    @classmethod
    def from_dict(cls, message_data: dict) -> object or None:
        """
        Creates a new object instance from the dictionary (clear message).
        The data must be checked to be valid beforehand.

        :param dict message_data: A message, as a dict.
        :return object|None: A new message object or None.
        """
        msg = cls()

        msg.set_message(message_data["content"])
        msg.set_time_sent(message_data["time_sent"])
        msg.set_author(message_data["author"])

        return msg

    # Attributes setters section

    def set_message(self, message: str) -> None:
        """
        Sets the message's content (its text).

        :param str message: A new message, as a string.
        """
        self.content = message

    def set_time_sent(self, timestamp: int = None) -> None:
        """
        Sets the "date_sent" timestamp as the actual time.
        """
        if timestamp is not None:
            self.meta.time_sent = timestamp
        else:
            self.meta.time_sent = Utils.get_timestamp()

    def set_time_received(self) -> None:
        """
        Sets the message's "time_received" timestamp as the actual time.
        """
        self.meta.time_received = Utils.get_timestamp()

    def set_author(self, author: Node):
        """
        Sets the "author" attribute.

        :param Node author: A Node object.
        """
        self.author = author

    def set_digest(self, digest: str) -> None:
        """
        Sets the "message["meta"]["digest"]" attribute.

        :param str digest: The digest of the encrypted message.
        """
        self.meta.digest = digest

    def set_id(self) -> None:
        """
        Sets the message's id.
        """
        self.meta.id = self.get_id()

    # Attributes getters section

    def get_message(self) -> str or None:
        """
        Returns the message's content (its text).

        :return str: The message's text (if set), None otherwise.
        """
        return self.content

    def get_time_sent(self) -> str or None:
        return self.meta.time_sent

    def get_time_received(self) -> str or None:
        """
        Returns the message's "time_received" value.

        :return str\None: The received timestamp as a string if it is set, None otherwise.
        """
        return self.meta.time_received

    def get_digest(self) -> str or None:
        """
        Returns own AES digest.

        :return str|None: A serialized digest if set, otherwise None.
        """
        return self.meta.digest

    def get_id(self) -> str or None:
        """
        Returns the message's id.

        :return str|None: The message's ID if set, otherwise None.
        """
        return Message.get_id_from_message(self.to_dict())

    @staticmethod
    def get_id_from_message(message: dict) -> str:
        """
        Gets an ID from a message's information, namely the time_sent and the digest.

        :param dict message: A message information, as a dictionary.
        :return str: An identifier for this message.
        """
        assert message["meta"]["time_sent"]
        assert message["meta"]["digest"]
        identifier = Encryption.hash_iterable([message["meta"]["time_sent"], message["meta"]["digest"]]).hexdigest()
        return identifier

    # Export section

    def to_dict(self) -> dict:
        """
        Returns the message instance's attributes as a dictionary.

        :return dict: The message, as a dictionary.
        """
        return {
            "content": self.get_message(),
            "meta": {
                "time_sent": self.get_time_sent(),
                "time_received": self.get_time_received(),
                "digest": self.get_digest()
            },
            "author": self.author.to_dict()
        }

    def to_json(self) -> str:
        """
        Converts the current object to a JSON-encoded string.

        :return str: A JSON-encoded string.
        """
        return Utils.encode_json(self.to_dict())


class OwnMessage(Message):

    def __init__(self):
        Message.__init__(self)
        self.is_prepared: bool = False  # Should be read-only

    @staticmethod
    def is_prepared_message_valid(message_data: dict) -> bool:
        """
        Performs tests on the data passed to check if it is a correct (prepared) message.

        :param dict message_data: A message, as a dict.
        :return bool: True if it is, False otherwise.
        """

        if type(message_data) is not dict:
            return False

        if not Utils._validate_fields(message_data, Structures.prepared_message_structure):
            return False

        return True

    def set_aes(self, master_node) -> None:
        """
        Set AES linked to the message (the conversation's AES key).

        Note: What the fuck is this method ?
        It's useless to store the AES key in the message as :
        - The locally stored message is encrypted using our own AES key.
        - When receiving a new message, we indeed use the AES negotiated with the distant node,
        but we don't need this message anymore ! And even if we did, there's no way we're making a query on this object
        instead of the database !

        This function would be way more useful in the node object.

        :param master_node:
        """
        assert type(self.author) == type(Node)
        master_node.conversations.get_decrypted_aes(master_node.rsa_private_key, self.author.get_id())

    def prepare(self, aes) -> None:
        """
        Prepare message: encrypts and sets values.
        Use the "to_json" method to get a JSON-encoded string for network communication and storage.

        :param aes: AES key used for symmetric encryption.
        """
        assert type(self.content) == str
        # Next, encode and encrypt the content.
        encoded_content: bytes = Encryption.encode_string(self.content)
        se_en_content, digest = Encryption.encrypt_symmetric(aes, encoded_content)
        self.set_message(se_en_content)
        self.set_digest(digest)
        self.set_id()

        self.is_prepared = True

    def is_preparation_done(self) -> bool:
        """
        Returns a status code as a boolean.

        :return bool: True if the node is properly prepared, False otherwise.
        """
        return OwnMessage.is_prepared_message_valid(self.to_dict())
