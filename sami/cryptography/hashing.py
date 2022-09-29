import logging as _logging
import pickle
from typing import Any

from Crypto.Hash import SHA256

from ..config import pow_difficulty

logger = _logging.getLogger("cryptography")


def hash_object(obj: Any) -> SHA256.SHA256Hash:
    """
    Returns a hash object of the value passed.
    """
    return SHA256.new(pickle.dumps(obj))


def compute_pow(request):
    """
    Takes a request and returns the same with an additional nonce.
    This nonce is computed with a Proof-of-Work algorithm.
    """
    difficulty = pow_difficulty
    limit = 10 * (difficulty + 1)
    iterations = 10 * limit
    # We limit the PoW iterations.
    # If we reach this limit (next "else" loop), we issue an error.
    for n in range(iterations):
        request.set_nonce(n)
        j: str = request.to_json()
        h = hash_object(j)
        hx = h.hexdigest
        if hx[0:difficulty] == "0" * difficulty:
            break
    else:
        raise logger.error(
            f"Could not compute proof-of-work in {iterations} "
            f"iterations (difficulty={difficulty})"
        )
    return request
