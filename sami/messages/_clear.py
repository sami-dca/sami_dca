from __future__ import annotations

from typing import TYPE_CHECKING

from ._base import ReadOnlyMessage

if TYPE_CHECKING:
    from ..nodes import Node
    from ._conversation import Conversation


class ClearMessage(ReadOnlyMessage):

    """
    This is a special state during which the message is clear-text.
    It is only suited for display, and not for storage nor transmission.

    Note: doesn't have an id.
    """

    def __init__(
        self,
        author: Node,
        content: str,
        conversation: Conversation,
        time_sent: int,
        time_received: int,
    ):
        super().__init__(
            author=author,
            content=content,
            conversation=conversation,
        )
        self.time_sent = time_sent
        self.time_received = time_received
