from __future__ import annotations

from typing import Optional

from ..config import Identifier
from ._base import ReadOnlyMessage
from ..utils import get_time, get_id
from ._conversation import Conversation
from ..structures import MessageStructure
from ..database.private import KeysDatabase
from ..database.base.models import MessageDBO
from ..cryptography.hashing import hash_object
from ..cryptography.symmetric import DecryptionKey

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..nodes import Node
    from ._clear import ClearMessage


class EncryptedMessage(ReadOnlyMessage):

    """
    This is the final state of a message.
    It is encrypted, and ready for storage / transmission.

    To get a clear-text version of the message (if we can),
    use method `to_clear`.

    Note: has an id.
    """

    def __init__(self, *, author: Node, content: str, digest: str,
                 time_sent: int, time_received: int,
                 conversation: Conversation):
        super().__init__(
            author=author,
            content=content,
            conversation=conversation,
        )
        self.time_sent = time_sent
        self.time_received = time_received
        self.digest = digest
        self.id = self._compute_id()

    @classmethod
    def from_data(cls, message_data: MessageStructure) -> EncryptedMessage:
        return cls(
            author=Node.from_data(message_data.author).id,
            content=message_data.content,
            conversation=Conversation.from_id(message_data.conversation),
            time_sent=message_data.time_sent,
            time_received=get_time(),
            digest=message_data.digest,
        )

    @classmethod
    def from_dbo(cls, dbo: MessageDBO) -> EncryptedMessage:
        return cls(
            author=dbo.author_id,
            content=dbo.content,
            digest=dbo.digest,
            time_sent=dbo.time_sent,
            time_received=dbo.time_received,
            conversation=Conversation.from_id(dbo.conversation_id),
        )

    def to_dbo(self) -> MessageDBO:
        return MessageDBO(
            uid=self.id,
            content=self.content,
            time_sent=self.time_sent,
            time_received=self.time_received,
            digest=self.digest,
            author_id=self.author,
            parent_conversation_id=self.conversation,
        )

    def to_data(self) -> MessageStructure:
        return MessageStructure(
            content=self.content,
            time_sent=get_time(),
            digest=self.digest,
            author=self.author.to_data(),
            conversation=self.conversation.id,
        )

    def to_clear(self) -> Optional[ClearMessage]:
        key_dbo = KeysDatabase().get_symmetric_key(self.conversation.id)
        if key_dbo is None:
            # We don't have the key to decrypt this message
            return
        return DecryptionKey.from_dbo(key_dbo) \
            .decrypt_symmetric(self.content, self.digest)

    def _compute_id(self) -> Identifier:
        """
        Creates an identifier from the time sent and the digest.
        We use the time sent because it is a constant set by the author,
        and the digest because it is a hash of the content.
        """
        return get_id(hash_object([self.time_sent, self.digest]))
