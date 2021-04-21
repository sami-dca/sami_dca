# -*- coding: UTF8 -*-

from dataclasses import dataclass

from .config import Config
from .encryption import Encryption
from .utils import get_timestamp, encode_json
from .validation import is_valid_request, validate_export_structure


def set_timestamp_on_call(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        self.set_timestamp()
        return func(*args, **kwargs)
    return wrapper


@dataclass
class Request:
    status: str
    data: dict
    timestamp: int = None
    nonce: int = None

    @classmethod
    def from_dict(cls, req_data: dict):
        """
        Returns a new object instance from the passed data if it is valid.

        :param dict req_data: A valid request as a dictionary.
        :return Request|None: A Request object or None.
        """
        if not is_valid_request(req_data):
            return
        status = req_data["status"]
        data = req_data["data"]
        timestamp = req_data["timestamp"]
        return cls(status, data, timestamp)

    @set_timestamp_on_call
    def set_nonce(self, nonce) -> None:
        """
        Sets the request's nonce.
        This function should only be called by the Proof-of-Work algorithm.
        """
        self.nonce = nonce

    def set_timestamp(self) -> None:
        """
        Sets instance attribute "timestamp".
        """
        self.timestamp = get_timestamp()

    @validate_export_structure('request_standard_structure')
    @set_timestamp_on_call
    def to_dict(self) -> dict:
        """
        Returns the Request as a dictionary.
        """
        return {
            "status": self.status,
            "data": self.data,
            "timestamp": self.timestamp,
        }

    @set_timestamp_on_call
    def to_json(self) -> str:
        """
        Returns the Request as a json-encoded string.
        """
        return encode_json(self.to_dict())

    @set_timestamp_on_call
    def get_id(self) -> str:
        """
        This method derives an ID from this request.
        To avoid filling the database with duplicate requests,
        we will consider some special cases: for instance, a node information
        already received, but with a different timestamp, is considered useless.
        On a technical standpoint, it means that we will not consider the
        timestamp of the request for the ID generation.
        Note however that the timestamp will be stored in the database anyway.

        TODO: Update the already existing request with the new timestamp.

        :return str: An hexadecimal identifier.
        """
        s = self.to_dict()
        if self.status in Config.avoid_duplicates:  # Somewhat hackish
            s.pop('timestamp')
        h = Encryption.hash_iterable(encode_json(s))
        return h.hexdigest()[:Config.id_len]
