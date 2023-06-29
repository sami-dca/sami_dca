"""
Resources for UDP Peer-To-Peer:
https://resources.infosecinstitute.com/topic/udp-hole-punching/
https://github.com/dwoz/python-nat-hole-punching
https://youtu.be/IbzGL_tjmv4

Also, UPnP
"""

from __future__ import annotations

import ipaddress
import re
import threading as th
from functools import cached_property
from typing import Generator
from urllib.request import urlopen

import upnpclient

from ..config import settings
from ..design import Singleton
from ..jobs import Job
from ..objects import Contact
from ..threads.jobs import JobsThread
from ..utils import get_time
from ._network import Network
from .requests import Request
from .threads import RequestHandlingThread, RequestSenderThread
from .utils import (
    IPV6_REGEX,
    PortListing,
    get_address_object,
    get_local_available_port,
    in_same_subnet,
    next_external_port,
)


class Networks(Singleton):

    """
    Mediator for interacting with network interfaces.

    TODO: make the networks "refreshable"
     Notes on that matter:
     - Consider a network can change its address
    """

    _networks: set[Network] = []

    _last_upnp_lease_refresh: int
    # This event is set when no public port could be opened with UPnP
    no_upnp = th.Event()
    no_upnp.set()  # It is set by default

    handle_thread: RequestHandlingThread
    sender_thread: RequestSenderThread

    jobs_thread: JobsThread

    def init(self):
        self.refresh_upnp(force=True)

        self.handle_thread = RequestHandlingThread()
        self.handle_thread.start()
        self.sender_thread = RequestSenderThread()
        self.sender_thread.start()

        self.jobs_thread = JobsThread()
        self.jobs_thread.jobs.register(
            Job(
                action=self.discover_nodes,
                schedule=settings.nodes_discovery_schedule,
            )
        )
        self.jobs_thread.jobs.register(
            Job(
                action=self.discover_contacts,
                schedule=settings.contact_discovery_schedule,
            )
        )
        self.jobs_thread.start()

    @cached_property
    def get_public_address(
        self,
    ) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
        """
        Tries to get the public IP address for this client.

        FIXME: should be able to return a DNS name.
        """
        # First, try with UPnP.
        for device in upnpclient.discover():
            if action := device.find_action("GetExternalIPAddress"):
                return get_address_object(action())

        # Second, try with an external service
        url = "http://checkip.dyndns.org"
        try:
            request = urlopen(url).read().decode("utf-8")
        except:  # FIXME # noqa
            return

        found_ipv4s = re.findall(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", request)
        found_ipv6s = re.findall(IPV6_REGEX, request)

        if found_ipv4s:
            return get_address_object(found_ipv4s[0])
        elif found_ipv6s:
            return get_address_object(found_ipv6s[0])

    def discover_nodes(self):
        # TODO
        pass

    def discover_contacts(self):
        # TODO
        pass

    def refresh_upnp(self, /, force: bool = False) -> None:
        """
        Update the UPnP port mapping on the router if appropriate.
        """
        if not force and not hasattr(self, "_last_upnp_lease_refresh"):
            force = True

        if force:
            self._last_upnp_lease_refresh = get_time() - (settings.upnp_lease + 1)

        # Find and use only the Internet Gateway Device
        # FIXME: Can a network have multiple IGDs?
        #  And if yes, how should we handle that?
        igds = [
            device
            for device in upnpclient.discover()
            if "InternetGatewayDevice" in device.device_type
        ]
        if len(igds) != 1:
            return
        igd = igds[0]

        lease_time_left = (
            self._last_upnp_lease_refresh + settings.upnp_lease
        ) - get_time()
        if not lease_time_left <= (0.1 * settings.upnp_lease):
            # If more than 10% of the lease time is left, we don't update.
            # Even though we don't need to update based on the lease time,
            # it is possible another system has overwritten our mapping.
            # In this case, we'll simply add the port to the exclude list,
            # since we can expect it will overwrite the lease again.
            if action := igd.find_action("GetListOfPortMappings"):
                port_listing = PortListing.parse(
                    action(
                        NewStartPort=settings.external_available_port_range.get().start,
                        NewEndPort=settings.external_available_port_range.get().stop
                        - 1,
                        NewProtocol="TCP",
                        NewManage="1",  # FIXME: what is this?
                        NewNumberOfPorts=0,  # FIXME: what is this?
                    )["NewPortListing"]
                )
                if (
                    str(self.primary.address),
                    settings.external_port.get(),
                    settings.sami_port.get(),
                ) in port_listing.get_info():
                    return
                else:
                    settings.external_port_blacklist.append(
                        settings.external_port
                    )  # FIXME
            else:
                # FIXME
                return

        # If we can, we'll try to be polite by trying to discover
        # which external ports are already in use to avoid overriding
        # those when creating the port mapping
        # (adding a UPnP port mapping overrides the one already in place).
        if action := igd.find_action("GetListOfPortMappings"):
            port_listing = PortListing.parse(
                action(
                    NewStartPort=settings.external_available_port_range.get().start,
                    NewEndPort=settings.external_available_port_range.get().stop - 1,
                    NewProtocol="TCP",
                    NewManage="1",  # FIXME: what is this?
                    NewNumberOfPorts=0,  # FIXME: what is this?
                )["NewPortListing"]
            )
            exclude = port_listing.ports_in_use()
        else:
            exclude = []
        external_port = next_external_port(
            exclude=exclude,
        )

        if action := (
            igd.find_action("AddAnyPortMapping") or igd.find_action("AddPortMapping")
        ):
            response = action(
                NewRemoteHost="",
                NewExternalPort=external_port,
                NewProtocol="TCP",
                NewInternalPort=get_local_available_port(),
                NewInternalClient=str(self.primary.address),  # FIXME: will str work?
                NewEnabled="1",
                NewPortMappingDescription="Sami DCA",
                NewLeaseDuration=settings.upnp_lease.get(),
            )
            if returned_external_port := response.get("NewReservedPort"):
                settings.external_port.set(returned_external_port)
            else:
                settings.external_port.set(external_port)
            self._last_upnp_lease_refresh = get_time()
            self.no_upnp.clear()
        else:
            self.no_upnp.set()

    def what_is_up(self):
        """
        Selects a random beacon or contact, tries to connect to it and sends a
        WUP_INI request.
        This method blocks until we receive a WUP_REP, timing out and asking
        another node if necessary.
        Once this method is finished, we should be up-to-date on sent requests.
        """
        # TODO

    def broadcast(self, request: Request) -> None:
        for network in self:
            network.broadcast(request)

    @property
    def primary(self) -> Network | None:
        """
        Returns the primary network instance.
        It is the one which we can use to communicate over the Internet.
        """
        for net in self:
            if net.is_primary:
                return net

    def register_network(self, network: Network) -> None:
        network.start()
        self._networks.update({network})

    def get_corresponding_network(self, contact: Contact) -> Network | None:
        """
        Given a contact, return the network which can be used to connect to it.
        Returns None if none of our networks correspond
        (the contact is unreachable).
        """
        return next(
            filter(
                lambda net: in_same_subnet(net.address, contact.address),
                self,
            ),
            None,
        )

    def __iter__(self) -> Generator[Network, None, None]:
        """
        Iterate over the registered networks.
        """
        for net in self._networks:
            yield net
