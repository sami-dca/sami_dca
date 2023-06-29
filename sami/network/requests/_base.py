from abc import ABC
from typing import TypeVar

import pydantic

_T = TypeVar("_T")


class RequestData(pydantic.BaseModel, ABC):
    class Config:
        allow_mutation = False

    _full_name: str
    _to_store: bool
    _waiting_for_answer: bool
