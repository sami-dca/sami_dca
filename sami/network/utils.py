from __future__ import annotations

import ipaddress as ip
import socket
from collections import namedtuple
from dataclasses import dataclass
from typing import Collection

import psutil
from dns.name import Name as DNSName
from loguru import logger
from lxml import etree

from ..config import settings
from ..network.af import supported_af
from ..utils import shuffled

# Ignore lines too long
# flake8: noqa: E501

IPV6_REGEX = (
    "("
    "([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"  # 1:2:3:4:5:6:7:8
    "([0-9a-fA-F]{1,4}:){1,7}:|"  # 1::                              1:2:3:4:5:6:7::
    "([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"  # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    "([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"  # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    "([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"  # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    "([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"  # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    "([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"  # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    "[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"  # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
    ":((:[0-9a-fA-F]{1,4}){1,7}|:)|"  # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
    "fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"  # fe80::7:8%eth0   fe80::7:8%1     (link-local IPv6 addresses with zone index)
    "::(ffff(:0{1,4}){0,1}:){0,1}"
    "((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    "(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"  # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255  (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    "([0-9a-fA-F]{1,4}:){1,4}:"
    "((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    "(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"  # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
    ")"
)


@dataclass
class PortListing:
    """
    UPnP action "PortListing".

    Wrapper for LXML's bullshittery
    """

    def __init__(self, tree: etree.ElementTree):
        self.tree = tree

    @classmethod
    def parse(cls, xml: str) -> PortListing:
        return cls(etree.fromstring(xml))

    def ports_in_use(self) -> set[int]:
        return {
            int(param.text)
            for entry in self.tree
            for param in entry
            if "NewExternalPort" in param.tag
        }

    def get_info(self) -> tuple[str, int, int]:
        """
        Returns information about the current port mappings as a 3-tuple of
        (1) local address, (2) external port, (3) local port.
        """


def get_address_object(
    address: str,
) -> ip.IPv4Address | ip.IPv6Address | DNSName | None:
    """
    Takes an address as a string, and try to convert it to an IP address
    (first v4 then v6), then a DNS.
    Returns None if invalid.
    """
    try:
        add_obj = ip.ip_address(address)
    except ValueError:
        pass
    else:
        return add_obj

    dns_labels = address.split(".")
    unique_labels_count = len([label for label in dns_labels if label])
    if unique_labels_count < 2:
        return
    try:
        add_obj = DNSName(dns_labels)
    except ip.AddressValueError:
        pass
    else:
        return add_obj


def is_supported_af(family):
    return any([str(family).endswith(af) for af in supported_af])


def get_network_interfaces(
    exclude_down: bool = True, exclude_loopback: bool = True
) -> list[str]:
    """
    Get all available network interfaces on this computer.
    """
    ifaces_addrs: dict[str, namedtuple] = psutil.net_if_addrs()
    ifaces_stats: dict[str, namedtuple] = psutil.net_if_stats()

    interfaces = list(ifaces_addrs.keys())

    def is_interface_loopback(pair) -> bool:
        def is_loopback(info: namedtuple) -> bool | None:
            """
            Returns True if loopback, False if not, None if invalid.
            """
            if is_supported_af(info.family):
                return get_address_object(info.address).is_loopback

        name, all_info = pair  # Unpack
        return any(map(is_loopback, all_info))

    if exclude_loopback:
        interfaces = filter(is_interface_loopback, ifaces_addrs.items())

    if exclude_down:
        for index, (interface, info) in enumerate(interfaces):
            if not ifaces_stats[interface].isup:
                interfaces.pop(index)

    return interfaces


def get_interface_info(interface: str, filter_af: bool = True) -> list[namedtuple]:
    """
    Queries the addresses attributed on a given interface.
    Returns a list of namedtuples (the addresses) containing the information
    of each address (such as the address family and the address).
    See https://psutil.readthedocs.io/en/latest/index.html#psutil.net_if_addrs

    Raises KeyError on invalid interface name.
    """
    all_info = psutil.net_if_addrs()
    interface_info: list[namedtuple] = all_info[interface]

    if filter_af:
        interface_info = [
            addr
            for addr in interface_info
            if any([str(addr.family).endswith(af) for af in supported_af])
        ]

    return interface_info


def is_local_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            return s.connect_ex(("localhost", port)) == 0
        except socket.gaierror:
            return False


def get_local_available_port() -> int | None:
    """
    Returns the first available local port available.
    By local, we mean on the primary network interface.
    """
    # First, try using the port defined in the configuration
    if not is_local_port_in_use(settings.sami_port):
        return settings.sami_port
    # If it doesn't work, try finding another randomly
    for p in shuffled(settings.local_available_port_range):
        if not is_local_port_in_use(p):
            return p


def get_all_local_ip_addresses() -> set[ip.IPv4Address | ip.IPv6Address]:
    """
    Gets all addresses assigned on our network interfaces.
    """
    _, _, local_ip_addresses = socket.gethostbyname_ex(socket.gethostname())
    return set(map(get_address_object, local_ip_addresses))


def get_primary_ip_address() -> str | None:
    """
    Gets the IP address of the interface used to connect to the internet.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(("10.255.255.255", 1))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception:
        pass
    else:
        return ip_address


def in_same_subnet(address1: ip.IPv4Interface, address2: ip.IPv4Address) -> bool:
    """
    Checks whether `address2` is part of `address1`'s subnet.
    We expect a network mask with `address1`.
    `address2` is an IP address without mask.
    Example: `address1='192.168.1.14/24', address2='192.168.1.56'`
    """
    network = ip.IPv4Network(address1, strict=False)
    address = ip.IPv4Address(address2)
    return network.network_address < address < network.broadcast_address


def host_dns_name(dns_name: DNSName) -> ip.IPv4Address | ip.IPv6Address | None:
    """
    Given a DNS name, resolves to an IP address.
    """
    try:
        address = socket.gethostbyname(dns_name.to_text())
    except socket.gaierror:
        logger.error(f"Could not resolve host {dns_name!r}")
        return
    return get_address_object(address)


def next_external_port(
    exclude: Collection[int], use_default: bool = True, shuffle: bool = True
) -> int:
    """
    Returns the next external port which is not theoretically in use.
    Note: `settings.external_port_blacklist` gets appended to `exclude`.
    """
    excluded_ports = []
    excluded_ports.extend(exclude)
    excluded_ports.extend(settings.external_port_backlist.get())
    default = settings.external_port
    if use_default and default not in exclude:
        yield default
    space = settings.external_available_port_range
    for port in space if shuffle else shuffled(space):
        if port not in exclude:
            return port
