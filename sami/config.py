# -*- coding: UTF8 -*-

from Crypto.Cipher import AES

from .utils import Utils


class Config:

    # The maximum number of contacts we should know of.
    max_contacts: int = 50

    # List of Beacons.
    # An entry is made of an address (IP or DNS) and a port, separated by a colon (:).
    # Example : ["192.168.0.100:12345"]
    beacons: list = []

    # If the AES key exchange is not made within this delay, abort it.
    # In seconds, default is 604800 (one week).
    ake_timeout: int = 604800

    # Lifespan of a request in seconds.
    # After this delay, the request will automatically be removed from the raw_requests.
    # Default is 5356800, two months.
    max_request_lifespan: int = 5356800

    # Network port used by the system.
    port: int = 62355

    # IP address on the local network
    local_ip_address = Utils.get_local_ip_address()

    # Public IP address, accessible from Internet.
    public_ip_address = Utils.get_public_ip_address()

    # ---------------------------------------------
    # ----- DO NOT MODIFY ANYTHING UNDER THIS -----
    # ---------------------------------------------

    # Length an hexadecimal ID should have. DO NOT modify unless you know what you are doing.
    id_len: int = 16

    # RSA keys length, in bits.
    rsa_keys_length: int = 4096

    # Length of the AES object in bytes. Therefore, multiply by 8 to get the AES protocol used.
    # e.g. 32 * 8 = 256 ; we use AES256.
    aes_keys_length: int = 32

    # AES mode. Default is EAX.
    aes_mode: int = AES.MODE_EAX

    # Network buffer.
    network_buff_size = 4096

    # Maximum connections at once.
    network_max_conn = 5

    # Proof-of-Work difficulty
    pow_difficulty = 5
