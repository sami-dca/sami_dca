from __future__ import annotations

from functools import cached_property

import pydantic
from pydantic import BaseModel

from ...config import Identifier, settings
from ...cryptography.hashing import hash_object
from ...cryptography.symmetric import DecryptionKey
from ...utils import get_id
from .._base import SamiObject
from ..nodes import Node
from ._base import ReadOnlyMessage
from ._clear import ClearMessage


class EncryptedMessage(BaseModel, ReadOnlyMessage, pydantic.BaseModel, SamiObject):
    """
    This is the final state of a message.
    It is encrypted, and ready for storage / transmission.

    Note: has an id.
    """

    author: Node
    content: str
    digest: str
    time_sent: pydantic.conint(gt=settings.sami_start)
    time_received: pydantic.conint(gt=settings.sami_start)

    def decrypt(self, key: DecryptionKey) -> ClearMessage:
        return ClearMessage(
            author=self.author,
            content=key.decrypt_raw(self.content, self.digest),
            time_sent=self.time_sent,
            time_received=self.time_received,
        )

    @cached_property
    def id(self) -> Identifier:
        """
        Creates an identifier from the time sent and the digest.
        We use the time sent because it is a constant set by the author,
        and the digest because it is essentially a signature of the value.
        """
        return get_id(hash_object([self.time_sent, self.digest]))
