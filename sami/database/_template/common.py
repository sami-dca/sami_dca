from typing import TYPE_CHECKING

from ..base.common import CommonDatabase
from ._base import _DatabaseTemplate

if TYPE_CHECKING:
    from ..base._database import Database as _Database


class CommonDatabaseTemplate(_DatabaseTemplate):
    def __init__(self):
        self.database: _Database = CommonDatabase()
