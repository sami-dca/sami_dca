from __future__ import annotations

import ipaddress as ip
import logging as _logging
from typing import Optional, Union

import dns

from ..config import Identifier
from ..cryptography.hashing import hash_object
from ..database.base.models import ContactDBO
from ..database.common import ContactsDatabase
from ..structures import ContactStructure
from ..utils import get_id, get_time
from ..utils.network import get_address_object, host_dns_name

logger = _logging.getLogger("objects")


class Contact:
    def __init__(
        self,
        address: Union[
            ip.IPv4Address,
            ip.IPv6Address,
            ip.IPv4Interface,
            ip.IPv6Interface,
            dns.name.Name,
        ],
        port: int,
        last_seen: int,
    ):

        self._original_address = address
        self.update_address()
        self.port = port
        self.last_seen = last_seen
        self.id = self._compute_id()

    @classmethod
    def from_id(cls, identifier: Identifier) -> Optional[Contact]:
        db: ContactsDatabase = ContactsDatabase()
        dbo = db.get_contact(identifier)
        if dbo is None:
            return
        return cls.from_dbo(dbo)

    @classmethod
    def from_data(cls, contact_data: ContactStructure) -> Optional[Contact]:
        port = contact_data.port
        address = get_address_object(contact_data.address)
        if address is None:
            # Invalid address
            return

        return cls(
            address=address,
            port=port,
            last_seen=get_time(),
        )

    @classmethod
    def from_dbo(cls, dbo: ContactDBO) -> Contact:
        return cls(
            address=get_address_object(dbo.address),
            port=dbo.port,
            last_seen=dbo.last_seen,
        )

    def to_data(self) -> ContactStructure:
        return ContactStructure(
            address=str(self.address),
            port=self.port,
        )

    def to_dbo(self) -> ContactDBO:
        return ContactDBO(
            uid=self.id,
            address=str(self._original_address),
            port=self.port,
            last_seen=self.last_seen,
        )

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

    def store(self) -> None:
        db: ContactsDatabase = ContactsDatabase()
        db.store(self.to_dbo())

    def _compute_id(self) -> Identifier:
        return get_id(hash_object([self.address, self.port]))
