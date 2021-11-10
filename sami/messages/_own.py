from __future__ import annotations

from ..utils import get_time
from ._base import EditableMessage
from ..nodes.own import MasterNode
from ._encrypted import EncryptedMessage
from ..database.private import KeysDatabase
from ..cryptography.symmetric import EncryptionKey

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ._conversation import Conversation

import logging as _logging
logger = _logging.getLogger('objects')


class OwnMessage(EditableMessage):

    """
    Class for representing the messages we create.

    The usual workflow is as such:
    ```
    >>> conversation = Conversation(...)
    >>> new_message = OwnMessage(conversation=conversation)
    >>> new_message.content = 'Hello world!'
    >>> encrypted_new_message = new_message.to_encrypted()
    >>> ...  # Send the encrypted message over the network!
    ```
    """

    def __init__(self, *, conversation: Conversation):
        super().__init__(
            author=MasterNode().id,
            content='',
            conversation=conversation.id,
        )

    def to_encrypted(self) -> EncryptedMessage:
        key_dbo = KeysDatabase().get_symmetric_key(self.conversation.id)
        if key_dbo is None:
            msg = ("Tried to encrypt a message part "
                   "of a conversation we're not part of ?")
            logger.critical(msg)
            raise ValueError(msg)
        key = EncryptionKey.from_dbo(key_dbo)
        en_se_content, en_se_digest = key.encrypt_symmetric(self.content)
        return EncryptedMessage(
            author=self.author,
            content=en_se_content,
            digest=en_se_digest,
            conversation=self.conversation,
            time_sent=get_time(),
            time_received=get_time(),
        )
