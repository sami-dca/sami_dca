from pathlib import Path
from typing import List, Type

from Crypto.Cipher import AES

# ---------------------------------------------------
# ----- GENERAL PARAMETERS, FEEL FREE TO MODIFY -----
# ---------------------------------------------------

# Minimum number of contacts/nodes we should know before sending our
# identity (along with theirs). The higher the better, but it must be
# set in accordance with the network's size.
min_peers: int = 0

# Lifespan of a request in seconds.
# How long we should keep a request in the raw_requests database.
# Default is two months.
# Note: seconds * minutes * hours * days * months
max_request_lifespan: int = 60 * 60 * 24 * 31 * 2

# Network port used by the app.
sami_port: int = 62362

# Port used by the autodiscover.
broadcast_port: int = 62365

# When connecting to a contact, timeout in seconds.
contact_connect_timeout: int = 10

# Number of contacts we should know before stopping the autodiscover
# broadcast.
broadcast_limit: int = 15

# Local directory where the database files will be stored.
databases_directory: Path = Path('./db/').absolute()

# Logging configuration file path
logging_conf_file: Path = Path('./sami/logging.conf').absolute()

# Log file path, in which logs will be output.
# Relative path only (because absolute causes issues on Windows)
log_file: Path = Path('./sami.log')

# A range in which we will pick a random available port.
default_port_range: List[int] = list(range(1024, 65536))

# Type (used for type hinting) of identifiers
Identifier: Type = str

# -------------------------------------
# ----- BE CAREFUL WHEN MODIFYING -----
# -------------------------------------

# Below parameters are not supposed to be modified, unless a very specific
# configuration are needed. If these are set too low, you might get
# classified as spammers by peers !

# How often should we broadcast our contact information, in seconds.
# If set too low, you might get classified as a spammer !
# Default is 10 minutes
broadcast_schedule: int = 60 * 10

# How often should we ask for new nodes, in seconds.
# If set too low, you might get classified as a spammer !
# Default is 30 minutes
nodes_discovery_schedule: int = 60 * 30

# How often should we ask for new nodes, in seconds.
# If set too low, you might get classified as a spammer !
# Default is 15 minutes
contact_discovery_schedule: int = 60 * 15

# How long, in seconds, we will let processes run in the background
# before killing them.
# Must be a strictly positive number.
# Default is 5
mp_timeout: int or float = 5

# ---------------------------------------------
# ----- DO NOT MODIFY ANYTHING UNDER THIS -----
# ---------------------------------------------

# These are core parameters.
# Modifying them will result in your client being unusable, or
# unrecognized by other peers.

# RSA keys length, in bits.
rsa_keys_length: int = 4096

# Length of the AES object in bytes. Therefore, multiply by 8 to get
# the AES protocol used. e.g., 32 * 8 = 256 ; we use AES256.
aes_keys_length: int = 32

# AES mode. Default is EAX.
aes_mode: int = AES.MODE_EAX

# Network buffer.
network_buffer_size: int = 4096

# Proof-of-Work difficulty
pow_difficulty: int = 2
