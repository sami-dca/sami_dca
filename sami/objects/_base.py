from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property

import pydantic
from loguru import logger

from ..config import Identifier
from ..database import Database

_T = type["_T"]


class SamiObject(pydantic.BaseModel, ABC):
    class Config:
        validate_assignment = True

    @cached_property
    @abstractmethod
    def id(self) -> Identifier:
        """
        Generates an ID for this object.
        """
        pass


class StoredSamiObject(SamiObject, ABC):
    """
    Same thing as a ``SamiObject``, except we actually store this type of object
    in the database.
    """

    __table_name__: str
    __node_specific__: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def all(cls) -> set[_T]:
        """
        Queries the database and returns all the conversations.
        """
        with Database() as db:
            dbos = db.get_all(cls)

            objects = set()
            for dbo in dbos:
                try:
                    objects.update(cls(**dbo))
                except pydantic.ValidationError:
                    logger.error(
                        f"Found invalid information in the database: {dbo!r}. "
                        "Removed it. "
                    )
                    db.remove(dbo.doc_id)
        return objects

    @classmethod
    def from_id(cls, identifier: Identifier) -> _T | None:
        with Database() as db:
            info = db.get_by_id(cls, identifier)
            if info is None:
                # Document with specified ID does not exist.
                return
            try:
                return cls(**info)
            except pydantic.ValidationError:
                # If loading the information in the database returned an error,
                # that probably means it was altered, so we'll just remove it.
                db.remove(identifier)

    def upsert(self) -> None:
        with Database() as db:
            db.upsert(self)

    def is_known(self) -> bool:
        with Database() as db:
            return db.is_known(self)
