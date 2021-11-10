from __future__ import annotations

from typing import Optional

from .base import Request
from ...structures import MPPStructure
from ...messages import EncryptedMessage


class MPP(Request):

    full_name = "Message Propagation Protocol"
    to_store = True
    inner_struct = MPPStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        pass

    @classmethod
    def new(cls, encrypted_message: EncryptedMessage) -> MPP:
        return cls(MPPStructure(
            message=encrypted_message.to_data(),
            conversation=encrypted_message.conversation.id,
        ))
