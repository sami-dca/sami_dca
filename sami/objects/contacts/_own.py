from __future__ import annotations

import ipaddress as ip
from collections import namedtuple

from ...config import settings
from ...network.utils import get_interface_info, is_supported_af
from ...utils import get_time
from ._base import Contact


class OwnContact(Contact):
    @classmethod
    def from_interface(cls, interface: str) -> OwnContact | None:
        """
        Creates a Contact from an interface name.
        Assumes the interface is valid.
        """
        addresses = get_interface_info(interface)
        return cls.from_address_list(addresses)

    @classmethod
    def from_address_list(cls, addresses: list[namedtuple]) -> OwnContact | None:
        for address in addresses:
            if is_supported_af(address.family):
                return cls.from_address(address)

    @classmethod
    def from_address(cls, address: namedtuple) -> OwnContact | None:
        # If the family is not supported
        if not is_supported_af(address.family):
            return

        return cls(
            address=ip.IPv4Interface(address.address),
            port=settings.sami_port,
            last_seen=get_time(),
        )
