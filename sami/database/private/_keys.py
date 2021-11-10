from typing import Optional
from sqlalchemy import exists

from ...config import Identifier
from ..base.models import KeyDBO
from .._template.private import PrivateDatabaseTemplate


class KeysDatabase(PrivateDatabaseTemplate):

    def store(self, key: KeyDBO) -> None:
        with self._init_session() as session:
            session.add(key)

    def is_known(self, key_id: Identifier) -> bool:
        with self._init_session() as session:
            return session.query(exists().where(KeyDBO.uid == key_id)).scalar()

    def get_symmetric_key(self, key_id: Identifier) -> Optional[KeyDBO]:
        with self._init_session() as session:
            key = session.query(KeyDBO)\
                .where(KeyDBO.uid == key_id)\
                .one_or_none()
            session.expunge_all()
        return key
