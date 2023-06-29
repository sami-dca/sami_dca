from __future__ import annotations

import pydantic

from ...config import settings
from ...objects import Contact, OwnContact
from ...utils import get_time
from ._base import RequestData


class WUP_INI(RequestData, pydantic.BaseModel):
    beginning: pydantic.conint(gt=settings.sami_start)
    end: int
    author: Contact

    _full_name = "What's Up Initialize"
    _to_store = False
    _waiting_for_answer = True

    @classmethod
    def new(cls, last_timestamp: int, own_contact: OwnContact) -> WUP_INI:
        return cls(
            beginning=last_timestamp,
            end=get_time() + 10,
            author=own_contact,
        )


# WUP_REP is located in ``_request.py``.
