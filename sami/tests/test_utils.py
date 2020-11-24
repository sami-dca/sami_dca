from unittest import mock

import pytest

from sami.utils import Utils


def test_json():
    dic = {
        "Test": "This is a test dictionnary",
        "with": "123456",
        "It contains": [
            "different",
            "values",
        ],
        "And": {
            "Intricate": {
                "data": "1337",
            },
        },
    }

    processed_dir = Utils.decode_json(Utils.encode_json(dic))

    assert dic == processed_dir


@mock.patch("time.time")
def test_timestamp(mock_time):
    mock_time.return_value = 123456.0

    tm = Utils.get_timestamp()
    assert tm == 123456

    f_tm = Utils.get_date_from_timestamp()
    assert f_tm == '10:17:36 01/02/70'


def test__validate_fields():
    dic = {
        "status": "Working!",
        "data": {
            "oui": {
                "non": {
                    "val1": "17",
                    "val2": [1, 2, 3],
                },
                "maybe": {},
            },
            "perhaps": "no",
        },
        "timestamp": "123456",
        "nonce": "123456"
    }

    structure = {
        "status": str,
        "data": {
            "oui": {
                "non": {
                    "val1": int,
                    "val2": list,
                },
                "maybe": dict,
            },
            "perhaps": str,
        },
        "timestamp": int,
        "nonce": str
    }

    assert Utils._validate_fields(dic, structure)


def test_is_int():
    assert Utils.is_int(13)
    assert Utils.is_int("13")
    assert not Utils.is_int("thirteen")


def test_is_address_valid():
    valid_addresses = [
        "192.168.0.15",
        "10.0.1.5",
        "224.125.89.12",
        "google.com",
        "sami.example.org",
        "localhost"
    ]
    invalid_addresses = [
        "",
        "192.168.0.0",
        "192.268.5.5",
        "255.255.255.255",
        "192.168.0.255",
        "123.123.123.123.123"
        "123.123.123",
        "foo."
        ".foo.bar"
        "a*"
        "foo"
    ]

    for add in valid_addresses:
        assert Utils.is_address_valid(add)

    for add in invalid_addresses:
        assert not Utils.is_address_valid(add)


def test_is_network_port_valid():
    valid_ports = [
        "1"  # Not recommended at all, but possible
        "1024",
        "15000",
        "19631"
        "65535",
    ]
    invalid_ports = [
        "0",
        "65536",
        "70000",
        "123456"
    ]

    for p in valid_ports:
        assert Utils.is_network_port_valid(p)

    for p in invalid_ports:
        assert not Utils.is_network_port_valid(p)

    with pytest.raises(ValueError):
        assert Utils.is_network_port_valid("")
        assert Utils.is_network_port_valid("test")
