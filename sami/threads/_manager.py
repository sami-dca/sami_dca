from ..design import Singleton
from ..events import global_stop_event
from ._base import BaseThread


class ThreadManager(Singleton):
    def __init__(self):
        self._threads: list[BaseThread] = []

    def register(self, thread: BaseThread, start: bool = True) -> None:
        self._threads.append(thread)
        if start:
            thread.start()

    def stop_all(self) -> None:
        global_stop_event.set()
        for thread in self._threads:
            thread.stop()

    def join_all(self) -> None:
        for thread in self._threads:
            thread.join()
