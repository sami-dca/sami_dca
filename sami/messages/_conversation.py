from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from ..config import Identifier
from ..cryptography.hashing import hash_object
from ..database.base.models import ConversationDBO, KeyDBO
from ..database.private import (
    ConversationsDatabase,
    ConversationsMembershipsDatabase,
    KeysDatabase,
    MessagesDatabase,
)
from ..utils import get_id

if TYPE_CHECKING:
    from ..nodes import Node
    from ._clear import ClearMessage


class Conversation:

    """
    Object used to manipulate Conversations.
    Conversations hold two important information: messages and members.
    """

    def __init__(self, members: List[Node]):
        self.members = members
        self.messages: List[ClearMessage] = self._get_messages()
        self.key_dbo = self._get_key_dbo()
        self.id = self._compute_id()

    @classmethod
    def from_id(cls, uid: Identifier) -> Optional[Conversation]:
        dbo = ConversationsDatabase().get_conversation(uid)
        if dbo is None:
            return
        return cls.from_dbo(dbo)

    @classmethod
    def from_dbo(cls, dbo: ConversationDBO) -> Conversation:
        return cls(ConversationsDatabase().get_members(dbo.uid))

    def add_message(self, message: ClearMessage) -> None:
        """
        Adds a message to the conversation.
        Mainly used to avoid saving the message in the database,
        then reading all the messages again.
        """
        self.messages.append(message)

    def _get_messages(self) -> List[ClearMessage]:
        """
        Returns the messages part of this conversation,
        as extracted from the database.
        """
        messages = MessagesDatabase().get_messages(self.id)
        messages.sort(key=lambda msg: msg.time_received, reverse=True)
        return messages

    def is_known(self) -> bool:
        return ConversationsDatabase().is_known(self.id)

    def store(self) -> None:
        """
        Stores the conversation.
        Also registers the memberships.
        """
        if ConversationsDatabase().is_known(self.id):
            return
        ConversationsDatabase().store(self.to_dbo())
        ConversationsMembershipsDatabase().register_memberships(
            list(map(lambda member: member.to_dbo(), self.members)), self.id
        )

    def get_members(self) -> List[Node]:
        return list(
            map(
                lambda dbo: Node.from_dbo(dbo),
                ConversationsDatabase().get_members(self.id),
            )
        )

    def to_dbo(self) -> ConversationDBO:
        return ConversationDBO(
            uid=self.id,
        )

    def _get_key_dbo(self) -> Optional[KeyDBO]:
        """
        Tries to get the conversation's key database object.
        """
        return KeysDatabase().get_symmetric_key(self.id)

    def _compute_id(self) -> Identifier:
        sorted_members = sorted([node.id for node in self.members])
        return get_id(hash_object(sorted_members))
