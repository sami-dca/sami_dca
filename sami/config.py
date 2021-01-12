# -*- coding: UTF8 -*-

from typing import List

from Crypto.Cipher import AES

from .utils import get_local_ip_address, get_public_ip_address


class Config:

    # ---------------------------------------------------
    # ----- GENERAL PARAMETERS, FEEL FREE TO MODIFY -----
    # ---------------------------------------------------

    # The maximum number of contacts we want to know.
    max_contacts: int = 50

    # Minimum number of contacts/nodes we should know before sending our identity (along with theirs).
    # The higher the better, but it must be set in accordance with the network's size.
    min_peers: int = 1

    # List of Beacons. Please refer to the documentation for more information on this concept.
    # An entry is made of an address (IP or DNS) and a port, separated by a colon (:).
    # Example : ["192.168.0.100:12345", "beacon.domain.org"]
    beacons: List[str] = []

    # If the AES key exchange is not established within this delay, abort it.
    # In seconds ; default is one week.
    # Note: seconds * minutes * hours * days
    kep_timeout: int = 60 * 60 * 24 * 7

    # Lifespan of a request in seconds.
    # How long we should keep a request in the raw_requests database.
    # Default is two months.
    # Note: seconds * minutes * hours * days * months
    max_request_lifespan: int = 60 * 60 * 24 * 31 * 2

    # Network ports used by the system.
    port_send: int = 62362
    port_receive: int = port_send + 1  # Needs to be exactly one above the send port.

    # Whether public and private IPs should appear in the logs.
    # If you have to share your logs with a third-party (e.g. to report a bug)
    # you should turn this to False.
    # Note: it is not retroactive.
    log_ip_addresses: bool = True

    # IP address on the local network
    local_ip_address = get_local_ip_address(log_ip_addresses=log_ip_addresses)

    # Public IP address, accessible from Internet.
    public_ip_address = get_public_ip_address(log_ip_addresses=log_ip_addresses)

    # When connecting to a contact, timeout in seconds.
    contact_connect_timeout: int = 10

    # Number of contacts we should know before stopping the autodiscover broadcast.
    broadcast_limit: int = 15

    # Port used by the autodiscover.
    broadcast_port: int = 62365

    # Local directory where the database files will be stored.
    # Can be relative or absolute.
    databases_directory: str = "db/"

    # -------------------------------------
    # ----- BE CAREFUL WHEN MODIFYING -----
    # -------------------------------------

    # Below parameters are not supposed to be modified, unless a very specific configuration are needed.
    # If these are set too low, you might get classified as spammers by peers !

    # How often should we broadcast our contact information, in seconds.
    # If set too low, you might get classified as a spammer !
    # Default is 10 minutes
    broadcast_schedule: int = 60 * 10

    # How often should we ask for new nodes, in seconds.
    # If set too low, you might get classified as a spammer !
    # Default is 15 minutes
    nodes_discovery_schedule: int = 60 * 15

    # How often should we ask for new nodes, in seconds.
    # If set too low, you might get classified as a spammer !
    # Default is 15 minutes
    contact_discovery_schedule: int = 60 * 15

    # How long, in seconds, we will let processes run in the background before killing them.
    # Must be a strictly positive number.
    # Default is 5
    mp_timeout: int or float = 5

    # ---------------------------------------------
    # ----- DO NOT MODIFY ANYTHING UNDER THIS -----
    # ---------------------------------------------

    # These are core parameters.
    # Modifying them will result in your client being unusable, or unrecognized by other peers.

    # Length an hexadecimal ID should have.
    id_len: int = 16

    # RSA keys length, in bits.
    rsa_keys_length: int = 4096

    # Length of the AES object in bytes. Therefore, multiply by 8 to get the AES protocol used.
    # e.g. 32 * 8 = 256 ; we use AES256.
    aes_keys_length: int = 32

    # AES mode. Default is EAX.
    aes_mode: int = AES.MODE_EAX

    # Network buffer.
    network_buffer_size: int = 4096

    # Maximum connections at once.
    network_max_conn: int = 5

    # Proof-of-Work difficulty
    pow_difficulty: int = 2

    # Status of the AES key in the database when it has not been fully negotiated.
    status_1: str = "IN-PROGRESS"

    # Status of the AES key in the database once it has been fully negotiated.
    status_2: str = "DONE"

    # Delimiter between a contact's IP and port.
    contact_delimiter: str = ":"
