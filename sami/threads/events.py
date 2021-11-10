from threading import Event
from ..design import Singleton


class GlobalStopEvent(Singleton, Event):
    """
    Stop event used in the control flow of all threads.
    """
    pass
