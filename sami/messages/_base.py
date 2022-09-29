import logging as _logging

from ..nodes import Node
from ._conversation import Conversation

logger = _logging.getLogger("objects")


class _Message:
    def __init__(self, *, author: Node, content: str, conversation: Conversation):  # noqa
        self.author = author
        self.content = content
        self.conversation = conversation
        self.id = None


class EditableMessage(_Message):
    pass


class ReadOnlyMessage(_Message):
    def __setattr__(self, key, value):
        logger.warning("Tried to modify a ReadOnlyMessage.")
        return
