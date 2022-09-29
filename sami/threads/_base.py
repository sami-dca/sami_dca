import logging as _logging
import threading as th
from abc import ABC, abstractmethod

logger = _logging.getLogger("threads")


class BaseThread(ABC, th.Thread):
    def __init__(self, global_app_stop_event: th.Event, **kwargs):
        self.global_app_stop_event = global_app_stop_event
        self._stop_event = th.Event()

        super().__init__(
            name=self.__class__.__name__,
            daemon=True,
            **kwargs,
        )

    def start(self):
        super().start()
        logger.info(f"Started thread {self.name!r}")

    def stop(self):
        self._stop_event.set()
        logger.info(f"Stopped thread {self.name!r}")

    @abstractmethod
    def run(self):
        raise NotImplementedError
