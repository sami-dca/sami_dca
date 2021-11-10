from __future__ import annotations

from typing import Optional, List

from .base import Request
from ...contacts import Contact
from ...structures import CSPStructure, ContactStructure


class CSP(Request):

    full_name = "Contact Sharing Protocol"
    to_store = True
    inner_struct = CSPStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        for potential_contact in data.contacts:
            contact = Contact.from_data(potential_contact)
            if contact is None:
                return
        return data

    @classmethod
    def new(cls, contacts: List[Contact]) -> CSP:
        return cls(CSPStructure(
            contacts=[
                contact.to_data()
                for contact in contacts
            ]
        ))
