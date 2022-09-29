from typing import List

from ...config import Identifier
from .._template.private import PrivateDatabaseTemplate
from ..base.models import ConversationMembershipDBO, NodeDBO
from ._nodes import NodesDatabase


class ConversationsMembershipsDatabase(PrivateDatabaseTemplate):
    def register_memberships(
        self, nodes: List[NodeDBO], conv_id: Identifier
    ) -> None:
        """
        Register that `nodes` are members of a specific `conversation`.
        """
        with self._init_session() as session:
            for node in nodes:
                session.add(ConversationMembershipDBO(node.id, conv_id))

    def get_members_of_conversation(self, conv_id: Identifier) -> List[NodeDBO]:  # noqa
        with self._init_session() as session:
            members = (
                session.query(ConversationMembershipDBO)
                .where(ConversationMembershipDBO.conversation_id == conv_id)
                .all()
            )
            session.expunge_all()
            nodes_db = NodesDatabase()
            return [nodes_db.get_node(dbo.node_id) for dbo in members]
