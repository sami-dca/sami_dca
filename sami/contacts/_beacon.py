from __future__ import annotations

from ._base import Contact
from ..utils import get_time
from ..utils.network import get_address_object


class Beacon(Contact):
    pass


beacons = (
    # FIXME
    # Beacon(address=get_address_object(''), port=0, last_seen=get_time()),
)
