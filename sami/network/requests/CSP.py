from __future__ import annotations

import pydantic

from ...objects import Contact
from ._base import RequestData


class CSP(RequestData, pydantic.BaseModel):
    contacts: set[Contact]

    _full_name = "Contact Sharing Protocol"
    _to_store = True
    _waiting_for_answer = False
