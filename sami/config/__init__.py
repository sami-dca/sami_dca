"""
Application's configuration.
"""

from datetime import datetime as _dt
from pathlib import Path as _Path
from random import randint as _randint

from Crypto.Cipher import AES as _AES

from ._base import Setting
from ._base import Settings as _Settings


class Identifier(int):
    base: int = 10


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
settings.local_available_port_range = Setting(
    default_value=range(1025, 65536),
    description=(
        "The range from which we will pick a random available port "
        "for the local mapping"
    ),
    user_settable="no",
)
settings.external_available_port_range = Setting(
    # https://en.wikipedia.org/wiki/User_Datagram_Protocol#Ports
    # https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers#Registered_ports
    default_value=range(49152, 65536),
    description=(
        "The range from which we will pick a random available port "
        "for the external mapping"
    ),
    user_settable="no",
)
settings.sami_port = Setting(
    # https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers#Registered_ports
    default_value=_randint(
        settings.local_available_port_range.get().start,
        settings.local_available_port_range.get().stop - 1,
    ),
    description="Default network port used by the app",
    hint=(
        "Should be contained in `local_available_port_range`. "
        "It is susceptible of being changed by internal mechanisms if it is "
        "detected that the port is used by another system. "
    ),
)
# TODO: generalize
assert settings.sami_port.get() in settings.local_available_port_range.get()
settings.broadcast_port = Setting(  # TODO: deprecate in favor of UPnP
    default_value=2108,
    description="Port used by the autodiscover",
    hint="Should be contained in `local_available_port_range`",
)
settings.external_port = Setting(
    default_value=_randint(
        settings.external_available_port_range.get().start,
        settings.external_available_port_range.get().stop - 1,
    ),
    description="External port that will be opened for outside clients to contact us",
    hint=(
        "Should be contained in `external_available_port_range`. "
        "It is susceptible of being changed by internal mechanisms if it is "
        "detected that the port is used by another system. "
    ),
)
# TODO: generalize
assert settings.external_port.get() in settings.external_available_port_range.get()
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
settings.private_key_file = Setting(
    default_value=None,
    description="Location of the private key",
)
settings.broadcast_schedule = Setting(
    default_value=60 * 10,
    description="How often should we broadcast our contact information, in seconds",
    user_settable="advanced",
)
settings.nodes_discovery_schedule = Setting(
    default_value=60 * 30,
    description="How often should we ask for new nodes, in seconds",
    user_settable="advanced",
)
settings.contact_discovery_schedule = Setting(
    default_value=60 * 15,
    description="How often should we ask for new nodes, in seconds",
    user_settable="advanced",
)
settings.network_buffer_size = Setting(
    # https://stackoverflow.com/a/2614188/9084059
    default_value=65535,
    description="Network buffer",
    user_settable="advanced",
)
settings.valid_base_characters = Setting(
    default_value=(
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "!\"#$%&'()*+,-./:;<=>?[\\]^_`{|}~"
    ),
    description="Characters that can be used for custom bases - order matters",
    user_settable="advanced",
)
settings.max_base = Setting(
    default_value=len(settings.valid_base_characters.get()),  # TODO: Make refreshable
    description="Maximum usable base",
    user_settable="no",
)
settings.upnp_lease = Setting(
    default_value=60 * 60 * 24,
    description="UPnP default lease time, in seconds",
    user_settable="advanced",
)
settings.identifier_base = Setting(
    default_value=settings.max_base,  # TODO: Make refreshable
    description=(
        "Identifier base, specifying in which base the identifiers "
        "we work with should be in"
    ),
    user_settable="no",
)
settings.rsa_keys_length = Setting(
    default_value=4096,
    description="RSA keys length, in bits",
    user_settable="advanced",
)
settings.aes_keys_length = Setting(
    default_value=32,
    description="Length of the AES object in bytes",
    # Note: multiply by 8 to get the AES protocol used e.g., 32*8=256 (AES256)
    user_settable="advanced",
)
settings.aes_mode = Setting(
    default_value=_AES.MODE_EAX,
    description="AES mode",
    user_settable="advanced",
)
settings.pow_difficulty = Setting(
    default_value=2,
    description="Proof-of-Work difficulty",
    user_settable="advanced",
)
settings.sami_start = Setting(
    default_value=round(_dt.timestamp(_dt(year=2020, month=1, day=1)), None),
    description="Sami epoch",
    user_settable="no",
)
