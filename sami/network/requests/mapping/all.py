from .wup_valid import status_mapping_wup_valid

from ..WUP import WUP_INI
from ..WUP import WUP_REP

status_mapping = status_mapping_wup_valid.copy()
status_mapping.update({
    'WUP_INI': WUP_INI,
    'WUP_REP': WUP_REP,
})
