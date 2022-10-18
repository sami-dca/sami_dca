from __future__ import annotations

import inspect
from threading import Lock


def caller_name(skip=2):
    """Get a name of a caller in the format module.class.method

    `skip` specifies how many levels of stack to skip while getting caller
    name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

    An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ""
    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if "self" in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals["self"].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != "<module>":  # top level usually
        name.append(codename)  # function or a method
    del parentframe
    return ".".join(name)


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
