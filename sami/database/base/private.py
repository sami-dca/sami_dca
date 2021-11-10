from .models import PrivateBase
from ._database import set_engine, Database as _Database
from ...design import Singleton, apply_init_callback_to_singleton


@apply_init_callback_to_singleton(set_engine)
class PrivateDatabase(_Database, Singleton):
    """
    Database for tables that are node-encrypted, therefore unique to a single
    node.
    """
    name = f'private'  # TODO
    base = PrivateBase
