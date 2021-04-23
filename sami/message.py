# -*- coding: UTF8 -*-

import logging

from typing import Optional
from dataclasses import dataclass

from .node import Node
from .config import Config
from .encryption import Encryption
from .utils import get_timestamp
from .validation import is_valid_base_message, validate_export_structure


@dataclass
class Meta:
    time_sent: int = None
    time_received: int = None
    digest: str = None
    identifier: str = None


class Message:

    def __init__(self, author: Optional[Node] = None, content: Optional[str] = None):
        self.content = content
        self.author = author
        self.meta = Meta()
        self._id = None

    # Class methods section

    @classmethod
    def from_dict_encrypted(cls, aes_key: bytes, nonce: bytes, message_data: dict):
        """
        Creates and returns a new object instance created from the dictionary "message_data".
        The message, originally encrypted, is returned with its content in clear-text.

        :param bytes aes_key: The AES key used for decryption.
        :param bytes nonce: The AES nonce linked to the key.
        :param dict message_data: A message information, as a dictionary.
        :return: A message object or None.
        """
        # As we'll directly modify the dictionary,
        # we'll create a copy to avoid interfering with outside instances.
        message_data = message_data.copy()
        message_id = cls.get_id_from_values(message_data['meta']['time_sent'],
                                            message_data['meta']['digest'])

        if not is_valid_base_message(message_data):
            return

        aes = Encryption.construct_aes_object(aes_key, nonce)
        try:
            content = Encryption.decrypt_symmetric(aes, message_data["content"], message_data["meta"]["digest"])
        except (ValueError, KeyError):
            logging.debug(f'We could not decrypt message {message_id!r}')
            return

        content = Encryption.decode_bytes(content)
        message_data["content"] = content
        return cls.from_dict(message_data)

    @classmethod
    def from_dict(cls, message_data: dict):
        """
        Creates a new object instance from the dictionary.
        The message's content is returned as-is ; as long as the structure is respected,
        the content can be encrypted or clear-text, it doesn't matter.

        :param dict message_data: A message, as a dict.
        :return: A new message object or None.
        """
        if not is_valid_base_message(message_data):
            return

        if 'author' in message_data.keys():
            author = Node.from_dict(message_data["author"])
            if not isinstance(author, Node):
                logging.warning('Author is invalid, which makes no sense because '
                                'we are supposed to have validated its values beforehand !')
                return
            msg = cls(author=author, content=message_data["content"])
        else:
            msg = cls(content=message_data["content"])

        if 'time_received' in message_data['meta']:
            time_received = int(message_data['meta']['time_received'])
            msg.set_time_received(time_received)

        time_sent = int(message_data['meta']['time_sent'])
        msg.set_time_sent(time_sent)
        msg.set_digest(message_data["meta"]["digest"])
        msg.set_id()

        return msg

    # Static methods

    @staticmethod
    def get_id_from_values(time_sent: int, digest: str):
        """
        Create an identifier from the time sent and the digest.
        We use these two because the time sent is a constant set by the author,
        and the digest is a hash of the content.
        """
        return Encryption.hash_iterable([time_sent, digest]).hexdigest()[:Config.id_len]

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

    def set_time_received(self, value: Optional[int] = None) -> None:
        """
        Sets the message's "time_received" timestamp as the actual time,
        or as "value" if passed.
        """
        if isinstance(value, int):
            self.meta.time_received = value
        else:
            self.meta.time_received = get_timestamp()

    def set_digest(self, digest: str) -> None:
        """
        Sets the digest attribute.

        :param str digest: The digest of the encrypted message.
        """
        self.meta.digest = digest

    def set_id(self) -> None:
        """
        Sets the message's id.
        """
        # Assert the values are set.
        assert self.meta.time_sent
        assert self.meta.digest
        self._id = self.get_id_from_values(self.meta.time_sent, self.meta.digest)

    # Attributes getters section

    def get_message(self) -> Optional[str]:
        """
        Returns the message's content (its text).

        :return Union[str, None]: The message's text (if set), None otherwise.
        """
        return self.content

    def get_time_sent(self) -> Optional[int]:
        return self.meta.time_sent

    def get_time_received(self) -> Optional[int]:
        return self.meta.time_received

    def get_digest(self) -> Optional[str]:
        """
        Returns own AES digest.

        :return Optional[str]: A serialized digest if set, otherwise None.
        """
        return self.meta.digest

    def get_id(self) -> str:
        """
        Returns the message's id.

        :return str: The message's unique ID.
        """
        return self._id

    # Export section

    @validate_export_structure('stored_message_structure')
    def to_dict(self) -> dict:
        """
        Returns the message instance's attributes as a dictionary, ready for storage.

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
            },
            "author": author
        }


class OwnMessage(Message):

    def __init__(self, author):
        # TODO: get rid of author once the MasterNode is a singleton.
        Message.__init__(self, author)
        self._is_prepared: bool = False

    @classmethod
    def from_dict(cls, *args, **kwargs):
        raise PermissionError('Illegal operation.')

    def prepare(self, aes) -> None:
        """
        Prepare message: encrypts and sets values.

        :param aes: AES key object used for symmetric encryption.
        """
        bytes_content = Encryption.encode_string(self.content)
        se_en_content, digest = Encryption.encrypt_symmetric(aes, bytes_content)
        self.set_message(se_en_content)
        self.set_digest(digest)
        self.set_time_sent()
        self.set_id()

        self._is_prepared = True

    def is_prepared(self) -> bool:
        """
        :return bool: True if the node is properly prepared, False otherwise.
        """
        return self._is_prepared

    @validate_export_structure('received_message_structure')
    def to_dict(self) -> dict:
        """
        Returns the message instance's attributes as a dictionary.

        :return dict: The message, as a dictionary.
        """
        content = self.get_message()
        time_sent = self.get_time_sent()
        digest = self.get_digest()
        author = self.author.to_dict()

        assert content
        assert time_sent
        assert digest
        assert author

        return {
            "content": content,
            "meta": {
                "time_sent": time_sent,
                "digest": digest
            },
            "author": author
        }
