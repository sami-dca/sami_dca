from __future__ import annotations

from typing import List, Optional

from ...nodes import Node
from ...structures import NPPStructure
from .base import Request


class NPP(Request):

    full_name = "Node Publication Protocol"
    to_store = True
    inner_struct = NPPStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        for potential_node in data.nodes:
            node = Node.from_data(potential_node)
            if node is None:
                return
        return data

    @classmethod
    def new(cls, nodes: List[Node]) -> NPP:
        return cls(
            cls.inner_struct(nodes=list(map(lambda node: node.to_data(), nodes)))
        )
