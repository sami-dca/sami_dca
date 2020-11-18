# -*- coding: UTF8 -*-

from dataclasses import dataclass

from .utils import Utils
from .encryption import Encryption
from .structures import Structures


def set_timestamp_on_call(func):
    def wrapper(*args):
        self = args[0]
        self.set_timestamp()
        return func(*args)
    return wrapper


@dataclass
class Request:
    status: str
    data: dict
    timestamp: int = None
    nonce: int = None

    @staticmethod
    def is_request_valid(req_data: dict) -> bool:
        """
        Takes a request information (as a dictionary) and checks whether it is valid.

        :param req_data:
        :return bool: True if the request is valid, False otherwise.
        """
        if not Utils._validate_fields(req_data, Structures.request_standard_structure):
            return False
        return True

    @classmethod
    def from_dict(cls, req_data: dict):
        """
        Returns a new object instance from the passed data.

        :param dict req_data: A valid request as a dictionary.
        :return: A Request object.
        """
        status = req_data["status"]
        data = req_data["data"]
        timestamp = req_data["status"]
        return cls(status, data, timestamp)

    @classmethod
    def from_json(cls, json_data: str):
        """
        Returns a new object instance from the passed data.

        !!! DEPRECATED !!!

        :param str json_data:
        :return: A Request object.
        """
        req_data = Utils.decode_json(json_data)
        return cls.from_dict(req_data)

    @set_timestamp_on_call
    def set_nonce(self, nonce):
        """
        Sets the request's nonce.
        This function should only be called by the Proof-of-Work algorithm.
        """
        self.nonce = nonce

    @set_timestamp_on_call
    def set_timestamp(self):
        """
        Sets instance attribute "timestamp".
        """
        self.timestamp = Utils.get_timestamp()

    @set_timestamp_on_call
    def to_dict(self) -> dict:
        """
        Returns the Request as a dictionary.
        """
        pass

    @set_timestamp_on_call
    def to_json(self) -> str:
        """
        Returns the Request as a json-encoded string.
        """
        return Utils.encode_json(self.to_dict())

    @set_timestamp_on_call
    def get_id(self) -> str:
        """
        This method derives an ID from this request.

        :return str: An hexadecimal identifier.
        """
        h = Encryption.hash_iterable(self.to_json())
        return h.hexdigest()
