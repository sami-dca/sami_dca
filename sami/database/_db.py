from __future__ import annotations

from typing import Callable, TypeVar

from tinydb import TinyDB
from tinydb.table import Document

from ..config import Identifier
from ..design import Singleton
from ..objects.nodes import MasterNode
from ..utils import SupportsComparison

_T = TypeVar("_T")


def _get_table_name(obj) -> str:
    if obj.__node_specific__:
        return f"{obj.__table_name__}_{MasterNode().id}"
    else:
        return obj.__table_name__


class Database(Singleton):

    """
    Simple, generic interface to access a TinyDB file.
    Database logic is implemented in the Sami objects.
    """

    _db: TinyDB

    def __enter__(self) -> Database:
        return self

    def __exit__(self) -> None:
        pass

    def init(self):
        self._db = TinyDB()  # FIXME

    def get_by_id(self, obj: _T, identifier: Identifier) -> Document:
        return self._db.table(_get_table_name(obj)).get(doc_id=identifier)

    def get_all(self, obj: _T) -> list[Document]:
        return self._db.table(_get_table_name(obj)).all()

    def is_known(self, obj: _T) -> bool:
        return self._db.table(_get_table_name(obj)).contains(doc_id=obj.id)

    def get_last(
        self, obj: _T, key: Callable[[_T], SupportsComparison]
    ) -> Document | None:
        results = sorted(self._db.table(_get_table_name(obj)).all(), key=key)
        if results:
            return results[0]

    def upsert(self, obj: _T) -> None:
        """
        Takes any object from Sami and inserts/updates the information
        in the database.
        """
        table = self._db.table(_get_table_name(obj))
        table.upsert(Document(obj.dict(), doc_id=obj.id))

    def remove(self, identifier: int) -> None:
        # FIXME: table-wise
        self._db.remove(doc_ids=[identifier])
