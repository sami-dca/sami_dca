# -*- coding: UTF8 -*-

import socket
from random import randint

from .node import Node
from .utils import Utils
from .nodes import Nodes
from .config import Config
from .request import Request
from .contact import Contact
from .requests import Requests
from .contacts import Contacts
from .structures import Structures
from .encryption import Encryption
from .raw_requests import RawRequests
from .message import Message, OwnMessage


class Network:

    def __init__(self, master_node, host: str, port: int):
        self.raw_requests = RawRequests()
        self.contacts = Contacts()
        self.nodes = Nodes()

        self.master_node = master_node

        self.host = host
        self.port = port

    def __del__(self):
        self.master_node.display.mainFrame.set_server_display(False)

    # Validation section

    @staticmethod
    def is_request_valid(request: dict) -> bool:
        """
        Takes a request as a JSON-encoded request and checks it is valid.
        Valid does not mean trustworthy.

        :param str request: A JSON-encoded dictionary.
        """
        if not Utils._validate_fields(request, Structures.request_standard_structure):
            return False

        return True

    # Requests section

    def route_request(self, request: Request, broadcast: bool = True) -> None:
        """
        This method is used to route the requests to their corresponding functions, in order to process them.

        :param Request request: The request, as a Request object.
        :param bool broadcast: Whether we want to broadcast the message.
        The only case it should be set to False is if we are replying to a specific request.
        """

        """
        For each of the requests, we first verify it is valid, 
        and then process it.
        """

        def broadcast_and_store(req):
            if broadcast:
                self.broadcast_request(req)
            self.raw_requests.add_new_raw_request(req)

        if request.status == "WUP_INI":  # What's Up Protocol Initialization
            self.handle_what_is_up_init(request)
            return
        elif request.status == "WUP_REP":
            self.handle_what_is_up_reply(request)  # What's Up Protocol Reply
            return

        elif request.status == "DPP":
            if not Requests.is_valid_dp_request(request):  # Discover Pub Protocol
                return
            self.handle_discover_pub(request)
            return

        elif request.status == "DCP":  # Discover Contact Protocol
            if not Requests.is_valid_dp_request(request):
                return
            self.handle_discover_contact(request)
            return

        # All requests above are neither stored nor broadcasted back.
        # Only those below are, and only if they are valid.

        if request.status == "MPP":  # Message Propagation Protocol
            if not Message.is_received_message_valid(request.data):
                return
            broadcast_and_store(request)
            self.handle_message(request)

        elif request.status == "NPP":  # Node Publication Protocol
            if not Requests.is_valid_npp_request(request):
                return
            broadcast_and_store(request)
            node = Node.from_dict(request.data)
            self.nodes.add_node(node)

        elif request.status == "CSP":  # Contact Sharing Protocol
            if not Requests.is_valid_csp_request(request):
                return
            broadcast_and_store(request)
            contact = Contact.from_dict(request.data)
            self.contacts.add_contact(contact)

        elif request.status == "KEP":  # Keys Exchange Protocol
            if not Requests.is_valid_kep_request(request):
                return
            broadcast_and_store(request)
            self.negotiate_aes(request)

        else:
            # The request has an invalid status.
            return

    def handle_raw_request(self, json_request: str) -> None:
        """
        This function is called everytime we receive a JSON request.
        It converts the request to a dictionary (if structurally valid) and routes it.

        :param str json_request: A request, as a JSON-encoded string.
        """
        dict_request = Utils.decode_json(json_request)

        if not self.is_request_valid(dict_request):
            return

        request = Request.from_dict(dict_request)

        self.route_request(request)

    # Request handling section
    # All methods of this section must have only one argument: request, as Request object.

    def negotiate_aes(self, request: Request) -> bool:
        """
        Negotiate an AES key.
        This function is called by two events:
        - When we receive an Keys Exchange (KEP) request,
        - When we discover a new node (Node Publication Protocol).

        :param Request request: A valid request.
        :return bool: True if the negotiation is over, False otherwise.
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
            Wrapper used to broadcast the AKE request over the network.

            :param bytes half_aes_key: Half an AES key.
            """
            req = Requests.kep(half_aes_key, self.master_node, node)
            self.broadcast_request(req)

        def store(key_id: str, key: bytes, nonce: bytes or None) -> None:
            """
            Store the AES key in the conversations database.

            :param str key_id: A key ID ; the Node's ID.
            :param bytes key: The AES key.
            :param bytes|None nonce: The nonce.
            """
            self.master_node.conversations.store_aes(self.master_node.get_rsa_public_key(), key_id, key, nonce)

        def finish_negotiation() -> None:
            """
            Used when a negotiation is already initialized and we want to conclude it.
            At the end of this function, we have a valid AES key for communicating with this node.
            """
            key = self.master_node.conversations.get_decrypted_aes(self.master_node.get_rsa_private_key(), key_id)
            aes_key, nonce = key
            half_aes_key = Encryption.create_half_aes_key()
            key, nonce = concatenate_keys(aes_key, half_aes_key)
            propagate(half_aes_key)
            store(key_id, key, nonce)

        def continue_negotiation() -> None:
            """
            Used when an AKE request is received but we haven't initialized it.
            We then proceed to send the other half of the key.
            At the end of this function, we have a valid AES key for communicating with this node.
            """
            half_aes_key = Encryption.create_half_aes_key()
            rsa_public_key = Encryption.construct_rsa_object(request.data["author"]["rsa_n"],
                                                             request.data["author"]["rsa_e"])
            Encryption.verify_received_aes_key(request.data["key"], rsa_public_key)

            # This AES key's length is 16 bytes.
            aes_key = Encryption.decrypt_asymmetric(self.master_node.get_rsa_private_key(), request.data["key"])

            key, nonce = concatenate_keys(aes_key, half_aes_key)
            propagate(half_aes_key)
            store(key_id, key, nonce)

        def new_negotiation() -> None:
            """
            Used when initializing a new negotiation, mainly when acknowledging a new node.
            We send our half, store it and wait.
            When receiving the second part, we will call "finish_negotiation()".
            """
            half_aes_key = key = Encryption.create_half_aes_key()
            propagate(half_aes_key)
            store(key_id, key, None)

        if request.status == "KEP":
            node = Node.from_dict(request.data["author"])
        elif request.status == "NPP":
            node = Node.from_dict(request.data)
        else:
            raise ValueError
        key_id = node.get_id()

        # If the key is already negotiated, end.
        if self.master_node.conversations.is_aes_negotiated(key_id):
            # You might want to add a renegotiation system here.
            return True
        # If the negotiation has been launched, check if it is expired.
        # If it is, remove it.
        # If it is not expired, this means we are receiving the second part of the AES key,
        # and therefore we can conclude the negotiation.
        if self.master_node.conversation.is_aes_negotiation_launched(key_id):
            if self.master_node.conversations.is_aes_negotiation_expired(key_id):
                self.master_node.conversations.remove_aes_key(key_id)
                new_negotiation()
            # If the negotiation has not yet expired, we then conclude it.
            else:
                status = request.status
                if status == "AKE":  # AKE request from a node.
                    finish_negotiation()
                    return True
                else:
                    raise ValueError(f"Invalid request status \"{status}\"")
        # If the negotiation has not been launched, we will be initiating it.
        else:
            status = request.status
            if status == "KEP":
                continue_negotiation()
                return True
            elif status == "NPP":
                new_negotiation()
                return False
            else:
                raise ValueError(f"Invalid request status \"{status}\"")

    def handle_message(self, request: Request) -> None:
        """
        This method is used when receiving a new message.
        It is called after the request has been broadcasted back,
        and will take care of storing the message if we can decrypt its content.

        :param Request request: A MPP request.
        """
        node = Node.from_dict(request.data["author"])
        if not node.auto_aes():
            # Here, the negotiation is not done yet, so we launch it.
            # If it returns False, meaning the negotiation is not over, we end the function.
            # Otherwise, we continue.
            if not self.negotiate_aes(request):
                return

        # The AES negotiation has been established, so we can proceed.

        # Tries to set the AES values again.
        # If for any reason it fails, end the function.
        if not node.auto_aes():
            return

        aes_key, nonce = node.get_aes_attr()
        message = Message.from_dict_encrypted(aes_key, nonce, request.data)

        if message is None:
            return

        # At this point, the message has been read and we can store it in our own database.
        self.master_node.conversations.store_new_message(
            self.master_node.get_rsa_private_key(),
            node.get_id(),
            message
        )

    def handle_what_is_up_init(self, request: Request) -> None:
        """
        Called when we receive a What's Up init request.

        :param Request request: A WUP_INI request.
        """
        request_timestamp = int(request.data["timestamp"])

        contact_info = request.data["author"]
        contact = Contact.from_dict(contact_info)

        all_requests = self.raw_requests.get_all_raw_requests_since(request_timestamp)
        for request in all_requests.values():
            req = Request.from_dict(request)
            req = Requests.wup_rep(req)
            self.send_request(req, contact)

    def handle_what_is_up_reply(self, request: Request) -> None:
        """
        Called when receiving a What's Up replies request.

        :param Request request: A WUP_REP request.
        """
        if not Requests.is_valid_wup_rep_request(request):
            return

        inner_request = Request.from_dict(request.data)

        # Route the request.
        self.route_request(inner_request, broadcast=False)

    def handle_discover_pub(self, request: Request) -> None:
        """
        Handles the Discover Pub requests.
        The request must be valid.

        :param Request request: A valid DPP request.
        """
        contact = Contact.from_raw_address(request.data["address"])

        if not self.contacts.contact_exists(contact.get_id()):
            self.contacts.add_contact(contact)

        for node in self.master_node.nodes.get_all_node_ids():
            node_object = Node.from_dict(node)
            req = Requests.npp(node_object)
            self.send_request(req, contact)

    def handle_discover_contact(self, request: Request) -> None:
        """
        Handles the Discover Contacts requests.
        The request must be valid.

        :param Request request: A valid CSP request.
        """
        contact = Contact.from_raw_address(request.data["address"])

        if not self.contacts.contact_exists(contact.get_id()):
            self.contacts.add_contact(contact)

        for contact_id in self.contacts.get_all_contacts_ids():
            contact_object = Contact.from_dict(self.contacts.get_contact_info(contact_id))
            req = Requests.csp(contact_object)
            self.send_request(req, contact)

    # Protocols section

    def what_is_up(self) -> None:
        """
        Chooses a node (preferably a beacon) and asks for all requests since the last one we received.
        This method is called when a RSA private key is loaded into the client.
        """

        def get_node_list_id(node_list: list, excluded: list) -> int:
            while True:
                random_id = randint(0, len(node_list) - 1)
                if random_id not in excluded:
                    break
            return random_id

        all_requests = self.raw_requests.get_all_raw_requests()
        # Gets the timestamp of the last request we receive.
        # This is a hard-coded version, please optimize.
        last_message_timestamp: int = 0
        for request in all_requests:
            if request["timestamp"] > last_message_timestamp:
                last_message_timestamp = request["timestamp"]

        # Create the WHATSUP_INIT request
        req = Requests.wup_ini(last_message_timestamp)

        # Find a beacon or a node and send the WHATSUP request.
        if len(Config.beacons) > 0:
            node_list = ("beacon", Config.beacons)
        else:
            all_contacts = self.contacts.get_all_contacts_ids()
            if len(all_contacts) > 0:
                node_list = ("node", all_contacts)
            else:
                # Here, we know no nodes nor beacons.
                return

        excluded = []
        while True:
            random_id = get_node_list_id(node_list[1], excluded)
            excluded.append(random_id)
            request_target = node_list[1][random_id]

            if node_list[0] == "beacon":
                address, port = request_target.split(":")
                contact = Contact(address, port, Utils.get_timestamp())
            elif node_list[1] == "node":
                contact_info = self.contacts.get_contact_info(request_target)
                address, port = contact_info["address"].split(":")
                last_seen = contact_info["last_seen"]
                contact = Contact(address, port, last_seen)
            else:
                raise ValueError

            if self.send_request(req, contact):
                break

    # Message section

    @staticmethod
    def read_message(msg: str, node: str) -> None or Message:
        """
        Tries to read a message received by a peer, to only check if it is correct (not decrypting it here).

        :param str msg: A message, as a JSON string.
        :param str node: A node, as a JSON string.
        :return None|Message: None if the message is invalid, otherwise returns the message object.
        """
        if not Node.is_valid(Utils.decode_json(node)):
            return

        # Converts the JSON string to a dictionary.
        unpacked_msg = Utils.decode_json(msg)

        if Message.is_received_message_valid(unpacked_msg):
            message_object = Message.from_dict(unpacked_msg)
            message_object.set_time_received()
            message_object.set_id()
        else:
            return

        # At this point, the message is valid and we can relay it to other nodes without danger.
        return message_object

    def prepare_message_for_recipient(self, node: Node, message: OwnMessage):
        """
        Prepare a message by encrypting its values.
        This message is addresses to a specific node.
        """
        aes_key, nonce = self.master_node.conversations.get_decrypted_aes(node.get_id())
        aes = Encryption.construct_aes_object(aes_key, nonce)
        message.prepare(aes)

    # Network interactions section

    def listen(self) -> None:
        """
        Setup a server and listens on a port.
        """

        def receive_all(sock: socket.socket) -> bytes:
            """
            Receives all parts of a network-sent message.

            :param socket.socket sock: The socket object.
            :return bytes: The complete message.
            """
            data = bytes()
            while True:
                part = sock.recv(Config.network_buff_size)
                data += part
                if len(part) < Config.network_buff_size:
                    # Either 0 or end of data
                    break
            return data

        server_socket = socket.socket()
        server_socket.bind((self.host, self.port))
        server_socket.listen(Config.network_max_conn)

        while True:
            connection, address = server_socket.accept()
            raw_request = receive_all(connection)

    def broadcast_request(self, request: Request) -> None:
        """
        Broadcast a request to all known contacts.

        :param Request request:
        """
        known_contacts = {}

        for contact_id in self.master_node.contacts.list_peers():
            known_contacts.update({contact_id: self.master_node.contacts.get_contact_info(contact_id)})

        for contact_info in known_contacts:
            contact_object = Contact.from_dict(contact_info)
            self.send_request(request, contact_object)

    def send_request(self, request: Request, contact: Contact) -> None:
        """
        Send a request to a specific contact.

        :param Request request: The request to send.
        :param Contact contact: The contact to send the request to.
        """
        # Initiate network connection with the contact.
        # TODO : error handling
        address = contact.get_address()
        port = contact.get_port()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((address, port))  # Convert node.port to str ? !!! DEV !!!
        client_socket.send(request.to_json())
