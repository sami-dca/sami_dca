from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..nodes import Node
    from ._conversation import Conversation

import logging as _logging
logger = _logging.getLogger('objects')


class _Message:

    def __init__(self, *, author: Node, content: str,
                 conversation: Conversation):
        self.author = author
        self.content = content
        self.conversation = conversation
        self.id = None


class EditableMessage(_Message):
    pass


class ReadOnlyMessage(_Message):
    def __setattr__(self, key, value):
        logger.warning('Tried to modify a ReadOnlyMessage.')
        return
