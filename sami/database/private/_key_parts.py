from sqlalchemy import exists
from typing import Optional, List

from ...config import Identifier
from ..base.models import KeyPartDBO
from .._template.private import PrivateDatabaseTemplate


class KeyPartsDatabase(PrivateDatabaseTemplate):

    def store(self, key_part: KeyPartDBO) -> None:
        if self.is_known(key_part.uid):
            with self._init_session() as session:
                session.add(key_part)

    def is_known(self, key_id: Identifier) -> bool:
        with self._init_session() as session:
            return session.query(exists().where(KeyPartDBO.id == key_id))\
                .scalar()

    def get_incomplete_key(self, key_id: Identifier) -> Optional[KeyPartDBO]:
        with self._init_session() as session:
            key = session.query(KeyPartDBO)\
                .where(KeyPartDBO.id == key_id)\
                .one_or_none()
            session.expunge_all()
        return key

    def get_parts(self, conv_id: Identifier) -> List[KeyPartDBO]:
        with self._init_session() as session:
            parts = session.query(KeyPartDBO)\
                .where(KeyPartDBO.conversation_id == conv_id).all()
            session.expunge_all()
        return parts

    def remove(self, key_id: Identifier) -> None:
        if not self.is_known(key_id):
            return
        with self._init_session() as session:
            q = session.query(KeyPartDBO)\
                .where(KeyPartDBO.id == key_id)\
                .one_or_none()
            if q is not None:
                session.delete(q)
