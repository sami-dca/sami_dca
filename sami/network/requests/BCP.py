from __future__ import annotations

import pydantic

from ...objects import Contact, OwnContact
from ._base import RequestData


class BCP(RequestData, pydantic.BaseModel):
    author: Contact

    _full_name = "Broadcast Contact Protocol"
    _to_store = False
    _waiting_for_answer = False

    @classmethod
    def new(cls, own_contact: OwnContact) -> BCP:
        return cls(author=own_contact)
