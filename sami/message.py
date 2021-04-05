# -*- coding: UTF8 -*-

from dataclasses import dataclass

from .node import Node
from .encryption import Encryption
from .utils import get_timestamp, encode_json, is_int
from .validation import is_valid_received_message, validate_export_structure


@dataclass
class Meta:
    time_sent: int = None
    time_received: int = None
    digest: str = None
    identifier: str = None


class Message:

    def __init__(self, author, content: str = None):
        self.content = content
        self.author = author
        self.meta = Meta()

    # Class methods section

    @classmethod
    def from_dict_encrypted(cls, aes_key: bytes, nonce: bytes, message_data: dict) -> object or None:
        """
        Creates and returns a new object instance created from the dictionary "message_data".
        The message, originally encrypted, is returned with its content in clear-text.

        :param bytes aes_key: The AES key used for decryption.
        :param bytes nonce: The AES nonce linked to the key.
        :param dict message_data: A message information, as a dictionary.
        :return object|None: A message object or None.
        """
        if not is_valid_received_message(message_data):
            return

        aes = Encryption.construct_aes_object(aes_key, nonce)
        try:
            content = Encryption.decrypt_symmetric(aes, message_data["content"], message_data["meta"]["digest"])
        except (ValueError, KeyError):
            return

        content = Encryption.decode_bytes(content)
        message_data["content"] = content
        return cls.from_dict(message_data)

    @classmethod
    def from_dict(cls, message_data: dict) -> object or None:
        """
        Creates a new object instance from the dictionary.
        The message's content is returned as-is ; as long as the structure is respected,
        the content can be encrypted or clear-text, it doesn't matter.

        :param dict message_data: A message, as a dict.
        :return Message|None: A new message object or None.
        """
        if not is_valid_received_message(message_data):
            return

        author = Node.from_dict(message_data["author"])
        if not isinstance(author, Node):
            # This block should never be entered as the author is already validated in the message validation process.
            # Just in case :)
            return

        msg = cls(author, message_data["content"])
        time_sent = message_data['time_sent']
        # We check the time sent is passed as expected.
        if not isinstance(time_sent, str) and time_sent and is_int(time_sent):
            return
        msg.set_time_sent(message_data["time_sent"])
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
            self.meta.time_sent = get_timestamp()

    def set_time_received(self) -> None:
        """
        Sets the message's "time_received" timestamp as the actual time.
        """
        self.meta.time_received = get_timestamp()

    def set_digest(self, digest: str) -> None:
        """
        Sets the "message["meta"]["digest"]" attribute.

        :param str digest: The digest of the encrypted message.
        """
        self.meta.digest = digest

    def set_signature(self, sig) -> None:
        pass

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

        :return str|None: The received timestamp as a string if it is set, None otherwise.
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
        Gets an ID from a message's information.
        It is unique, and can be computed by anyone at anytime.

        :param dict message: A message information, as a dictionary.
        :return str: An identifier for this message.
        """
        # Assert the values are set and are strings.
        assert isinstance(message["meta"]["time_sent"], str)
        assert isinstance(message["meta"]["digest"], str)
        # Create an identifier from the time sent and the digest.
        # We use these two because the time sent is a constant set by the author,
        # and the digest is a hash of the content.
        return Encryption.hash_iterable([message["meta"]["time_sent"], message["meta"]["digest"]]).hexdigest()

    # Export section

    @validate_export_structure('stored_message_structure')
    def to_dict(self) -> dict:
        """
        Returns the message instance's attributes as a dictionary.

        :return dict: The message, as a dictionary.
        """
        content = self.get_message()
        time_sent = self.get_time_sent()
        time_received = self.get_time_received()
        digest = self.get_digest()
        author = self.author.to_dict()

        assert content
        assert time_sent
        assert time_received
        assert digest
        assert author

        return {
            "content": content,
            "meta": {
                "time_sent": time_sent,
                "time_received": time_received,
                "digest": digest
                # !!! No signature ?!
            },
            "author": author
        }

    def to_json(self) -> str:
        """
        Converts the current object to a JSON-encoded string.

        :return str: A JSON-encoded string.
        """
        return encode_json(self.to_dict())


class OwnMessage(Message):

    def __init__(self, author):
        Message.__init__(self, author)
        self._is_prepared: bool = False

    def prepare(self, aes) -> None:
        """
        Prepare message: encrypts and sets values.
        Use the "to_json" method to get a JSON-encoded string for network communication and storage.

        :param aes: AES key object used for symmetric encryption.
        """
        encoded_content = Encryption.encode_string(self.content)
        se_en_content, digest = Encryption.encrypt_symmetric(aes, encoded_content)
        self.set_message(se_en_content)
        self.set_digest(digest)
        self.set_id()

        self._is_prepared = True

    def is_prepared(self) -> bool:
        """
        :return bool: True if the node is properly prepared, False otherwise.
        """
        return self._is_prepared
