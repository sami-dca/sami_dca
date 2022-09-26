from typing import List
from json.decoder import JSONDecodeError

from ..nodes import Node
from ..contacts import Contact
from ._network import Networks
from ..design import Singleton
from ..utils import decode_json
from ..nodes.own import MasterNode
from .requests.mapping.all import status_mapping
from ..cryptography.serialization import decode_bytes
from ..messages import EncryptedMessage, Conversation
from ..cryptography.symmetric import SymmetricKey, KeyPart
from ..database.common import RawRequestsDatabase,  ContactsDatabase
from ..database.private import KeyPartsDatabase, MessagesDatabase, \
    NodesDatabase
from ..network.requests import Request, BCP, KEP, CSP, NPP, DNP, MPP, DCP, \
    WUP_REP, WUP_INI

import logging as _logging
logger = _logging.getLogger('network.handling')


class RequestsHandler(Singleton):

    """
    Handles the requests we receive.

    This is here the actual processing of the requests takes place.
    """

    def __init__(self):
        # This variable can be modified before and after handling
        # requests (for instance in WUP_REP) to avoid broadcasting some
        # requests.
        # FIXME: dirty!
        self._broadcast: bool = True

    def broadcast(self, request: Request) -> None:
        if self._broadcast:
            Networks().map(lambda net: net.broadcast(request))

    def __call__(self, raw_request: bytes, from_address: str) -> None:
        """
        Takes the raw requests as bytes, and manipulates it to finally route it
        """
        json_request = decode_bytes(raw_request)
        try:
            dict_request = decode_json(json_request)
        except JSONDecodeError:
            return

        status: str = dict_request['status']

        # Cast the dictionary to an appropriate dataclass.
        # This verifies the structure, but not the info inside.
        req_type = status_mapping[status]
        if req_type is None:
            # Couldn't find an appropriate structure
            return

        request_data = req_type.request_struct(**dict_request)
        if request_data is None:
            # The request is malformed
            return

        request = req_type.from_data(request_data)
        self.route(request)

    def route(self, request: Request) -> None:
        """
        This method is used to route the requests to their corresponding
        functions, in order to process them.
        """

        if request.is_known():
            return
        else:
            request.store()

        # Programmatically get the handler function, and call with the request
        self.__getattribute__(request.status.lower())(request=request)

    def wup_ini(self, request: WUP_INI) -> None:
        """
        Called when we receive a What's Up init request.
        """
        req_timestamp = int(request.data["timestamp"])

        contact = Contact.from_data(request.data["author"])
        if contact is None:
            return
        contact.store()

        nic = Networks().get_corresponding_network(contact)
        if nic is None:
            return

        all_req_since = RawRequestsDatabase().get_all_since(req_timestamp)
        for request in all_req_since:
            req = WUP_REP.new(request)
            nic.parent.send_queue.put((nic, req, contact))

    def wup_rep(self, request: WUP_REP) -> None:
        """
        Called when receiving a What's Up reply request.
        """
        inner_request = Request.from_data(request.data)

        if inner_request is None:
            return

        # Route the request without broadcasting it.
        self._broadcast = False
        self.route(inner_request)
        self._broadcast = True

    def bcp(self, request: BCP) -> None:
        contact = Contact.from_data(request.data['author'])
        if contact is None:
            # Contact information invalid
            return
        ContactsDatabase().store(contact.to_dbo())

    def dnp(self, request: DNP) -> None:
        """
        Handles Discover Nodes requests.
        The request must be valid.
        """
        contact = Contact.from_data(request.data["author"])
        if not contact:
            return
        ContactsDatabase().store(contact.to_dbo())

        nic = Networks().get_corresponding_network(contact)
        if nic is None:
            return

        req = NPP.new(NodesDatabase().get_all_nodes())
        nic.parent.send_queue.put((nic, req, contact))

    def dcp(self, request: DCP) -> None:
        """
        Handles Discover Contacts requests.
        The request must be valid.
        """
        contact = Contact.from_data(request.data["author"])
        if not contact:
            return
        ContactsDatabase().store(contact.to_dbo())

        nic = Networks().get_corresponding_network(contact)
        if nic is None:
            return

        for contact_object in ContactsDatabase().get_all():
            req = CSP.new(contact_object)
            nic.parent.send_queue.put((nic, req, contact))

    def mpp(self, request: MPP) -> None:
        """
        This method is used when receiving a new message.
        It is called after the request has been broadcast back and stored
        in the raw_requests database, and will take care of storing
        the message if we can decrypt its content.
        """
        author = Node.from_data(request.data.author)
        if author is None:
            # Invalid node
            return

        message_enc = EncryptedMessage.from_data(request.data)
        if message_enc is None:
            # Invalid message
            return

        # We'll now try to decrypt it
        message_dec = message_enc.to_clear()
        if message_dec is None:
            # Couldn't decrypt
            return

        # We store the encrypted message
        MessagesDatabase().store(message_enc.to_dbo())

    def npp(self, request: NPP) -> None:
        node = Node.from_data(request.data)
        if node is None:
            # Node information is invalid
            return
        if NodesDatabase().is_known(node.id):
            # We already know this node, and therefore already
            # had negotiated a key.
            return

        NodesDatabase().store(node.to_dbo())
        master_node = MasterNode()
        own_node = Node(
            master_node.public_key,
            master_node.sig,
        )
        conv = Conversation(members=[node, own_node])
        new_key_part = KeyPart.new(conv)
        KeyPartsDatabase().store(new_key_part.to_dbo())
        kep = KEP.new(
            key_part=new_key_part,
            to=node,
            conversation=conv,
        )
        self.broadcast(kep)

    def kep(self, request: KEP) -> None:
        sender_key_part = KeyPart.from_data(request.data)
        if sender_key_part is None:
            # The request is not meant for us
            return

        author = Node.from_data(request.data.author)
        if author is None:
            # The author node information is invalid
            return
        conv_members: List[Node] = []
        for member_info in request.data.members:
            member = Node.from_data(member_info)
            if member is None:
                # At least one of the nodes from the members list is invalid
                return
            else:
                conv_members.append(member)
        conv_members.append(author)

        # Discover the nodes
        self._broadcast = False
        self.npp(NPP.new(conv_members))
        self._broadcast = True

        if sender_key_part.is_known():
            # Somehow, we already know this key part.
            # It should have been filtered out as the request should have been
            # the same.
            # Perhaps it's an id collision
            return
        sender_key_part.store()

        conv = Conversation(members=conv_members)
        if not conv.is_known():
            conv.store()
            our_key_part = KeyPart.new(conv)
            our_key_part.store()
            for member in conv_members:
                self.broadcast(KEP.new(
                    key_part=our_key_part,
                    to=member,
                    conversation=conv
                ))

        key_parts = KeyPartsDatabase().get_parts(conv.id)
        key = SymmetricKey.from_parts(key_parts)
        if key is None:
            # We don't have all the parts yet
            return
        key.store()

    def csp(self, request: CSP) -> None:
        contact = Contact.from_data(request.data)
        if contact is None:
            # Contact information is invalid
            return
        ContactsDatabase().store(contact.to_dbo())

    def invalid_request(self, request: Request) -> None:
        logger.warning(f'Captured request calling unknown protocol: '
                       f'{request.status!r}.')
