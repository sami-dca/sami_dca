from __future__ import annotations

from typing import Optional

from ...contacts import Contact, OwnContact
from ...structures import BCPStructure
from .base import Request


class BCP(Request):

    full_name = "Broadcast Contact Protocol"
    to_store = False
    inner_struct = BCPStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        author = Contact.from_data(data.author)
        if author is None:
            return
        return data

    @classmethod
    def new(cls, own_contact: OwnContact) -> BCP:
        return cls(BCPStructure(author=own_contact.to_data()))
