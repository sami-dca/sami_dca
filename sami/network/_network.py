"""
Resources for UDP Peer-To-Peer:
https://resources.infosecinstitute.com/topic/udp-hole-punching/
https://github.com/dwoz/python-nat-hole-punching
https://youtu.be/IbzGL_tjmv4

Also, UPnP
"""

from __future__ import annotations

import ipaddress
import logging as _logging
import random
import socket
import threading as th
from queue import Queue
from typing import Any, Callable, Generator, List, Optional, Tuple, Union

import upnpy
from upnpy.exceptions import IGDError

from ..config import (
    broadcast_limit,
    broadcast_port,
    contact_connect_timeout,
    min_peers,
    network_buffer_size,
    sami_port,
    upnp_lease,
)
from ..contacts import Beacon, Contact, OwnContact, beacons
from ..database.common import ContactsDatabase, RawRequestsDatabase
from ..design import Singleton, apply_init_callback_to_singleton
from ..messages import OwnMessage
from ..utils import get_time, iter_to_dict
from ..utils.network import get_primary_ip_address, in_same_subnet
from .requests import BCP, DNP, MPP, WUP_INI, Request

logger = _logging.getLogger("network")


class Network:

    """
    Network interface, linked to an actual NIC (Network Interface Card).
    As such, this Network has its own dedicated contact.
    """

    def __init__(self, parent: Networks, own_contact: OwnContact):
        self.parent = parent
        self.own_contact = own_contact
        self.address = self.own_contact.address

        self.raw_requests_database: RawRequestsDatabase = RawRequestsDatabase()
        self.contacts_database: ContactsDatabase = ContactsDatabase()

        self._stop_event = th.Event()

        # Define the threads which will listen for requests on the network.
        # These threads listen for requests and put them in a queue, therefore
        # they do not perform any important processing and can be terminated
        # anytime, which is why they are daemons.
        self.listen_requests_thread = th.Thread(
            name=f"{self.address}_requests",
            target=self.listen_for_requests,
            daemon=True,
        )
        self.listen_broadcast_thread = th.Thread(
            name=f"{self.address}_broadcast",
            target=self.listen_for_autodiscover_packets,
            daemon=True,
        )

    def __hash__(self):
        return hash(self.address)

    @property
    def is_primary(self) -> bool:
        return self.address == ipaddress.ip_address(get_primary_ip_address())

    def what_is_up(self) -> None:
        """
        Selects a node and asks for all requests since the last we received.
        This method is called when a private key is loaded into the client.

        TODO: Keep running until we receive a response,
         timeout and send to another
        """
        # Note: we don't pass the request to the send queue because this
        #  method is only called by the job scheduler.
        if ContactsDatabase().nunique() < min_peers:
            # We don't know enough unique contacts
            return

        last_request_received = self.raw_requests_database.get_last_received()
        if not last_request_received:
            # We didn't receive any request yet
            return

        req = WUP_INI.new(last_request_received.timestamp, self.own_contact)
        for contact in self.find_valid_contact():
            if self._send_request(req, contact):
                return

    def request_nodes(self) -> None:
        """
        Discovers nodes by requesting a peer.
        """
        # Note: we don't pass the request to the send queue because this
        #  method is only called by the job scheduler.
        req = DNP.new(self.own_contact)
        for contact in self.find_valid_contact():
            if self._send_request(req, contact):
                return

    def request_contacts(self) -> None:
        """
        Discovers contacts by requesting a peer.
        """
        # Note: we don't pass the request to the send queue because this
        #  method is only called by the job scheduler.
        req = DNP.new(self.own_contact)
        for contact in self.find_valid_contact():
            if self._send_request(req, contact):
                return

    def iter_known_contacts(
        self,
    ) -> Generator[Union[Beacon, Contact], None, None]:  # noqa
        """
        Generator used for choosing a contact to send Requests to.
        Yields beacons first, then contacts.
        They are shuffled in order to avoid always sending Requests to
        the same one.
        Eventually returns None when no more are available.
        """
        all_beacons = list(beacons)
        random.shuffle(all_beacons)
        for beacon in all_beacons:
            yield beacon

        all_contacts = self.contacts_database.get_all()
        random.shuffle(all_contacts)
        for contact in all_contacts:
            yield Contact.from_dbo(contact)

    def start(self) -> None:
        """
        Starts listening on this network interface.
        """
        self.listen_requests_thread.start()
        self.listen_broadcast_thread.start()

    def send_own_message(self, own_message: OwnMessage) -> None:
        enc_own_message = own_message.to_encrypted()
        req = MPP.new(enc_own_message)
        self.broadcast(req)

    def can_connect_to(self, contact: Contact) -> bool:
        """
        Takes a Contact and verifies whether this network instance
        can connect to it.
        It doesn't verify the contact availability on the network,
        only if it is theoretically possible to connect to it, based on
        network rules and protocols.
        """
        if self.address.is_loopback:
            return False
        if contact.address.is_global:
            if not self.is_primary:
                return False
        elif contact.address.is_private:
            if not in_same_subnet(self.address, contact.address):
                return False
        elif contact.address.is_loopback:
            # We're not supposed to have a loopback as a Contact
            raise ValueError(f"Got loopback address: {contact.address!r}")
        elif contact.address.is_reserved:
            return False
        elif contact.address.is_multicast:
            return False
        elif contact.address.is_link_local:
            return False
        elif contact.address.is_unspecified:
            return False
        return True

    def find_valid_contact(self) -> Generator[Contact, None, None]:
        for contact in self.iter_known_contacts():
            if self.can_connect_to(contact):
                yield contact

    def _receive_all(
        self, sock: socket.socket
    ) -> Tuple[bytes, Tuple[str, int]]:
        """
        Receives all parts of a network-sent message.
        Takes a socket object and returns a tuple with
        (1) the complete message as bytes
        (2) a tuple with (1) the address and (2) distant port of the sender.
        """
        data = bytes()
        while True:
            # Could there be interlaced packets (two different
            # addresses gathered during successive loops) ?
            part, add = sock.recvfrom(network_buffer_size)
            data += part
            if len(part) < network_buffer_size:
                # Either 0 or end of data
                break
        return data, add

    def listen_for_autodiscover_packets(self) -> None:
        """
        Captures Requests from the LAN broadcast traffic and routes them.
        FIXME: Currently allows for all kinds of request, but in practice,
         we want to accept BCP exclusively
        """
        with socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        ) as s:  # noqa
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind(("", broadcast_port))
            while not self._stop_event.is_set():
                raw_request, (address, port) = self._receive_all(s)
                self.parent.handle_queue.put((raw_request, address))

    def listen_for_requests(self) -> None:
        """
        Sets up a server and listens on a port.
        It requires a TCP connection to receive information.
        """
        with socket.socket() as server_socket:
            server_socket.bind((self.address, sami_port))
            server_socket.listen()
            while not self._stop_event.is_set():
                connection, address = server_socket.accept()
                raw_request, (address, port) = self._receive_all(connection)
                self.parent.handle_queue.put((raw_request, address))
                connection.close()

    def broadcast_autodiscover(self) -> None:
        if self.contacts_database.nunique() > broadcast_limit:
            return
        request = BCP.new(own_contact=self.own_contact)
        self.broadcast_request_lan(request)

    def broadcast(self, request: Request) -> None:
        """
        Broadcast a Request to all known contacts.
        """
        contacts = list(self.iter_known_contacts())
        for contact in contacts:
            self.parent.send_queue.put((self, request, contact))

        logger.info(f"Broadcast request {request.id!r} " f"to {len(contacts)} contacts")

    def broadcast_request_lan(self, bcp_request: BCP) -> None:
        """
        Broadcasts a Request on the local network (broadcast).
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(
                data=bcp_request.to_bytes(),
                address=("<broadcast>", broadcast_port),
            )

    def _send_request(self, request: Request, contact: Contact) -> bool:
        """
        Send a Request to a specific Contact.
        Returns True if we managed to send the Request, False otherwise.
        """
        address = contact.address
        port = contact.port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
            client_sock.settimeout(contact_connect_timeout)
            req = request.to_bytes()
            try:
                client_sock.connect((address, port))
                total_sent = 0
                while total_sent < len(req):
                    sent = client_sock.send(req[total_sent:])
                    if sent == 0:
                        raise RuntimeError("Socket connection broken")
                    total_sent += sent
            except (
                socket.timeout,
                ConnectionRefusedError,
                ConnectionResetError,
                OSError,
            ):
                logger.info(
                    f"Could not send request {request.id!r} " f"to {address}:{port}"
                )
            except Exception as e:
                logger.error(f"Unhandled {type(e)} exception caught: {e!r}")
            else:
                logger.info(
                    f"Sent {request.status!r} request {request.id!r} "
                    f"to {address}:{port}"
                )
                return True
        return False


def init_networks(instance):
    instance.refresh_upnp(force=True)


@apply_init_callback_to_singleton(init_networks)
class Networks(Singleton):

    """
    Mediator for interacting with network interfaces.

    TODO: make the networks "refreshable"
     Notes on that matter:
     - Consider a network can change its address
    """

    networks: List[Network] = []

    # Requests in this queue will be handled by an independent thread
    handle_queue = Queue()
    # Requests in this queue will be sent by an independent thread
    send_queue = Queue()

    # UPnP controller
    upnp = upnpy.UPnP()
    _last_upnp_lease_refresh: int
    # This event is set when no public port could be opened with UPnP
    no_upnp = th.Event()
    no_upnp.set()  # It is set by default

    def refresh_upnp(self, /, force: bool = False) -> None:
        """
        Update the UPnP port mapping on the router if appropriate.
        """
        if force:
            self._last_upnp_lease_refresh = get_time() - (upnp_lease + 1)

        lease_time_left = get_time() - self._last_upnp_lease_refresh
        # If more than 90% of the lease time is left, we don't update.
        if not lease_time_left < (0.1 * upnp_lease):
            return

        try:
            router = self.upnp.get_igd()
        except IGDError:
            # No Internet Gateway Device on this network.
            self.no_upnp.set()
            return

        services = router.get_services()

        could_open: bool = False
        for service in services:
            actions = iter_to_dict(
                service.get_actions(),
                key=lambda action: action.name,
            )
            if "AddPortMapping" in actions:
                for suitable_service in actions["AddPortMapping"]:
                    suitable_service.AddPortMapping(
                        NewRemoteHost="",
                        NewExternalPort=80,  # FIXME
                        NewProtocol="TCP",
                        NewInternalPort=2108,  # FIXME
                        NewInternalClient="192.168.1.3",  # FIXME
                        NewEnabled=1,
                        NewPortMappingDescription="Sami DCA.",
                        NewLeaseDuration=upnp_lease,
                    )
                    self._last_upnp_lease_refresh = get_time()
                    could_open = True

        if could_open:
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

    def get_primary(self) -> Optional[Network]:
        """
        Returns the primary network instance.
        It is the one which we can use to communicate over the Internet.
        """
        for net in self.iter():
            if net.is_primary:
                return net

    def register_network(self, network: Network) -> None:
        network.start()
        self.networks.append(network)

    def get_corresponding_network(self, contact: Contact) -> Optional[Network]:
        """
        Given a Contact, return the Network which can be used to connect to it.
        Returns None if none of our networks correspond
        (the Contact is unreachable).
        """
        return next(
            filter(
                lambda net: in_same_subnet(net.address, contact.address),
                self.iter(),
            ),
            None,
        )

    def map(self, func: Callable[[Network], Any]) -> List[Any]:
        """
        Takes a function and applies it on all network interfaces.
        `func` will receive a `Network` instance as its only argument.
        Most of the time, you'll want to use it this way:
        ```
        >>> networks = Networks()
        >>> networks.map(lambda net: net.broadcast(...))
        ```
        """
        return [func(net) for net in self.iter()]

    def iter(self) -> Generator[Network, None, None]:
        """
        Iterate over the registered networks.
        """
        for net in self.networks:
            yield net