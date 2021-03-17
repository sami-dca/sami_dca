# -*- coding: UTF8 -*-

import logging

from .node import Node
from .config import Config
from .message import Message
from .node import MasterNode
from .request import Request
from .encryption import Encryption
from .structures import Structures
from .contact import Contact, OwnContact
from .validation import is_valid_node, is_valid_contact, validate_fields


class Requests:

    # KEP section

    @staticmethod
    def kep(half_aes_key: bytes, master_node: MasterNode, node: Node) -> Request:
        """
        Creates a new Key Exchange request.

        :param bytes half_aes_key: Our half of the AES key.
        :param MasterNode master_node: Our node.
        :param Node node: The recipient.
        :return Request: A KEP Request.
        """
        se_en_half_aes_key: str = Encryption.encrypt_asymmetric(node.get_rsa_public_key(), half_aes_key)
        master_node_info: dict = master_node.to_dict()
        node_info: dict = node.to_dict()
        h_object = Encryption.hash_iterable(se_en_half_aes_key)
        h: str = h_object.hexdigest()
        sig: str = Encryption.serialize_bytes(Encryption.get_rsa_signature(master_node.get_rsa_private_key(), h_object))

        data = {
            "key": {
                "value": se_en_half_aes_key,
                "hash": h,
                "sig": sig
            },
            "author": master_node_info,
            "recipient": node_info
        }

        return Request(Requests.kep.__name__.upper(), data)

    @staticmethod
    def is_valid_kep_request(request: Request) -> bool:
        if not validate_fields(request.to_dict(), Structures.kep_request_structure):
            return False

        # Verify nodes values are valid.
        if not is_valid_node(request.data["author"]):
            msg = (f'Request {request.status!r} {request.get_id()!r}: '
                   f'"author" field is invalid')
            if Config.verbose:
                msg = f"{msg} Got {request.data['author']}"
            logging.warning(msg)
            return False
        if not is_valid_node(request.data['recipient']):
            msg = (f'Request {request.status!r} {request.get_id()!r}: '
                   f'"recipient" field is invalid')
            if Config.verbose:
                msg += f"{msg} Got {(request.data['recipient'])}"
            logging.warning(msg)
            return False

        author = Node.from_dict(request.data['author'])

        data = request.data["key"]["value"]
        original_hash = request.data["key"]["hash"]
        original_sig = request.data["key"]["sig"]

        if not Encryption.are_hash_and_sig_valid(data, author.get_rsa_public_key(), original_hash, original_sig):
            msg = f'Request {request.status!r} {request.get_id()}: hash and sig are invalid'
            if Config.verbose:
                msg += f": passed hash / sig: {original_hash!r} / {original_sig!r}"
            logging.debug(msg)
            return False

        return True

    # WUP section

    @staticmethod
    def wup_ini(last_timestamp: int, contact: Contact) -> Request:
        own_contact = OwnContact(contact.get_address())
        data = {
            "timestamp": last_timestamp,
            "author": own_contact.to_dict()
        }
        return Request(Requests.wup_ini.__name__.upper(), data)

    @staticmethod
    def wup_rep(request: Request) -> Request:
        data = request.to_dict()
        return Request(Requests.wup_rep.__name__.upper(), data)

    @staticmethod
    def is_valid_wup_ini_request(request: Request) -> bool:
        if not validate_fields(request.to_dict(), Structures.wup_ini_request_structure):
            return False
        if not is_valid_node(request.data["author"]):
            return False
        return True

    @staticmethod
    def is_valid_wup_rep_request(request: Request) -> bool:
        if not validate_fields(request.to_dict(), Structures.wup_rep_request_structure):
            return False
        return True

    # MPP section

    @staticmethod
    def mpp(message: Message) -> Request:
        data = message.to_dict()
        return Request(Requests.npp.__name__.upper(), data)

    @staticmethod
    def is_valid_mpp_request() -> bool:
        pass  # TODO

    # BCP section

    @staticmethod
    def bcp(own_contact: OwnContact) -> Request:
        data = own_contact.to_dict()
        return Request(Requests.npp.__name__.upper(), data)

    @staticmethod
    def is_valid_bcp_request(request: Request) -> bool:
        if not is_valid_contact(request.data):
            return False
        return True

    # NPP section

    @staticmethod
    def npp(node: Node) -> Request:
        data = node.to_dict()
        return Request(Requests.npp.__name__.upper(), data)

    @staticmethod
    def is_valid_npp_request(request: Request) -> bool:
        if not is_valid_node(request.data):
            return False
        return True

    # CSP section

    @staticmethod
    def csp(contact: Contact) -> Request:
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
        data = {"author": contact.to_dict()}
        return Request(Requests.dnp.__name__.upper(), data)

    @staticmethod
    def dcp(contact: Contact) -> Request:
        data = {"author": contact.to_dict()}
        return Request(Requests.dcp.__name__.upper(), data)

    @staticmethod
    def is_valid_dp_request(request: Request) -> bool:
        if not validate_fields(request.to_dict(), Structures.dp_request_structure):
            return False

        if not is_valid_contact(request.data["author"]):
            return False

        return True
