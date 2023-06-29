import queue
import time

from ...design import Singleton
from ...threads import BaseThread
from .._queue import send_queue


class RequestSenderThread(BaseThread, Singleton):
    def run(self):
        while self.running:
            # We don't block because we want to be able to stop the thread
            # with a condition.
            try:
                network, request, contact = send_queue.get(block=False)
            except queue.Empty:
                time.sleep(2)
            else:
                network.send_request(request, contact)
