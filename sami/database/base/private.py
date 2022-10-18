from ...design import Singleton
from ._database import Database as _Database
from .models import PrivateBase


class PrivateDatabase(_Database, Singleton):
    """
    Database for tables that are node-encrypted, therefore unique to a single
    node.
    """

    name = "private"  # TODO: rename per-node
    base = PrivateBase
