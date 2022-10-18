from typing import List as _List
from typing import Union as _Union

from pydantic import BaseModel as _BaseModel
from pydantic import conint as _conint
from pydantic import conlist as _conlist
from pydantic import constr as _constr

from ..config import settings


class Structure(_BaseModel):
    def to_dict(self, *args, **kwargs):
        return self.dict(*args, **kwargs)

    def to_json(self, *args, **kwargs):
        return self.json(*args, **kwargs)


class NodeImageStructure(Structure):
    seed: _conint(ge=0, le=9999, strict=True)
    colors: _conlist(
        item_type=_constr(to_lower=True, regex=r"[a-f0-9]{6}", strict=True),  # noqa
        min_items=3,
        max_items=9,
        unique_items=True,
    )
    shapes_count: _conint(ge=1, le=19, strict=True)


class NodeStructure(Structure):
    rsa_n: int
    rsa_e: int
    hash: str
    sig: str


class ContactStructure(Structure):
    address: str
    port: _conint(ge=1, le=65535, strict=True)


class SymmetricKeyStructure(Structure):
    value: str
    hash: str
    sig: str


class MessageStructure(Structure):
    content: str
    time_sent: _conint(gt=settings.sami_start)
    digest: str
    author: NodeStructure
    conversation: str


class RequestStructure(Structure):
    status: str
    data: dict
    timestamp: _conint(gt=settings.sami_start)


# Define protocols' `data`


class BCPStructure(Structure):
    author: ContactStructure


class CSPStructure(Structure):
    contacts: _List[ContactStructure]


class DCPStructure(Structure):
    author: ContactStructure


class DNPStructure(Structure):
    author: ContactStructure


class KEPStructure(Structure):
    key_part: str
    hash: str
    sig: str
    author: NodeStructure
    members: _List[NodeStructure]


class MPPStructure(Structure):
    message: MessageStructure
    conversation: str


class NPPStructure(Structure):
    nodes: _List[NodeStructure]


class WUP_INIStructure(Structure):
    beginning: int
    end: int
    author: ContactStructure


class WUP_REPStructure(Structure):
    requests: _List[RequestStructure]


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
