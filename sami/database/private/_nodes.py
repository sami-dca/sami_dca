from sqlalchemy import exists
from typing import List, Optional

from ...config import Identifier
from ..base.models import NodeDBO
from .._template.common import CommonDatabaseTemplate


class NodesDatabase(CommonDatabaseTemplate):

    def is_known(self, uid: Identifier) -> bool:
        with self._init_session() as session:
            return session.query(exists().where(NodeDBO.uid == uid)).scalar()

    def store(self, node: NodeDBO) -> None:
        if not self.is_known(node.uid):
            with self._init_session() as session:
                session.add(node)

    def get_all_nodes(self) -> List[NodeDBO]:
        with self._init_session() as session:
            nodes = session.query(NodeDBO).all()
            session.expunge_all()
        return nodes

    def get_node(self, uid: Identifier) -> Optional[NodeDBO]:
        with self._init_session() as session:
            node = session.query(NodeDBO).where(NodeDBO.uid == uid).one_or_none()
            session.expunge_all()
        return node
