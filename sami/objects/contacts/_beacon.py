from __future__ import annotations

from ...config import Setting, settings
from ...network.utils import get_address_object
from ._base import Contact


class Beacon(Contact):
    pass


settings.beacons = Setting(
    default_value={
        Beacon(
            address=get_address_object("projects.lilian.boulard.fr/sami"),
            port=2108,
        ),
    },
    description="The beacons we know.",
)
