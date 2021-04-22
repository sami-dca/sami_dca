# -*- coding: UTF8 -*-


class Structures:

    node_structure = {
        "rsa_n": int,
        "rsa_e": int,
        "hash": str,
        "sig": str
    }

    simple_contact_structure = {
        "address": str
    }

    stored_contact_structure = {
        "address": str,
        "last_seen": int
    }

    aes_key_structure = {
        "value": str,
        "hash": str,
        "sig": str
    }

    received_message_structure = {
        "content": str,
        "meta": {
            "time_sent": int,
            "digest": str
        },
        "author": node_structure
    }

    stored_message_structure = {
        "content": str,
        "meta": {
            "time_sent": int,
            "time_received": int,
            "digest": str
        }
    }

    # Requests section

    request_standard_structure = {
        "status": str,
        "data": dict,
        "timestamp": int
    }

    kep_request_structure = {
        "status": str,
        "data": {
            "key": aes_key_structure,
            "author": node_structure,
            "recipient": node_structure,
        },
        "timestamp": int
    }

    wup_ini_request_structure = {
        "status": str,
        "data": {
            "timestamp": int,
            "author": simple_contact_structure
        },
        "timestamp": int
    }

    wup_rep_request_structure = {
        "status": str,
        "data": request_standard_structure,
        "timestamp": int
    }

    bcp_request_structure = {
        "status": str,
        "data": simple_contact_structure,
        "timestamp": int
    }

    npp_request_structure = {
        "status": str,
        "data": node_structure,
        "timestamp": int
    }

    mpp_request_structure = {
        "status": str,
        "data": received_message_structure,
        "timestamp": int
    }

    dp_request_structure = {
        "status": str,
        "data": {"author": simple_contact_structure},
        "timestamp": int
    }

    @staticmethod
    def mapping(struct_name) -> dict or None:
        m = {
            "node_structure": Structures.node_structure,
            "simple_contact_structure": Structures.simple_contact_structure,
            "stored_contact_structure": Structures.stored_contact_structure,
            "aes_key_structure": Structures.aes_key_structure,
            "received_message_structure": Structures.received_message_structure,
            "stored_message_structure": Structures.stored_message_structure,
            "request_standard_structure": Structures.request_standard_structure,
            "kep_request_structure": Structures.kep_request_structure,
            "wup_ini_request_structure": Structures.wup_ini_request_structure,
            "wup_rep_request_structure": Structures.wup_rep_request_structure,
            "npp_request_structure": Structures.npp_request_structure,
            "mpp_request_structure": Structures.mpp_request_structure,
            "dp_request_structure": Structures.dp_request_structure,
        }

        if struct_name in m:
            return m[struct_name]
        else:
            return
