from __future__ import annotations

import pydantic

from ...objects import Contact, OwnContact
from ._base import RequestData


class DCP(RequestData, pydantic.BaseModel):
    author: Contact

    _full_name = "Discover Contact Protocol"
    _to_store = False
    _waiting_for_answer = True

    @classmethod
    def new(cls, own_contact: OwnContact) -> DCP:
        return cls(author=own_contact)


class DNP(RequestData, pydantic.BaseModel):
    author: Contact

    _full_name = "Discover Node Protocol"
    _to_store = False
    _waiting_for_answer = True

    @classmethod
    def new(cls, own_contact: OwnContact) -> DNP:
        return cls(author=own_contact)
