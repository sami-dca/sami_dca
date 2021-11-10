from sqlalchemy import exists
from typing import List, Optional

from ...utils import get_time
from ..base.models import RequestDBO
from .._template.common import CommonDatabaseTemplate
from ...config import Identifier, max_request_lifespan


class RawRequestsDatabase(CommonDatabaseTemplate):

    def is_known(self, uid: Identifier) -> bool:
        with self._init_session() as session:
            return session.query(exists().where(RequestDBO.uid == uid))\
                .scalar()

    def store(self, request: RequestDBO) -> None:
        if not self.is_known(request.uid):
            with self._init_session as session:
                session.add(request)

    def get_all_since(self, timestamp: int) -> List[RequestDBO]:
        with self._init_session() as session:
            requests = session.query(RequestDBO)\
                .where(RequestDBO.timestamp > timestamp)\
                .all()
            session.expunge_all()
        return requests

    def get_last_received(self) -> Optional[RequestDBO]:
        with self._init_session() as session:
            q = session.query(RequestDBO)\
                .where(max(RequestDBO.timestamp))\
                .one_or_none()
            session.expunge_all()
        return q

    def purge_old(self, lifespan: int = max_request_lifespan) -> None:
        now = get_time()
        threshold = now - lifespan
        with self._init_session() as session:
            requests = session.query(RequestDBO)\
                .where(RequestDBO.timestamp < threshold)
            for dbo in requests:
                session.delete(dbo)
