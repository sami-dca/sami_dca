from typing import List
from sqlalchemy import exists

from ...config import Identifier
from ..base.models import MessageDBO
from .._template.private import PrivateDatabaseTemplate


class MessagesDatabase(PrivateDatabaseTemplate):

    def is_known(self, uid: Identifier) -> bool:
        with self._init_session() as session:
            return session.query(exists().where(MessageDBO.uid == uid))\
                .scalar()

    def store(self, message: MessageDBO) -> None:
        if not self.is_known(message.uid):
            with self._init_session() as session:
                session.add(message)

    def get_messages(self, conversation_uid: Identifier) -> List[MessageDBO]:
        with self._init_session() as session:
            messages = session.query(MessageDBO)\
                .where(MessageDBO.conversation_id == conversation_uid)\
                .all()
            session.expunge_all()
        return messages
