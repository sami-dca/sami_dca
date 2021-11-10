from collections import defaultdict

from .BCP import BCP
from .CSP import CSP
from .D_P import DCP
from .D_P import DNP
from .KEP import KEP
from .MPP import MPP
from .NPP import NPP
from .WUP import WUP_INI
from .WUP import WUP_REP


# Maps a status to request
status_mapping = defaultdict(
    lambda: None,
    {
        'BCP': BCP,
        'CSP': CSP,
        'DCP': DCP,
        'DNP': DNP,
        'KEP': KEP,
        'MPP': MPP,
        'NPP': NPP,
        'WUP_INI': WUP_INI,
        'WUP_REP': WUP_REP,
    }
)
