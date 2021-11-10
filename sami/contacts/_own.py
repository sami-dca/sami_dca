from __future__ import annotations

import ipaddress as ip

from typing import Optional, List
from collections import namedtuple

from ._base import Contact
from ..utils import get_time
from ..config import sami_port
from ..utils.network import get_interface_info, is_supported_af


class OwnContact(Contact):

    @classmethod
    def from_interface(cls, interface: str) -> Optional[OwnContact]:
        """
        Creates a Contact from an interface name.
        Assumes the interface is valid.
        """
        addresses = get_interface_info(interface)
        return cls.from_address_list(addresses)

    @classmethod
    def from_address_list(cls,
                          addresses: List[namedtuple]) -> Optional[OwnContact]:
        for address in addresses:
            if is_supported_af(address.family):
                return cls.from_address(address)

    @classmethod
    def from_address(cls, address: namedtuple) -> Optional[OwnContact]:
        # If the family is not supported
        if not is_supported_af(address.family):
            return

        return cls(
            address=ip.IPv4Interface(address.address),
            port=sami_port,
            last_seen=get_time(),
        )
