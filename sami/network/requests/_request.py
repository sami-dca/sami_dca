from __future__ import annotations

import pickle
from functools import cached_property
from typing import Any, Generic, TypeVar

import pydantic

from ...config import Identifier, settings
from ...cryptography.hashing import hash_object
from ...database import Database
from ...objects import StoredSamiObject
from ...utils import get_id, get_time
from ._base import RequestData
from .BCP import BCP
from .CEP import CEP_INI, CEP_REP
from .CSP import CSP
from .D_P import DCP, DNP
from .KEP import KEP
from .MPP import MPP
from .NPP import NPP
from .WUP import WUP_INI


class WUP_REP(RequestData, pydantic.BaseModel):
    """
    WUP_REP is a special case, thus why it's located here.

    This is because it can contain a Request,
    and a Request can contain a WUP_REP.
    """

    requests: set[Request]

    _full_name = "What's Up Reply"
    _to_store = False
    _waiting_for_answer = False


all_data_types = (
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
)
_data_type_names = tuple(t.__name__ for t in all_data_types)
_data_name_to_type = {t.__name__: t for t in all_data_types}

_R = TypeVar("_R", *all_data_types)  # noqa
_S = TypeVar("_S", *_data_type_names)  # noqa


class Request(pydantic.BaseModel, StoredSamiObject, Generic[_R]):
    __table_name__ = "requests"
    __node_specific__ = False

    status: _S
    data: _R
    timestamp: pydantic.conint(gt=settings.sami_start)

    class Config:
        allow_mutation = False
        smart_union = True

    @classmethod
    @pydantic.validator("data")
    def _assert_data_matches_status(cls, data: _R, values: dict[str, Any]) -> _R:
        status = values["status"]
        schema = _data_name_to_type[status]
        assert (  # noqa
            isinstance(data, schema),  # noqa
            (
                f"Status {status!r} assumes {schema.__name__!r} schema,"
                f"got {data.__class__.__name__!r}."
            ),
        )  # noqa
        return data

    @classmethod
    def new(cls, data: _R) -> Request[_R]:
        return cls(
            status=data.__class__.__name__,
            data=data,
            timestamp=get_time(),
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> Request:
        return cls.parse_raw(
            data,
            content_type="application/pickle",
            allow_pickle=True,
        )

    @classmethod
    def last_received(cls):
        with Database() as db:
            db.get_last(cls, key=lambda req: req.timestamp)

    @cached_property
    def id(self) -> Identifier:
        # Note: do not include the timestamp in the hash
        return get_id(hash_object([self.status, self.data]))

    def to_bytes(self) -> bytes:
        return pickle.dumps(self)
