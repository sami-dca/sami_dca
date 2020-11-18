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
        },
        "author": node_structure
    }

    # Probably outdated, as well as the "preparation" concept.
    prepared_message_structure = {
        "content": str,
        "meta": {
            "time_sent": int,
            "time_received": int,
            "digest": str,
            "id": int
        },
        "author": node_structure
    }

    # Requests section

    request_standard_structure = {
        "status": str,
        "data": dict,
        "timestamp": int
    }

    ake_request_structure = {
        "status": str,
        "data": {
            "key": {
                aes_key_structure
            },
            "author": node_structure,
            "recipient": node_structure
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
        "data": {
            request_standard_structure
        },
        "timestamp": int
    }

    npp_request_structure = {
        "status": str,
        "data": {
            node_structure
        },
        "timestamp": int
    }

    mpp_request_structure = {
        "status": str,
        "data": {
            received_message_structure
        },
        "timestamp": int
    }

    dp_request_structure = {
        "status": str,
        "data": {
            simple_contact_structure
        },
        "timestamp": int
    }
