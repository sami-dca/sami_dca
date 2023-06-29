from __future__ import annotations

import pydantic

from ...objects import Contact
from ._base import RequestData


class CEP_INI(RequestData, pydantic.BaseModel):
    author: Contact
    contacts: set[Contact]

    _full_name = "Contact Exchange Protocol Initialize"
    _to_store = True
    _waiting_for_answer = True


class CEP_REP(RequestData, pydantic.BaseModel):
    author: Contact
    contacts: set[Contact]

    _full_name = "Contact Exchange Protocol Reply"
    _to_store = True
    _waiting_for_answer = False
