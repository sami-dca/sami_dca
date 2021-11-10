from sqlalchemy import exists
from typing import List, Optional

from ...config import Identifier
from ..base.models import ConversationDBO, NodeDBO
from .._template.private import PrivateDatabaseTemplate
from ._conversations_memberships import ConversationsMembershipsDatabase


class ConversationsDatabase(PrivateDatabaseTemplate):

    def is_known(self, uid: Identifier) -> bool:
        with self._init_session() as session:
            return session.query(exists().where(ConversationDBO.uid == uid))\
                .scalar()

    def store(self, conversation: ConversationDBO) -> None:
        if not self.is_known(conversation.uid):
            with self._init_session() as session:
                session.add(conversation)

    def get_members(self, conversation_id: Identifier) -> List[NodeDBO]:
        return ConversationsMembershipsDatabase()\
            .get_members_of_conversation(conversation_id)

    def get_conversation(self, uid: Identifier) -> Optional[ConversationDBO]:
        with self._init_session() as session:
            conversation = session.query(ConversationDBO)\
                .where(ConversationDBO.uid == uid)\
                .one_or_none()
            session.expunge_all()
        return conversation

    def get_all_conversations(self) -> List[ConversationDBO]:
        with self._init_session() as session:
            conversations = session.query(ConversationDBO).all()
            session.expunge_all()
        return conversations
