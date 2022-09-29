from __future__ import annotations

from typing import List, Optional

from ...contacts import Contact, OwnContact
from ...structures import WUP_INIStructure, WUP_REPStructure
from ...utils import get_time
from .base import Request
from .mapping.wup_valid import status_mapping_wup_valid


class WUP_INI(Request):

    full_name = "What's Up Init"
    to_store = False
    inner_struct = WUP_INIStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        now = get_time()
        if 0 < data.beginning <= now:
            # Beginning out of bounds
            return
        if 0 < data.end <= now:
            # End out of bounds
            return

        author = Contact.from_data(data.author)
        if author is None:
            # Invalid node info
            return

        return data

    @classmethod
    def new(cls, last_timestamp: int, own_contact: OwnContact) -> WUP_INI:
        return cls(
            WUP_INIStructure(
                beginning=last_timestamp,
                end=get_time() + 10,
                author=own_contact.to_data(),
            )
        )


class WUP_REP(Request):

    full_name = "What's Up Reply"
    to_store = False
    inner_struct = WUP_REPStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        for potential_request in data.requests:
            req_type = status_mapping_wup_valid[potential_request.status]
            if req_type is None:
                # Invalid status
                return

            inner_data = req_type.inner_struct(**potential_request.data)
            if inner_data is None:
                # Data is invalid
                return

            request = req_type.from_data(inner_data)
            if request is None:
                # Invalid request information
                return

        return data

    @classmethod
    def new(cls, requests: List[Request]) -> WUP_REP:
        return cls(
            WUP_REPStructure(requests=[request.to_data() for request in requests])
        )
