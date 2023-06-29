from __future__ import annotations

import pydantic

from ...objects import Node
from ._base import RequestData


class NPP(RequestData, pydantic.BaseModel):
    nodes: set[Node]

    _full_name = "Node Publication Protocol"
    _to_store = True
    _waiting_for_answer = False
