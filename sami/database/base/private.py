from ...design import Singleton, apply_init_callback_to_singleton
from ._database import Database as _Database
from ._database import set_engine
from .models import PrivateBase


@apply_init_callback_to_singleton(set_engine)
class PrivateDatabase(_Database, Singleton):
    """
    Database for tables that are node-encrypted, therefore unique to a single
    node.
    """

    name = "private"  # TODO: rename per-node
    base = PrivateBase
