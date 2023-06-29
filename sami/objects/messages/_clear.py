from __future__ import annotations

import pydantic

from ...config import settings
from ..nodes import Node
from ._base import ReadOnlyMessage


class ClearMessage(ReadOnlyMessage, pydantic.BaseModel):

    """
    This is a special state during which the message is clear-text.
    It is only suited for display, and not for storage nor transmission.
    It can't be converted back to an encrypted message either.

    Note: doesn't have an id.
    """

    author: Node
    content: str
    time_sent: pydantic.conint(gt=settings.sami_start)
    time_received: pydantic.conint(gt=settings.sami_start)
