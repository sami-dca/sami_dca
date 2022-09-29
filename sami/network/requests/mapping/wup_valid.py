"""
Maps statuses to requests objects.
It purposefully doesn't include WUP_INI and WUP_REP because a WUP_REP
should not contain a WUP_INI or WUP_REP.
Also, putting it all directly in a single dictionary tends to causes
circular imports issues.
"""
from collections import defaultdict

from ..BCP import BCP
from ..CSP import CSP
from ..D_P import DCP, DNP
from ..KEP import KEP
from ..MPP import MPP
from ..NPP import NPP

status_mapping_wup_valid = defaultdict(
    lambda: None,
    {
        "BCP": BCP,
        "CSP": CSP,
        "DCP": DCP,
        "DNP": DNP,
        "KEP": KEP,
        "MPP": MPP,
        "NPP": NPP,
    },
)
