from __future__ import annotations

from functools import cached_property
from typing import Generator

import pydantic
from Crypto.Random import get_random_bytes
from loguru import logger

from ...config import Identifier, settings
from ...cryptography.hashing import hash_object
from ...cryptography.symmetric import (
    DecryptionKey,
    SymmetricKey,
    SymmetricKeyPart,
    get_expected_key_length,
)
from ...objects import (
    ClearMessage,
    EncryptedMessage,
    MasterNode,
    Node,
    StoredSamiObject,
)
from ...utils import get_id


class _ClearMessagesProxy:

    """
    Interact with a clear-text version of the messages
    """

    def __iter__(self):
        return next(self)

    def __next__(self) -> Generator[ClearMessage, None, None]:
        for enc_message in self._enc_messages:
            yield enc_message.decrypt(self._key)
        raise StopIteration

    def __init__(self, key: DecryptionKey, enc_messages: list[EncryptedMessage]):
        self._key = key
        self._enc_messages = enc_messages

    def get_last(self) -> ClearMessage:
        return self._enc_messages[-1].decrypt(self._key)


class Conversation(StoredSamiObject):
    """
    Class for representing conversations, that is, collections of messages.

    Examples
    --------
    >>> conv = Conversation(
    >>>     messages=[],
    >>>     members={Node(...), MasterNode(...)},
    >>>     value={SymmetricKeyPart(...)},
    >>> )
    >>> conv.add_key_part(SymmetricKeyPart(...))
    >>> conv.messages.append(OwnMessage(value="This is my message!", ...).encrypt(...))
    >>> conv.clear_messages.get_last().value
    "This is my message!"
    """

    __table_name__ = "conversations"
    __node_specific__ = True

    messages: list[EncryptedMessage] = []
    members: pydantic.conset(Node, min_items=2, max_items=settings.aes_key_length)
    key: SymmetricKey | set[SymmetricKeyPart] = {}

    @classmethod
    @pydantic.validator("value", each_item=True)
    def _check_keys_length(cls, value: SymmetricKeyPart, values):
        """
        Asserts the value lengths are correct.
        """
        assert len(value) == get_expected_key_length(
            values["members"],
            value.author.id,
        )
        return value

    @classmethod
    @pydantic.validator("value")
    def _construct_full_key(cls, value: SymmetricKey | set[SymmetricKeyPart]):
        """
        Tries, given value parts, to construct a complete symmetric value.
        """
        if isinstance(value, SymmetricKey):
            return value
        else:
            key = SymmetricKey.from_parts(value)
            return key if isinstance(value, SymmetricKey) else value

    @classmethod
    @pydantic.validator("value")
    def _create_our_part_if_missing(
        cls, value: SymmetricKey | set[SymmetricKeyPart], values
    ):
        if isinstance(value, SymmetricKey):
            return value
        with MasterNode() as master_node:
            if len([part for part in value if part.author.id == master_node.id]) == 0:
                value.update(
                    SymmetricKeyPart(
                        value=get_random_bytes(
                            get_expected_key_length(
                                values["members"],
                                master_node.id,
                            )
                        ),
                        author=master_node,
                    )
                )
        return value

    @classmethod
    def load_or_new(cls, members: set[Node]) -> Conversation:
        temp_conv = Conversation(members=members)
        if temp_conv.is_known():
            conv = cls.from_id(temp_conv.id)
            if not isinstance(conv, cls):
                # Failed to create a valid Conversation from the values in
                # the database.
                # FIXME: repair database
                conv = temp_conv
        else:
            conv = temp_conv

        return conv

    def has_complete_key(self) -> bool:
        return isinstance(self.key, SymmetricKey)

    def add_key_part(self, key_part: SymmetricKeyPart) -> None:
        if self.has_complete_key():
            logger.warning(
                "Tried to add a value part to a conversation that "
                "already has a complete value. Ignored. "
            )
        else:
            self.key.update({key_part})
            sym_key = SymmetricKey.from_parts(self.key)
            if isinstance(sym_key, SymmetricKey):
                self.key = sym_key

    @property
    def clear_messages(self) -> _ClearMessagesProxy | None:
        if self.has_complete_key():
            return _ClearMessagesProxy(DecryptionKey.from_key(self.key), self.messages)

    @cached_property
    def id(self) -> Identifier:
        """
        Note: the identifier of a conversation is computed from its members.
        """
        sorted_members = sorted(node.id for node in self.members)
        return get_id(hash_object(sorted_members))
