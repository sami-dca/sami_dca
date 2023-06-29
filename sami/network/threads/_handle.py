import queue
import time

from loguru import logger

from ...design import Singleton
from ...threads import BaseThread
from .._queue import handle_queue
from ..requests import RequestsHandler


class RequestHandlingThread(BaseThread, Singleton):
    def run(self):
        logger.info("Beginning requests handling")
        handler = RequestsHandler()
        while self.running:
            # We don't block because we want to be able to stop the thread
            # with a condition.
            try:
                raw_req, from_address = handle_queue.get(block=False)
            except queue.Empty:
                time.sleep(2)
            else:
                handler(raw_req, from_address)
