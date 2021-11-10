import base64


def serialize_bytes(b: bytes) -> str:
    """
    Takes a bytes object and serialize it.
    Must be reversible with `deserialize_string()`.
    """
    return base64.b64encode(b).decode("utf-8")


def deserialize_string(s: str) -> bytes:
    """
    Takes a string and deserialize it.
    Must be reversible with `serialize_bytes()`.
    """
    return base64.b64decode(s)


def encode_string(data: str) -> bytes:
    """
    Takes a string and return a bytes encoded version of the data.
    Must be reversible with `decode_bytes()`.
    """
    return data.encode("utf-8")


def decode_bytes(data: bytes) -> str:
    """
    Takes a bytes object and return a decoded version of the data.
    Must be reversible with `encode_string()`.
    """
    return data.decode("utf-8")
