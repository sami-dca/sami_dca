from itertools import cycle
from time import sleep
from typing import Callable

from ...events import BaseEvent
from ...threads import BaseThread


class UIBackgroundThread(BaseThread):

    """
    Handle background events and pops up things on the UI if necessary.
    """

    def __init__(self, events_to_monitor: dict[tuple[BaseEvent, Callable]]):
        self.events_to_monitor = events_to_monitor
        super().__init__()

    def run(self):
        events_to_monitor = cycle(self.events_to_monitor)
        while self.running:
            event, event_callback = next(events_to_monitor)
            if event.is_set():
                event_callback()
            sleep(0.5)
