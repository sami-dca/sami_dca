from __future__ import annotations

import pydantic

from ...objects import EncryptedMessage
from ._base import RequestData


class MPP(RequestData, pydantic.BaseModel):
    message: EncryptedMessage
    conversation_id: pydantic.conint(
        strict=True,
        ge=0,
        le=int("f" * 64, 16),  # noqa
    )

    _full_name = "Message Propagation Protocol"
    _to_store = True
    _waiting_for_answer = False
