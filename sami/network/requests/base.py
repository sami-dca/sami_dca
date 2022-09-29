from __future__ import annotations

import typing
from abc import ABC, abstractmethod
from typing import Optional

from ...cryptography.hashing import hash_object
from ...cryptography.serialization import encode_string
from ...database.base.models import RequestDBO
from ...database.common import RawRequestsDatabase
from ...structures import AnyProtocolStructure, AnyRequestStructure
from ...utils import decode_json, get_id, get_time


class Request(ABC):

    """
    Base Request abstract class.

    See `./README.md` for information on how to implement this class.
    """

    # Full protocol name
    full_name: str = None
    # Whether we should store this type of request
    to_store: bool = None
    # Type of structure of the `data` field
    inner_struct: typing.Type = AnyProtocolStructure
    # Type of structure of the request
    request_struct: typing.Type = AnyRequestStructure

    def __init__(self, data: inner_struct, timestamp: int = get_time()):
        self.status = self.__class__.__name__.upper()
        self.data = data
        self.timestamp = timestamp

        self.nonce: int = 0
        self.id = self._compute_id()

    @staticmethod
    def validate_status(status: str) -> Optional[str]:
        # TODO: Verify status is known
        return status

    @staticmethod
    @abstractmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        """
        Our goal in this static method is to take some structurally valid
        data, and verify to the best extent the validity of the information.
        Consider this a man-in-the-middle validation ; we would like to avoid
        transmitting invalid requests, but we cannot verify identifying data
        such as encrypted values, because the request isn't necessarily
        meant for us.
        """
        raise NotImplementedError

    @staticmethod
    def validate_timestamp(timestamp: int) -> Optional[int]:
        if timestamp > get_time():
            # Request is from the future
            return

        return timestamp

    @classmethod
    @abstractmethod
    def new(cls, *args, **kwargs) -> Request:
        """
        Takes some arbitrary values and creates a brand new request.
        """
        # Implement in subclass
        raise NotImplementedError

    @classmethod
    def from_data(cls, req_data: AnyRequestStructure) -> Optional[Request]:
        """
        Takes a structure, validates the content and create a Request
        object if valid.
        """
        status = cls.validate_status(req_data.status)
        data = cls.validate_data(req_data.data)
        timestamp = cls.validate_timestamp(req_data.timestamp)

        if (status is None) or (data is None) or (timestamp is None):
            return
        else:
            return cls(data, timestamp)

    @classmethod
    def from_dbo(cls, dbo: RequestDBO) -> Request:
        return cls.from_data(
            cls.request_struct(
                status=dbo.protocol,
                data=cls.inner_struct(decode_json(dbo.data)),
                timestamp=dbo.timestamp,
            )
        )

    def is_known(self) -> bool:
        raw_request_database = RawRequestsDatabase()
        return raw_request_database.is_known(self.id)

    def store(self) -> None:
        if self.to_store:
            raw_request_database = RawRequestsDatabase()
            raw_request_database.store(self.to_dbo())

    def _compute_id(self) -> str:
        # Note: do not include the timestamp in the hash
        return get_id(
            hash_object(
                [
                    self.status,
                    self.data.to_json(),
                ]
            )
        )

    def to_data(self) -> AnyRequestStructure:
        return self.request_struct(
            status=self.status,
            data=self.data,
            timestamp=self.timestamp,
        )

    def to_json(self) -> str:
        return self.to_data().to_json()

    def to_bytes(self) -> bytes:
        """
        Returns the Request as a bytes json-encoded string, ready for network
        communication.
        """
        return encode_string(self.to_json())

    def to_dbo(self) -> RequestDBO:
        return RequestDBO(
            protocol=self.status, data=self.data.to_json(), timestamp=self.timestamp
        )
