# -*- coding: UTF8 -*-

"""

TODO:
- Fix arguments of find_contact()
- Implement PING protocol

"""

import socket
import random
import logging

from typing import Tuple
from json.decoder import JSONDecodeError
from unittest import mock

from .node import Node
from .config import Config
from .request import Request
from .requests import Requests
from .encryption import Encryption
from .message import Message, OwnMessage
from .contact import Contact, OwnContact, Beacon
from .utils import decode_json, get_primary_local_ip_address, get_timestamp
from .validation import is_valid_received_message, is_valid_request, is_valid_contact, verify_received_aes_key


class Network:

    def __init__(self, master_node):
        self.master_node = master_node

        self.host = get_primary_local_ip_address()  # TODO: listen on all interfaces, making this attribute deprecated.

    ####################
    # Requests section #
    ####################

    def route_request(self, request: Request, broadcast: bool = True) -> None:
        """
        This method is used to route the requests to their corresponding functions, in order to process them.

        :param Request request: The request, as a Request object.
        :param bool broadcast: Whether we want to broadcast the message.
        The only case it should be set to False is if we are replying to a specific request.
        """

        """
        For each request, we first verify it is valid, and then process it.
        """

        # If the request is already in the raw_requests database, we skip it.
        if self.master_node.databases.raw_requests.is_request_known(request.get_id()):
            return

        self.store_raw_request_depending_on_type(request)

        status = request.status

        def _broadcast(req):
            if broadcast:
                self.broadcast_request(req)
        # End of _broadcast method.

        def _log_invalid_req(req):
            log_msg = f'Invalid {req.status!r} request ({req.get_id()!r})'
            if Config.verbose:
                log_msg = f'{log_msg}: {req.to_json()}'
            logging.debug(log_msg)
        # End of _log_invalid_req method.

        if status == "WUP_INI":  # What's Up Protocol Initialization
            if not Requests.is_valid_wup_ini_request(request):
                _log_invalid_req(request)
                return
            self.handle_what_is_up_init(request)
            return
        elif status == "WUP_REP":  # What's Up Protocol Reply
            if not Requests.is_valid_wup_rep_request(request):
                _log_invalid_req(request)
                return
            self.handle_what_is_up_reply(request)
            return

        elif status == "BCP":  # BroadCast Protocol
            if not Requests.is_valid_bcp_request(request):
                _log_invalid_req(request)
                return
            self.handle_broadcast(request)
            return

        elif status == "DNP":  # Discover Nodes Protocol
            if not Requests.is_valid_dp_request(request):
                _log_invalid_req(request)
                return
            self.handle_discover_nodes(request)
            return

        elif status == "DCP":  # Discover Contact Protocol
            if not Requests.is_valid_dp_request(request):
                _log_invalid_req(request)
                return
            self.handle_discover_contact(request)
            return

        # All requests above are neither stored nor broadcast back.
        # Only those below are, and only if they are valid.

        if status == "MPP":  # Message Propagation Protocol
            if not is_valid_received_message(request.data):
                _log_invalid_req(request)
                return
            _broadcast(request)
            self.handle_message(request)
            return

        elif status == "NPP":  # Node Publication Protocol
            if not Requests.is_valid_npp_request(request):
                _log_invalid_req(request)
                return
            _broadcast(request)
            self.handle_new_node(request)
            return

        elif status == "CSP":  # Contact Sharing Protocol
            if not Requests.is_valid_csp_request(request):
                _log_invalid_req(request)
                return
            _broadcast(request)
            contact = Contact.from_dict(request.data)
            self.master_node.databases.contacts.add_contact(contact)
            return

        elif status == "KEP":  # Keys Exchange Protocol
            if not Requests.is_valid_kep_request(request):
                _log_invalid_req(request)
                return
            _broadcast(request)
            self.negotiate_aes(request)
            return

        else:
            # The request has an invalid status.
            logging.warning(f'Captured request calling unknown protocol: {status!r}.')
            return

    def handle_raw_request(self, json_request: str) -> None:
        """
        This function is called everytime we receive a JSON request.
        It converts the request to a dictionary (if structurally valid) and routes it.

        :param str json_request: A request, as a JSON-encoded string.
        """
        dict_request = decode_json(json_request)

        if not is_valid_request(dict_request):
            return

        request = Request.from_dict(dict_request)

        self.route_request(request)

    ############################
    # Request handling section #
    ############################

    # All methods of this section must have only one argument: request, a valid Request object.

    def negotiate_aes(self, request: Request) -> bool:
        """
        Negotiate an AES key.
        This function is called by two events:
        - When we receive a Keys Exchange (KEP) request,
        - When we discover a new node (Node Publication Protocol).
        Note that we are not guaranteed that this request is for us.

        :param Request request: A valid request.
        :return bool: True if the negotiation is over, False otherwise.

        TODO: Get rid of assertions
        """

        def concatenate_keys(key1: bytes, key2: bytes) -> tuple:
            """
            Concatenate the two keys and derive a nonce.

            :param bytes key1: Half an AES key.
            :param bytes key2: Half an AES key.
            :return tuple: 2-tuple (bytes: aes_key, bytes: nonce)
            """
            if key1 < key2:
                aes_key = key1 + key2
            elif key1 > key2:
                aes_key = key2 + key1
            else:
                # Almost impossible case where the two keys are the same
                raise ValueError("Wait, what ??!")
            nonce = Encryption.derive_nonce_from_aes_key(aes_key)
            return aes_key, nonce

        def propagate(half_aes_key: bytes) -> None:
            """
            Wrapper used to broadcast the KEP request over the network.

            :param bytes half_aes_key: Half an AES key.
            """
            req = Requests.kep(half_aes_key, self.master_node, author_node)
            self.broadcast_request(req)

        def store(key_identifier: str, key: bytes, nonce: bytes or None) -> None:
            """
            Store the AES key in the conversations database.

            :param str key_identifier: A key ID ; the Node's ID.
            :param bytes key: The AES key.
            :param bytes|None nonce: The nonce, bytes if the negotiation is over, None otherwise.
            """
            # Concatenate key and nonce if the later is passed.
            if nonce is not None:
                f_key = key + nonce
            else:
                f_key = key
            self.master_node.databases.conversations.store_aes(key_identifier, f_key, get_timestamp())

        def get_peer_half_key() -> bytes or None:
            if not verify_received_aes_key(request.data["key"], author_node.get_rsa_public_key()):
                # The AES key sent is invalid.
                return

            # This AES key's length is 16 bytes.
            se_en_half_key = request.data["key"]["value"]
            half_key = Encryption.decrypt_asymmetric(self.master_node.get_rsa_private_key(), se_en_half_key)
            assert len(half_key) == Config.aes_keys_length // 2

            return half_key

        def finish_negotiation() -> None:
            """
            Used when we already initialized the negotiation and we just received the second part to conclude it.
            At the end of this function, we have a valid AES key for communicating with this node.
            """
            stored_half_key, nonce = self.master_node.databases.conversations.get_decrypted_aes(key_id)

            # nonce should be empty and aes_key should be exactly half the expected key length
            assert nonce is None
            assert len(stored_half_key) == Config.aes_keys_length // 2

            half_key = get_peer_half_key()
            if half_key is None:
                return

            key, nonce = concatenate_keys(half_key, stored_half_key)

            assert len(key) == Config.aes_keys_length
            assert len(nonce) == Config.aes_keys_length // 2

            store(key_id, key, nonce)
            logging.info(f'Finished negotiation with {key_id!r}')

        def continue_negotiation() -> None:
            """
            Used when an KEP request is received but we haven't initiated it.
            We then proceed to send the other half of the key.
            At the end of this function, we have a valid AES key for communicating with this node.
            """
            new_half_key = Encryption.create_half_aes_key()
            half_key = get_peer_half_key()
            if half_key is None:
                return

            key, nonce = concatenate_keys(half_key, new_half_key)

            assert len(key) == Config.aes_keys_length
            assert len(nonce) == Config.aes_keys_length // 2

            propagate(new_half_key)
            store(key_id, key, nonce)
            logging.info(f'Continued negotiation with {key_id!r}')

        def new_negotiation() -> None:
            """
            Used when initializing a new negotiation, usually when acknowledging a new node.
            We send our half, store it and wait.
            When receiving the second part, we will call "finish_negotiation()".
            """
            half_aes_key = Encryption.create_half_aes_key()
            # We don't encrypt it here, we will take care of that when creating the KEP request.
            propagate(half_aes_key)
            store(key_id, half_aes_key, None)
            logging.info(f'Initiated negotiation with {key_id!r}')

        if not self.master_node.databases.are_node_specific_databases_open:
            return False

        status: str = request.status
        own_id = self.master_node.get_id()

        # We will take the author's RSA public key to encrypt our part of the AES key.
        if status == "KEP":
            author_node = Node.from_dict(request.data['author'])
            recipient_node = Node.from_dict(request.data['recipient'])

            # If we are not the recipient, end.
            recipient_id = recipient_node.get_id()
            if recipient_id != own_id:
                if Config.log_full_network:
                    msg = f"{status} request {request.get_id()!r} is not addressed to us"
                    if Config.verbose:
                        msg += f": got {recipient_id!r}, ours is {own_id!r}"
                return False

        elif status == "NPP":
            author_node = Node.from_dict(request.data)

        else:
            msg = f'Invalid protocol {request.status!r} called function {Network.negotiate_aes.__name__!r}'
            logging.critical(msg)
            raise ValueError(msg)
        key_id = author_node.get_id()

        # Special case: if we are the node of the NPP request, we'll create a new AES key for ourself.
        if status == "NPP" and key_id == own_id:
            aes_key, nonce = Encryption.create_aes()
            store(key_id, aes_key, nonce)
            return True

        # If the key is already negotiated, end.
        if self.master_node.databases.conversations.is_aes_negotiated(key_id):
            # You might want to add a renegotiation system here.
            return True
        # If the negotiation has been launched, check if it is expired.
        # If it is, remove it.
        # Otherwise, this means we are receiving the second part of the AES key,
        # and therefore we can conclude the negotiation.
        # If the negotiation has not been launched, we will be initiating it.
        if self.master_node.databases.conversations.is_aes_negotiation_launched(key_id):
            if self.master_node.databases.conversations.is_aes_negotiation_expired(key_id):
                self.master_node.databases.conversations.remove_aes_key(key_id)
                new_negotiation()
                return False
            # If the negotiation has not yet expired, we conclude it.
            else:
                if status == "KEP":
                    finish_negotiation()
                    return True
        else:
            if status == "KEP":
                continue_negotiation()
                return True
            elif status == "NPP":
                new_negotiation()
                return False
        return False

    def handle_message(self, request: Request) -> None:
        """
        This method is used when receiving a new message.
        It is called after the request has been broadcast back and stored in the raw_requests database,
        and will take care of storing the message if we can decrypt its content.

        :param Request request: A MPP request.
        """
        node = Node.from_dict(request.data["author"])
        if not node:
            return

        if not self.master_node.databases.conversations.is_aes_negotiated(node.id):
            # Here, the negotiation is not done yet, so we launch it.
            # If it returns False, meaning the negotiation is not over, we end the function.
            # Otherwise, we continue.
            if not self.negotiate_aes(request):
                return

        # The AES keys have been negotiated, so we can proceed.

        aes_key, nonce = self.master_node.databases.conversations.get_decrypted_aes(node.get_id())
        message_dec = Message.from_dict_encrypted(aes_key, nonce, request.data)

        if not message_dec:
            # We won't log anything else: any error should have been logged by the message constructor above.
            return

        message_enc = Message.from_dict(request.data)

        # At this point, the message has been read and we can store it (encrypted) in our conversations database.
        self.master_node.databases.conversations.store_new_message(
            node.get_id(),
            message_enc
        )

    def handle_new_node(self, request: Request) -> None:
        """
        Called when we receive a NPP request.

        :param Request request: A NPP request.
        """
        node = Node.from_dict(request.data)
        # Even if the node information was validated beforehand,
        # we'll check if it worked anyway.
        if not node:
            return
        self.negotiate_aes(request)
        self.master_node.databases.nodes.add_node(node)

    def handle_what_is_up_init(self, request: Request) -> None:
        """
        Called when we receive a What's Up init request.

        :param Request request: A WUP_INI request.
        """
        request_timestamp = int(request.data["timestamp"])

        contact_info = request.data["author"]
        contact = Contact.from_dict(contact_info)

        if not contact:
            # Double check
            return

        all_requests = self.master_node.databases.raw_requests.get_all_raw_requests_since(request_timestamp)
        for request in all_requests.values():
            req = Requests.wup_rep(request)
            self.send_request(req, contact)

    def handle_what_is_up_reply(self, request: Request) -> None:
        """
        Called when receiving a What's Up reply request.

        :param Request request: A WUP_REP request.
        """
        inner_request = Request.from_dict(request.data)

        if not inner_request:
            return

        # Route the request.
        self.route_request(inner_request, broadcast=False)

    def handle_broadcast(self, request: Request) -> None:
        pass  # TODO

    def handle_discover_nodes(self, request: Request) -> None:
        """
        Handles Discover Nodes requests.
        The request must be valid.

        :param Request request: A valid DNP request.
        """
        contact = Contact.from_dict(request.data["author"])

        # Add the contact requesting the nodes if we don't know it already.
        if not self.master_node.databases.contacts.contact_exists(contact.get_id()):
            self.master_node.databases.contacts.add_contact(contact)

        for node in self.master_node.databases.nodes.get_all_nodes():
            req = Requests.npp(node)
            self.send_request(req, contact)

    def handle_discover_contact(self, request: Request) -> None:
        """
        Handles Discover Contacts requests.
        The request must be valid.

        :param Request request: A valid CSP request.
        """
        contact = Contact.from_dict(request.data["author"])

        # Add the contact if we don't know it already.
        if not self.master_node.databases.contacts.contact_exists(contact.get_id()):
            self.master_node.databases.contacts.add_contact(contact)

        for contact_object in self.master_node.databases.contacts.get_all_contacts():
            req = Requests.csp(contact_object)
            self.send_request(req, contact)

    def store_raw_request_depending_on_type(self, request: Request) -> None:
        """
        Takes a raw request and stores it if it is appropriate to do so.

        :param Request request: The request to store.
        """
        if request.status not in Config.store_requests:
            return
        self.master_node.databases.raw_requests.add_new_raw_request(request)

    #####################
    # Protocols section #
    #####################

    def what_is_up(self) -> None:
        """
        Chooses a node (preferably a beacon) and asks for all requests since the last one we received.
        This method is called when a RSA private key is loaded into the client.

        TODO: Take care of the case where we know less than 10 contacts
        """
        last_received_request = self.master_node.databases.raw_requests.get_last_received()

        if not last_received_request:
            # We didn't receive any request yet.
            return

        for contact in self.find_available_contact():
            req = Requests.wup_ini(last_received_request.timestamp, contact)
            for _ in range(10):  # 10 tries
                if self.send_request(req, contact):
                    return

    def request_nodes(self) -> None:
        """
        Creates a DNP request and sends it to one contact.
        """
        own_contact = OwnContact('private')
        req = Requests.dnp(own_contact)
        for contact in self.find_available_contact():
            if self.send_request(req, contact):
                logging.info(f'Requested new contacts to {contact.get_address()}:{contact.get_port()}')
                return

    def request_contacts(self) -> None:
        """
        Creates a DCP request and sends it to one contact.
        """
        own_contact = OwnContact('private')
        req = Requests.dnp(own_contact)
        for contact in self.find_available_contact():
            if self.send_request(req, contact):
                logging.info(f'Requested new contacts to {contact.get_address()}:{contact.get_port()}')
                return

    ################################
    # Network interactions section #
    ################################

    def send_message(self, recipient: Node, own_message: OwnMessage) -> None:

        def prepare_message_for_recipient(node: Node, message: OwnMessage) -> None:
            """
            Prepares a message by encrypting its values.
            This message is addressed to a specific node.
            """
            aes_key, nonce = self.master_node.databases.conversations.get_decrypted_aes(node.get_id())
            aes = Encryption.construct_aes_object(aes_key, nonce)
            message.prepare(aes)
        # End of prepare_message_for_recipient method.

        if not self.master_node.databases.conversations.is_aes_negotiated(recipient.get_id()):
            logging.error(f'Tried to send a message to node {recipient.get_id()}, '
                          f'but AES negotiation is not complete.')
            return

        prepare_message_for_recipient(recipient, own_message)

        if not own_message.is_prepared():
            logging.error(f'Something went wrong during the preparation of the message.')
            return

        req = Requests.mpp(own_message)
        self.broadcast_request(req)

    def find_available_contact(self):
        contacts = self.get_all_contacts()
        for contact in contacts:
            # TODO: Add network verification
            yield contact

    def get_all_contacts(self):
        """
        Returns a contact if we know any.
        It will prioritize choosing beacons before regular contacts.
        The contact returned is not assured to be available on the network.

        :return Contact|None: A Contact object if we could find one, None otherwise.
        """

        def _get_beacons(beacons_list: list) -> Contact or None:
            for beacon_info in beacons_list:
                beacon_obj = Beacon.from_raw_address(beacon_info)

                if not beacon_obj:
                    # The beacon information is invalid.
                    logging.warning(f"A beacon is invalid: {beacon_info!r}")
                    continue

                yield beacon_info

        def __get_contacts(beacons_list: list, contacts_list: list) -> Contact or None:
            beacons = _get_beacons(beacons_list)
            if beacons:
                for beacon in beacons:
                    yield beacon

            for contact_obj in contacts_list:
                yield contact_obj

        # Gets the beacons and contacts lists.
        own_contact = OwnContact('private')
        all_beacons = Config.beacons
        all_contacts = self.master_node.databases.contacts.get_all_contacts(exclude=[own_contact.get_id()])

        random.shuffle(all_beacons)
        random.shuffle(all_contacts)
        contacts = __get_contacts(all_beacons, all_contacts)

        for contact in contacts:
            yield contact

    def listen_for_autodiscover_packets(self, stop_event) -> None:

        def receive_all(sock: socket.socket) -> Tuple[bytes, Tuple[str, int]]:
            """
            Receives all parts of a network-sent message.

            :param socket.socket sock: The socket object.
            :return: The complete message and the information of the sender.
            """
            data = bytes()
            while True:
                # Could there be interlaced packets (two different addresses gathered during successive loops) ?
                part, add = sock.recvfrom(Config.network_buffer_size)
                data += part
                if len(part) < Config.network_buffer_size:
                    # Either 0 or end of data
                    break
            return data, add

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind(("", Config.broadcast_port))
            while not stop_event.isSet():
                request_raw, address = receive_all(sock=s)
                if Config.log_full_network:
                    logging.debug(f'Received packet: {request_raw!r} from {address!r}')
                # The request is not assured to be JSON, could be text, raw bytes or anything else.
                json_request = Encryption.decode_bytes(request_raw)
                try:
                    dict_request = decode_json(json_request)
                except JSONDecodeError:
                    continue

                req_add = dict_request['address'].split(Config.contact_delimiter)[0]
                sender_add = address[0]
                own_add = OwnContact('private').get_address()

                if req_add != sender_add:
                    # If the addresses are not the same.
                    continue
                if req_add == own_add:
                    # If the request's sender address is ours.
                    continue

                if is_valid_contact(dict_request):
                    contact = Contact.from_dict(dict_request)
                    contact.set_last_seen()
                    msg = f'We received a new contact by listening on the broadcast: {json_request}'
                    # The following verification is already done in the add contact,
                    # but we do it anyway to be able to tell if it was already present or not.
                    if not self.master_node.databases.contacts.contact_exists(contact.get_id()):
                        self.master_node.databases.contacts.add_contact(contact)
                    else:
                        msg += ' (already registered)'
                    if Config.log_full_network:
                        logging.debug(msg)

    def broadcast_autodiscover(self) -> None:
        # Resource: https://github.com/ninedraft/python-udp
        if len(self.master_node.databases.contacts.get_all_contacts_ids()) > Config.broadcast_limit:
            # If we know enough contacts, we don't need to broadcast.
            # TODO: find a way of stopping calls to this function
            return
        own_contact = OwnContact('private')
        own_contact_information = Encryption.encode_string(own_contact.to_json())
        self.send_broadcast(own_contact_information)

    def send_broadcast(self, info: bytes) -> None:
        """
        Takes a contact information as a bytes object (containing JSON), and broadcasts it.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(info, ('<broadcast>', Config.broadcast_port))
            if Config.log_full_network:
                logging.debug(f'Broadcast own contact information: {info!r}')

    def listen_for_requests(self, stop_event) -> None:
        """
        Setup a server and listens on a port.
        It requires a TCP connection to transmit information.
        """

        def receive_all(sock: socket.socket) -> bytes:
            """
            Receives all parts of a network-sent message.

            :param socket.socket sock: The socket object.
            :return bytes: The complete message.
            """
            data = bytes()
            while True:
                part = sock.recv(Config.network_buffer_size)
                data += part
                if len(part) < Config.network_buffer_size:
                    break
            return data

        with socket.socket() as server_socket:
            server_socket.bind((self.host, Config.sami_port))
            server_socket.listen(Config.network_max_conn)

            while not stop_event.isSet():
                connection, address = server_socket.accept()
                raw_bytes_request = receive_all(connection)
                json_request = Encryption.decode_bytes(raw_bytes_request)
                try:
                    dict_request = decode_json(json_request)
                except JSONDecodeError:
                    if Config.log_full_network:
                        log_msg = 'Received an unknown packet'
                        if Config.verbose:
                            log_msg += f': {raw_bytes_request}'
                        logging.debug(log_msg)
                    continue
                request = Request.from_dict(dict_request)
                if request:  # If we managed to get a valid request.
                    if Config.log_full_network:
                        log_msg = f'Received {request.status!r} request {request.get_id()!r} from {address}'
                        if Config.verbose:
                            log_msg += f': {dict_request}'
                        logging.info(log_msg)
                    # We'll route it.
                    self.route_request(request)
                else:
                    if Config.log_full_network:
                        log_msg = f'Received invalid request from {address}'
                        if Config.verbose:
                            log_msg += f': {dict_request}'
                        logging.info(log_msg)
                connection.close()

    def broadcast_request(self, request: Request) -> None:
        """
        Broadcast a request to all known contacts.

        :param Request request:
        """
        contacts = list(self.get_all_contacts())
        for contact in contacts:
            self.send_request(request, contact)

        logging.info(f'Broadcast request {request.get_id()!r} to {len(contacts)} contacts.')

    def send_dummy_data_to_self(self) -> None:
        # Mocks the ``to_json()`` method.
        # As we don't want to send a dirty request, we will make it return an empty string.
        # Sockets will send this
        with mock.patch('sami.Request.to_json') as mock_req_to_json:
            mock_req_to_json.return_value = ''
            req = Request('', {}, 0, 0)
            own_contact = OwnContact('private')
            own_contact_information = Encryption.encode_string(own_contact.to_json())
            self.send_broadcast(own_contact_information)  # Used to end broadcast listening
            self.send_request(req, Contact.from_dict(own_contact.to_dict()))  # Used to end requests listening

    def send_request(self, request: Request, contact: Contact) -> bool:
        """
        Send a request to a specific contact.

        :param Request request: The request to send.
        :param Contact contact: The contact to send the request to.
        :return bool: True if it managed to send the request, False otherwise.

        TODO : error handling
        """
        address = contact.get_address()
        port = contact.get_port()

        self.store_raw_request_depending_on_type(request)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(Config.contact_connect_timeout)
            try:
                client_socket.connect((address, port))
                client_socket.send(Encryption.encode_string(request.to_json()))
            except (socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError):
                if Config.log_full_network:
                    logging.info(f'Could not send request {request.get_id()!r} to {address}:{port}')
            except Exception as e:
                logging.warning(f'Unhandled {type(e)} exception caught: {e!r}')
            else:
                if Config.log_full_network:
                    logging.info(f'Sent {request.status!r} request {request.get_id()!r} to {address}:{port}')
                return True
        return False
