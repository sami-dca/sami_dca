from __future__ import annotations

from threading import Lock


class SingletonMeta(type):
    """
    This is a thread-safe implementation of the Singleton design pattern.
    Inspired from
    https://refactoring.guru/design-patterns/singleton/python/example#example-1
    """

    __instances = {}

    __lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched.
        # Since there's no Singleton instance yet, multiple threads can
        # simultaneously pass the previous conditional and reach this
        # point almost at the same time.
        # The first of them will acquire lock and will proceed further, while
        # the rest will wait here.

        # If the program stays blocked here, waiting indefinitely for the lock,
        # it most likely is due to a never-ending process in the callback.
        with cls.__lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves
            # the lock block, a thread that might have been waiting for the
            # lock release may then enter this section. But since the
            # Singleton field is already initialized, the thread won't
            # create a new object.
            if cls not in cls.__instances:
                instance = super().__call__(*args, **kwargs)
                instance.init()
                cls.__instances[cls] = instance
        return cls.__instances[cls]


class Singleton(metaclass=SingletonMeta):
    def init(self):
        """
        This method is called when the first instance is created.
        """
        pass
