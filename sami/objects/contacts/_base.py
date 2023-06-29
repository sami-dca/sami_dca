from __future__ import annotations

import ipaddress as ip
import logging as _logging
from copy import deepcopy
from functools import cached_property

import dns
import pydantic

from ...config import Identifier
from ...cryptography.hashing import hash_object
from ...network.utils import host_dns_name
from ...objects import StoredSamiObject
from ...utils import get_id

logger = _logging.getLogger("objects")


class Contact(StoredSamiObject):
    # TODO: add last_seen

    __table_name__ = "contacts"
    __node_specific__ = False

    address: (
        ip.IPv4Address
        | ip.IPv6Address
        | ip.IPv4Interface
        | ip.IPv6Interface
        | dns.name.Name
    )
    port: pydantic.conint(ge=1, le=65535, strict=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._original_address = deepcopy(self.address)
        self.update_address()

    def update_address(self) -> None:
        """
        Updates the address by resolving the DNS name again.
        If the Contact is not stored as a DNS name, does nothing
        (uses the same address).
        """
        if isinstance(self._original_address, dns.name.Name):
            self.address = host_dns_name(self._original_address)
        else:
            self.address = self._original_address

    @cached_property
    def id(self) -> Identifier:
        return get_id(hash_object([self._original_address, self.port]))
