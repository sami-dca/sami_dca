"""
Application's configuration.
"""

from datetime import datetime as _dt
from pathlib import Path as _Path
from typing import Type as _Type

from Crypto.Cipher import AES as _AES

from ._base import Setting
from ._base import Settings as _Settings

settings = _Settings()

settings.min_peers = Setting(
    default_value=0,
    description=(
        "Minimum number of contacts/nodes we should know before sending our identity"
    ),
    hint=(
        "The higher, the better, but it must be set in accordance "
        "with the network's size"
    ),
)
settings.max_request_lifespan = Setting(
    # Note: seconds * minutes * hours * days * months
    default_value=60 * 60 * 24 * 31 * 2,
    description="Lifespan of a request in seconds",
)
settings.sami_port = Setting(
    default_value=2108,
    description="Network port used by the app",
)
settings.broadcast_port = Setting(  # TODO: deprecate in favor of UPnP
    default_value=2109,
    description="Port used by the autodiscover",
)
settings.contact_connect_timeout = Setting(
    default_value=10,
    description="When connecting to a contact, timeout in seconds",
)
settings.broadcast_limit = Setting(
    default_value=15,
    description=(
        "Number of contacts we should know before stopping the autodiscover broadcast"
    ),
)
settings.databases_directory = Setting(
    default_value=_Path("./db/").absolute(),
    description="Local directory where the database files will be stored",
)
settings.logging_conf_file = Setting(
    default_value=_Path("./sami/logging.conf").absolute(),
    description="Logging configuration file path",
)
settings.log_file = Setting(
    default_value=_Path("./sami.log").absolute(),
    description="Log file path, in which logs will be output",
)
settings.default_port_range = Setting(
    default_value=range(1024, 65536),
    description="A range in which we will pick a random available port",
)

# Type (used for type hinting) of identifiers
Identifier: _Type = str

###############
# Danger zone #
###############

settings.private_key_file = Setting(
    default_value=None,
    description="Location of the private key",
)
settings.broadcast_schedule = Setting(
    default_value=60 * 10,
    description="How often should we broadcast our contact information, in seconds",
)
settings.nodes_discovery_schedule = Setting(
    default_value=60 * 30,
    description="How often should we ask for new nodes, in seconds",
)
settings.contact_discovery_schedule = Setting(
    default_value=60 * 15,
    description="How often should we ask for new nodes, in seconds",
)
settings.mp_timeout = Setting(
    default_value=5,
    description=(
        "How long, in seconds, we should let processes run in the "
        "background before killing them"
    ),
)
settings.network_buffer_size = Setting(
    default_value=4096,
    description="Network buffer",
)
settings.valid_base_characters = Setting(
    default_value=(
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "!\"#$%&'()*+,-./:;<=>?[\\]^_`{|}~"
    ),
    description="Characters that can be used for custom bases - order matters",
)
settings.max_base = Setting(
    default_value=len(settings.valid_base_characters),
    description="Maximum usable base",
)
settings.upnp_lease = Setting(
    default_value=60 * 60 * 24,
    description="UPnP default lease time, in seconds",
)
settings.identifier_base = Setting(
    default_value=settings.max_base,
    description=(
        "Identifier base, specifying in which base the identifiers "
        "we work with should be in"
    ),
)
settings.rsa_keys_length = Setting(
    default_value=4096,
    description="RSA keys length, in bits",
)
settings.aes_keys_length = Setting(
    default_value=32,
    description="Length of the AES object in bytes",
    # Note: multiply by 8 to get the AES protocol used e.g., 32*8=256 (AES256)
)
settings.aes_mode = Setting(
    default_value=_AES.MODE_EAX,
    description="AES mode",
)
pow_difficulty = None
settings.pow_difficulty = Setting(
    default_value=2,
    description="Proof-of-Work difficulty",
)
settings.sami_start = Setting(
    default_value=round(_dt.timestamp(_dt(year=2020, month=1, day=1)), None),
    description="Sami epoch",
)
