from ...design import Singleton
from ._database import Database as _Database
from .models import CommonBase


class CommonDatabase(_Database, Singleton):
    """
    Database for tables that are not node-encrypted, which are therefore
    shared among the different identities stored on a same machine.
    """

    name = "common"
    base = CommonBase
