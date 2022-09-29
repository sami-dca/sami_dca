import ipaddress as ip
import logging as _logging
import random
import re
import socket
from collections import namedtuple
from typing import Dict, List, Optional, Set, Union
from urllib.request import urlopen

import psutil
from dns.name import Name as DNSName

from ..config import default_port_range
from ..network.af import supported_af

logger = _logging.getLogger("utils")


def get_address_object(
    address: str,
) -> Optional[Union[ip.IPv4Address, ip.IPv6Address, DNSName]]:
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
) -> List[str]:
    """
    Get all available network interfaces on this computer.
    """
    ifaces_addrs: Dict[str, namedtuple] = psutil.net_if_addrs()
    ifaces_stats: Dict[str, namedtuple] = psutil.net_if_stats()

    interfaces = list(ifaces_addrs.keys())

    def is_interface_loopback(pair) -> bool:
        def is_loopback(info: namedtuple) -> Optional[bool]:
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


def get_interface_info(
    interface: str, filter_af: bool = True
) -> List[namedtuple]:  # noqa
    """
    Queries the addresses attributed on a given interface.
    Returns a list of namedtuples (the addresses) containing the information
    of each address (such as the address family and the address).
    See https://psutil.readthedocs.io/en/latest/index.html#psutil.net_if_addrs

    Raises KeyError on invalid interface name.
    """
    all_info = psutil.net_if_addrs()
    interface_info: List[namedtuple] = all_info[interface]

    if filter_af:
        interface_info = [
            addr
            for addr in interface_info
            if any([str(addr.family).endswith(af) for af in supported_af])
        ]

    return interface_info


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def get_available_port() -> Optional[int]:
    """
    From a list of ports, return any available port.
    Return None if we couldn't find one.
    """
    rng = default_port_range.copy()
    random.shuffle(rng)
    for p in rng:
        if not is_port_in_use(p):
            return p


def get_public_ip_address() -> str:
    """
    Recovers our public address.
    """
    url = "http://checkip.dyndns.org"
    request = urlopen(url).read().decode("utf-8")
    # Get IPv4
    global_ip = re.findall(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", request)[0]
    logger.debug(f"Requested public IP address to {url!r}, got {global_ip!r}")
    return global_ip


def get_all_local_ip_addresses() -> Set[Union[ip.IPv4Address, ip.IPv6Address]]:
    """
    Gets all addresses assigned on our network interfaces.
    """
    _, _, local_ip_addresses = socket.gethostbyname_ex(socket.gethostname())
    return set(map(get_address_object, local_ip_addresses))


def get_primary_ip_address():
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


def in_same_subnet(
    address1: ip.IPv4Interface, address2: ip.IPv4Address
) -> bool:  # noqa
    """
    Checks whether `address2` is part of `address1`'s subnet.
    We expect a network mask with `address1`.
    `address2` is an IP address without mask.
    Example: `address1='192.168.1.14/24', address2='192.168.1.56'`
    """
    network = ip.IPv4Network(address1, strict=False)
    address = ip.IPv4Address(address2)
    return network.network_address < address < network.broadcast_address


def host_dns_name(dns_name: DNSName) -> Optional[Union[ip.IPv4Address, ip.IPv6Address]]:
    """
    Given a DNS name, resolves to an IP address.
    """
    try:
        address = socket.gethostbyname(dns_name.to_text())
    except socket.gaierror:
        logger.error(f"Could not resolve host {dns_name!r}")
        return
    return get_address_object(address)
