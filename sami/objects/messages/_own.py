from __future__ import annotations

import logging as _logging

import pydantic

from ...cryptography.symmetric import EncryptionKey
from ...utils import get_time
from ..nodes import MasterNode
from ._base import EditableMessage
from ._encrypted import EncryptedMessage

logger = _logging.getLogger("objects")


class OwnMessage(EditableMessage, pydantic.BaseModel):

    """
    Class for representing the messages we create.
    """

    author: MasterNode = MasterNode()
    content: str = ""

    def encrypt(self, key: EncryptionKey) -> EncryptedMessage:
        se_en_data, se_tag = key.encrypt_raw(self.content)
        return EncryptedMessage(
            author=self.author,
            content=se_en_data,
            digest=se_tag,
            time_sent=get_time(),  # FIXME
            time_received=get_time(),  # FIXME
        )
