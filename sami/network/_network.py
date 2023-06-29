from __future__ import annotations

import ipaddress
import socket
import threading as th
from typing import Generator

import pydantic
from loguru import logger

from ..config import settings
from ..objects import Contact, OwnContact
from ..utils import shuffled
from ._queue import handle_queue, send_queue
from .requests import BCP, WUP_INI, Request
from .utils import get_primary_ip_address, in_same_subnet


class ResponseExpected(pydantic.BaseModel):
    request: Request


class Network:

    """
    Network interface, linked to an actual NIC (Network Interface Card).
    As such, this Network has its own dedicated contact.
    """

    def __init__(self, contact: OwnContact):
        self.contact = contact
        self.address = self.contact.address

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

        # Cache that keeps track of requests we are expecting a response to
        self.expecting_response: dict[Contact, ResponseExpected] = {}

    def __hash__(self):
        return hash(self.address)

    @property
    def is_primary(self) -> bool:
        add = get_primary_ip_address()  # TODO: handle empty
        return self.address == ipaddress.ip_address(add)

    def what_is_up(self) -> None:
        """
        Selects a node and asks for all requests since the last we received.
        This method is called when a private value is loaded into the client.

        TODO: Keep running until we receive a response,
         timeout and send to another
        """
        # Note: we don't pass the request to the send queue because this
        #  method is only called by the job scheduler.
        if len(Contact.all()) < settings.min_peers:
            # We don't know enough unique contacts
            return

        last_request_received = Request.get_last()
        if not last_request_received:
            # We didn't receive any request yet
            return

        req = Request.new(WUP_INI.new(last_request_received.timestamp, self.contact))
        for contact in self.contacts():
            if self.send_request(req, contact):
                return

    def start(self) -> None:
        """
        Starts listening on this network interface.
        """
        self.listen_requests_thread.start()
        self.listen_broadcast_thread.start()

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

    def contacts(self) -> Generator[Contact, None, None]:
        """
        Iterative over the contacts we know, and that we can contact via
        this interface.
        """
        # First, we yield the beacons
        for beacon in shuffled(settings.beacons.get()):
            if self.can_connect_to(beacon):
                yield beacon
        # Then, the contacts
        for contact in shuffled(Contact.all()):
            if self.can_connect_to(contact):
                yield contact

    def _receive_all(
        self, sock: socket.socket, address_check: str | None = None
    ) -> tuple[bytes, tuple[str, int]]:
        """
        Receives all parts of a network-sent message.
        Takes a socket object and returns a tuple with
        (1) the complete message as bytes
        (2) a tuple with (1) the address and (2) distant port of the sender.
        """
        data = bytes()
        while True:
            # FIXME: Could there be interlaced packets (two different
            #  addresses gathered during successive loops) ?
            part, addr = sock.recvfrom(settings.network_buffer_size)
            if address_check:
                if addr == address_check:
                    data += part
            else:
                data += part
            if len(part) < settings.network_buffer_size:
                # Either 0 or end of data
                break
        return data, addr

    def listen_for_autodiscover_packets(self) -> None:
        """
        Captures Requests from the LAN broadcast traffic and routes them.
        FIXME: Currently allows for all kinds of request, but in practice,
         we want to accept BCP exclusively
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind(("", settings.broadcast_port))
            while not self._stop_event.is_set():
                raw_request, (address, port) = self._receive_all(s)
                try:
                    request = Request.from_bytes(raw_request)
                except pydantic.ValidationError:
                    pass
                else:
                    handle_queue.put((request, address))

    def listen_for_requests(self) -> None:
        """
        Sets up a server and listens on a port.
        It requires a TCP connection to receive information.
        """
        with socket.socket() as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.address, settings.sami_port))
            server_socket.listen()
            while not self._stop_event.is_set():
                connection, address = server_socket.accept()
                raw_request, _ = self._receive_all(connection, address)
                try:
                    request = Request.from_bytes(raw_request)
                except pydantic.ValidationError:
                    pass
                else:
                    handle_queue.put((request, address))
                connection.close()

    def broadcast(self, request: Request) -> None:
        """
        Broadcast a Request to all known (and reachable from this NIC) Contacts
        """
        contacts = list(self.contacts())
        for contact in contacts:
            send_queue.put((self, request, contact))

        logger.info(f"Broadcast request {request.id!r} to {len(contacts)} contacts")

    def broadcast_request_lan(self, bcp_request: Request[BCP]) -> None:
        """
        Broadcasts a Request on the local network (broadcast).
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(
                data=bcp_request.to_bytes(),
                address=("<broadcast>", settings.broadcast_port),
            )

    def send_request(self, request: Request, contact: Contact) -> bool:
        """
        Send a Request to a specific Contact.
        Returns True if we managed to send the Request, False otherwise.
        """
        if not self.can_connect_to(contact):
            return False

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
            client_sock.settimeout(settings.contact_connect_timeout)
            req = request.to_bytes()
            try:
                client_sock.connect((contact.address, contact.port))
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
                logger.info(f"Could not send request {request.id!r} to {contact!r}")
            except Exception as e:
                logger.error(f"Unhandled {type(e)} exception caught: {e!r}")
            else:
                logger.info(
                    f"Sent {request.status!r} request {request.id!r} to {contact!r}"
                )
                return True
        return False
