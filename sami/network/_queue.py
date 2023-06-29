from queue import Queue as _Queue

from ..objects import Contact as _Contact
from .requests import Request as _Request

# Requests in this queue will be sent by an independent thread
send_queue: _Queue[tuple["Network", _Request, _Contact]] = _Queue()  # noqa

# Requests in this queue will be handled by an independent thread
handle_queue: _Queue[tuple[_Request, str]] = _Queue()
