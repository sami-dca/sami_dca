import pydantic
from loguru import logger

from ...network import Network, Networks
from ...network.requests import (
    BCP,
    CEP_INI,
    CEP_REP,
    CSP,
    DCP,
    DNP,
    KEP,
    MPP,
    NPP,
    WUP_INI,
    WUP_REP,
    Request,
)
from ...objects import Contact, Conversation, MasterNode, Node
from .._queue import handle_queue, send_queue


class ToBroadcast(pydantic.BaseModel):
    request: Request


class ToSend(pydantic.BaseModel):
    network: Network
    request: Request
    contact: Contact


class ToHandle(pydantic.BaseModel):
    request: Request


ToDo = ToBroadcast | ToSend | ToHandle
ToProcess = ToDo | list[ToDo] | None


class RequestsHandler:

    """
    Handles the requests we receive.

    This is here the actual processing of the requests takes place.
    """

    networks = Networks()

    def __call__(self, raw_request: bytes, from_address: str) -> None:
        try:
            request = Request.from_bytes(raw_request)
        except pydantic.ValidationError:
            return

        self.route(request, from_address)

    def route(self, request: Request, from_address: str) -> None:
        """
        This method is used to route the requests to their corresponding
        functions, in order to process them.
        """
        if request.is_known():
            return
        else:
            request.upsert()

        # Programmatically get the handler function, and call with the request
        result: ToProcess = self.__getattribute__(request.status.lower())(
            request=request,
            data=request.data,
        )

        for todo in result:
            if isinstance(todo, ToSend):
                send_queue.put((todo.network, todo.request, todo.contact))
            elif isinstance(todo, ToHandle):
                handle_queue.put((todo.request, from_address))
            elif isinstance(todo, ToBroadcast):
                for network in self.networks:
                    for contact in network.contacts():
                        send_queue.put((network, todo.request, contact))

    @staticmethod
    def wup_ini(data: WUP_INI, **_) -> ToProcess:
        contact = data.author
        contact.upsert()

        nic = Networks().get_corresponding_network(contact)
        if nic is None:
            return

        req = Request.new(
            WUP_REP(
                requests=Request.get_between(
                    data.beginning,
                    data.end,
                ),
            )
        )

        return ToSend(
            network=nic,
            request=req,
            contact=contact,
        )

    @staticmethod
    def wup_rep(data: WUP_REP, **_) -> ToProcess:
        return [ToHandle(request=request) for request in data.requests]

    @staticmethod
    def bcp(data: BCP, **_) -> ToProcess:
        data.author.upsert()
        return

    @staticmethod
    def dnp(data: DNP, networks: Networks, **_) -> ToProcess:
        contact = data.author
        contact.upsert()

        nic = networks.get_corresponding_network(contact)
        if nic is None:
            return

        req = Request.new(NPP(nodes=Node.all()))

        return ToSend(
            network=nic,
            request=req,
            contact=contact,
        )

    @staticmethod
    def dcp(data: DCP, **_) -> ToProcess:
        contact = data.author
        contact.upsert()

        nic = Networks().get_corresponding_network(contact)
        if nic is None:
            return

        req = Request.new(CSP(contacts=Contact.all()))

        return ToSend(
            network=nic,
            request=req,
            contact=contact,
        )

    @staticmethod
    def mpp(data: MPP, **_) -> ToProcess:
        conversation = Conversation.from_id(data.conversation_id)
        if conversation is None:
            # We don't know the conversation, so we'll just ignore it
            return
        conversation.messages.append(data.message)
        conversation.upsert()
        return

    @staticmethod
    def npp(data: NPP, **_) -> ToProcess:
        to_broadcast = []
        for node in data.nodes:
            if node.is_known():
                continue
            node.upsert()
            # Create a new conversation with just this node and ourselves
            conversation = Conversation(members={node, MasterNode()})
            conversation.upsert()
            to_broadcast.append(
                ToBroadcast(
                    request=Request.new(
                        KEP.new(
                            conversation=conversation,
                            recipient=node,
                        )
                    )
                )
            )
        return to_broadcast

    @staticmethod
    def kep(data: KEP, **_) -> ToProcess:
        # FIXME
        to_process = []

        # Discover the nodes
        to_process.append(
            ToHandle(
                request=Request.new(NPP(nodes=data.members)),
            )
        )

        conversation = Conversation.load_or_new(members=data.members)
        conversation.add_key_part(data.our_key_part.to_clear())
        conversation.upsert()

        for member in conversation.members:
            to_process.append(
                ToBroadcast(
                    request=Request.new(
                        KEP.new(
                            conversation=conversation,
                            recipient=member,
                        )
                    ),
                )
            )

        return to_process

    @staticmethod
    def csp(data: CSP, **_) -> ToProcess:
        for contact in data.contacts:
            contact.upsert()
        return

    @staticmethod
    def cep_ini(data: CEP_INI, networks: Networks, **_) -> ToProcess:
        for contact in data.contacts:
            contact.upsert()
        all_contacts = Contact.all()
        contacts_to_share = all_contacts.difference(data.contacts)
        net = networks.get_corresponding_network(data.author)
        return ToSend(
            network=net,
            contact=data.author,
            request=Request.new(
                CEP_REP(
                    contacts=contacts_to_share,
                    author=net.contact,
                )
            ),
        )

    @staticmethod
    def cep_rep(data: CEP_REP, **_) -> ToProcess:
        for contact in data.contacts:
            contact.upsert()
        return

    @staticmethod
    def invalid_request(request: Request, **_) -> ToProcess:
        logger.info(f"Found request with invalid status: {request.status!r}.")
        return
