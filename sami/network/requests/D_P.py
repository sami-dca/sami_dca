from __future__ import annotations

from abc import ABC
from typing import Optional

from ...contacts import Contact, OwnContact
from ...structures import DCPStructure, DNPStructure
from .base import Request


class Discover(Request, ABC):

    to_store = False


class DCP(Discover):

    full_name = "Discover Contact Protocol"
    inner_struct = DCPStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        author = Contact.from_data(data.author)
        if author is None:
            return
        return data

    @classmethod
    def new(cls, own_contact: OwnContact) -> DCP:
        return cls(DCPStructure(author=own_contact.to_data()))


class DNP(Discover):

    full_name = "Discover Node Protocol"
    inner_struct = DNPStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        author = Contact.from_data(data.author)
        if author is None:
            return
        return data

    @classmethod
    def new(cls, own_contact: OwnContact) -> DNP:
        return cls(DCPStructure(author=own_contact.to_data()))
