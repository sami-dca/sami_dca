from .models import CommonBase
from ._database import set_engine, Database as _Database
from ...design import Singleton, apply_init_callback_to_singleton


@apply_init_callback_to_singleton(set_engine)
class CommonDatabase(_Database, Singleton):
    """
    Database for tables that are not node-encrypted, which are therefore
    shared among the different identities stored on a same machine.
    """
    name = 'common'
    base = CommonBase
