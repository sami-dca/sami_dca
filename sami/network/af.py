"""
Address families.
"""

import socket

af_map = {
    "AF_INET": socket.AF_INET,
    # 'AF_INET6': socket.AF_INET6,
}

# Supported address families, sorted by priority
# (what we prefer to use on the network comes first).
supported_af = list(af_map.keys())
