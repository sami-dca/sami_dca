# -*- coding: UTF8 -*-

from .node import Node
from .message import Message
from .node import MasterNode
from .request import Request
from .encryption import Encryption
from .structures import Structures
from .utils import validate_fields
from .contact import Contact, OwnContact
from .validation import is_valid_node, is_valid_contact


class Requests:

    # KEP section

    @staticmethod
    def kep(half_aes_key: bytes, master_node: MasterNode, node: Node) -> Request:
        """
        Creates a new Key Exchange request.

        :param bytes half_aes_key:
        :param MasterNode master_node:
        :param Node node:
        :return Request: A KEP Request.
        """
        en_half_aes_key: str = Encryption.encrypt_asymmetric(node.get_rsa_public_key(), half_aes_key)
        master_node_info: dict = master_node.to_dict()
        node_info: dict = node.to_dict()
        h_object = Encryption.hash_iterable(en_half_aes_key)
        h: str = h_object.hexdigest()
        sig: str = Encryption.serialize_bytes(Encryption.get_rsa_signature(master_node.get_rsa_private_key(), h_object))

        data = {
            "key": {
                "value": en_half_aes_key,
                "hash": h,
                "sig": sig
            },
            "author": master_node_info,
            "recipient": node_info
        }

        return Request(Requests.kep.__name__.upper(), data)

    @staticmethod
    def is_valid_kep_request(request: Request) -> bool:
        """
        Checks whether the KEP request passed is valid.

        :param Request request: A KEP request.
        :return bool: True if the request is valid, False otherwise.
        """
        if not validate_fields(request.to_dict(), Structures.kep_request_structure):
            return False

        # Verify nodes values are valid.
        if not is_valid_node(request.data["author"]):
            return False
        if not is_valid_node(request.data["recipient"]):
            return False

        author_values = request.data["author"]
        # The cast cannot raise errors as we validated the fields beforehand.
        rsa_n = int(author_values["rsa_n"])
        rsa_e = int(author_values["rsa_e"])

        rsa_public_key = Encryption.construct_rsa_object(rsa_n, rsa_e)

        data = request.data["key"]["value"]
        original_hash = request.data["key"]["hash"]
        original_sig = request.data["key"]["sig"]

        if not Encryption.are_hash_and_sig_valid(data, rsa_public_key, original_hash, original_sig):
            return False

        return True

    # WUP section

    @staticmethod
    def wup_ini(last_timestamp: int) -> Request:
        """
        Creates a new What's Up Init request, used to request all messages since passed timestamp.

        :param int last_timestamp:
        :return Request: A WUP_INI Request.
        """
        own_contact = OwnContact()  # TODO: needs type import
        data = {
            "timestamp": last_timestamp,
            "author": own_contact.to_dict()
        }
        return Request(Requests.wup_ini.__name__.upper(), data)

    @staticmethod
    def wup_rep(request: Request) -> Request:
        """
        Creates a new What's Up Reply request, used to reply to a What's Up Init request.

        :param Request request:
        :return Request: A WUP_REP Request.
        """
        data = request.to_dict()
        return Request(Requests.wup_rep.__name__.upper(), data)

    @staticmethod
    def is_valid_wup_ini_request(request: Request) -> bool:
        """
        Checks whether a WUP_INI request is valid.

        :param Request request: A WUP_INI request.
        :return bool: True if the request is valid, False otherwise.
        """
        if not validate_fields(request.to_dict(), Structures.wup_ini_request_structure):
            return False
        if not is_valid_node(request.data["author"]):
            return False
        return True

    @staticmethod
    def is_valid_wup_rep_request(request: Request) -> bool:
        """
        Checks whether a WUP_REP request is valid.

        :param Request request: A WUP_REP request.
        :return bool: True if the request is valid, False otherwise.
        """
        if not validate_fields(request.to_dict(), Structures.wup_rep_request_structure):
            return False
        return True

    # MPP section

    @staticmethod
    def mpp(message: Message) -> Request:
        data = message.to_dict()
        return Request(Requests.npp.__name__.upper(), data)

    # NPP section

    @staticmethod
    def npp(node: Node) -> Request:
        """
        Creates a new Node Publication request.

        :param Node node: The node to publish.
        :return Request: A NPP Request.
        """
        data = node.to_dict()
        return Request(Requests.npp.__name__.upper(), data)

    @staticmethod
    def is_valid_npp_request(request: Request) -> bool:
        """
        Checks whether a NPP request is valid

        :param Request request: A NPP request.
        :return bool: True if the request is valid, False otherwise.
        """
        if not is_valid_node(request.data):
            return False
        return True

    # CSP section

    @staticmethod
    def csp(contact: Contact) -> Request:
        """
        Creates a new Contact Sharing request.

        :param Contact contact:
        :return Request: A CSP Request.
        """
        data = contact.to_dict()
        return Request(Requests.csp.__name__.upper(), data)

    @staticmethod
    def is_valid_csp_request(request: Request) -> bool:
        """
        Checks whether a CSP request is valid.

        :param Request request: A CSP request.
        :return bool: True if the request is valid, False otherwise.
        """
        if not is_valid_contact(request.data):
            return False
        return True

    # Discover section

    @staticmethod
    def dnp(contact: Contact) -> Request:
        """
        Creates a new Discover Pub request.

        :param Contact contact:
        :return Request: A DPP Request.
        """
        data = {}
        return Request(Requests.dnp.__name__.upper(), data)

    @staticmethod
    def dcp(contact: Contact) -> Request:
        """
        Creates a new Discover Contact request.

        :param Contact contact:
        :return Request: A DCP Request.
        """
        data = {}
        return Request(Requests.dcp.__name__.upper(), data)

    @staticmethod
    def is_valid_dp_request(request: Request) -> bool:
        if not validate_fields(request.to_dict(), Structures.dp_request_structure):
            return False

        if not is_valid_contact(request.data):
            return False

        return True
