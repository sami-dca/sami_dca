from typing import TYPE_CHECKING

from ..base.private import PrivateDatabase
from ._base import _DatabaseTemplate

if TYPE_CHECKING:
    from ..base._database import Database as _Database


class PrivateDatabaseTemplate(_DatabaseTemplate):
    def __init__(self):
        self.database: _Database = PrivateDatabase()
