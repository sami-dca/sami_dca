from ...design import Singleton, apply_init_callback_to_singleton
from ._database import Database as _Database
from ._database import set_engine
from .models import CommonBase


@apply_init_callback_to_singleton(set_engine)
class CommonDatabase(_Database, Singleton):
    """
    Database for tables that are not node-encrypted, which are therefore
    shared among the different identities stored on a same machine.
    """

    name = "common"
    base = CommonBase
