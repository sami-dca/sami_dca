from typing import List
from typing import Union as _Union

from pydantic import BaseModel


class Structure(BaseModel):
    def to_dict(self, *args, **kwargs):
        return self.dict(*args, **kwargs)

    def to_json(self, *args, **kwargs):
        return self.json(*args, **kwargs)


class NodeStructure(Structure):
    rsa_n: int
    rsa_e: int
    hash: str
    sig: str


class ContactStructure(Structure):
    address: str
    port: int


class SymmetricKeyStructure(Structure):
    value: str
    hash: str
    sig: str


class MessageStructure(Structure):
    content: str
    time_sent: int
    digest: str
    author: NodeStructure
    conversation: str


class RequestStructure(Structure):
    status: str
    data: dict
    timestamp: int


# Define protocols' `data`

class BCPStructure(Structure):
    author: ContactStructure


class CSPStructure(Structure):
    contacts: List[ContactStructure]


class DCPStructure(Structure):
    author: ContactStructure


class DNPStructure(Structure):
    author: ContactStructure


class KEPStructure(Structure):
    key_part: str
    hash: str
    sig: str
    author: NodeStructure
    members: List[NodeStructure]  # List of NodeStructure


class MPPStructure(Structure):
    message: MessageStructure
    conversation: str


class NPPStructure(Structure):
    nodes: List[NodeStructure]


class WUP_INIStructure(Structure):
    beginning: int
    end: int
    author: ContactStructure


class WUP_REPStructure(Structure):
    requests: List[RequestStructure]


AnyProtocolStructure = _Union[
    BCPStructure,
    CSPStructure,
    DCPStructure,
    DNPStructure,
    KEPStructure,
    MPPStructure,
    NPPStructure,
    WUP_INIStructure,
    WUP_REPStructure,
]


# Define specific request structures

class BCPRequestStructure(RequestStructure):
    data: BCPStructure


class CSPRequestStructure(RequestStructure):
    data: CSPStructure


class DCPRequestStructure(RequestStructure):
    data: DCPStructure


class DNPRequestStructure(RequestStructure):
    data: DNPStructure


class KEPRequestStructure(RequestStructure):
    data: KEPStructure


class MPPRequestStructure(RequestStructure):
    data: MPPStructure


class NPPRequestStructure(RequestStructure):
    data: NPPStructure


class WUP_INIRequestStructure(RequestStructure):
    data: WUP_INIStructure


class WUP_REPRequestStructure(RequestStructure):
    data: WUP_REPStructure


AnyRequestStructure = _Union[
    BCPRequestStructure,
    CSPRequestStructure,
    DCPRequestStructure,
    DNPRequestStructure,
    KEPRequestStructure,
    MPPRequestStructure,
    NPPRequestStructure,
    WUP_INIRequestStructure,
    WUP_REPRequestStructure,
]
