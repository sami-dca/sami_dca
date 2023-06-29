from threading import Event as _Event

from .design import Singleton as _Singleton


class BaseEvent(_Singleton, _Event):
    pass


global_stop_event = BaseEvent()

database_needs_repair = BaseEvent()
