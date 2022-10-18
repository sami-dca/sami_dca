from __future__ import annotations

from abc import abstractmethod
from typing import Callable


class Monad:
    @abstractmethod
    def bind(self, f: Callable) -> Monad:
        pass


class MaybeMonad(Monad):
    def __init__(self, value: object = None):
        self.value = value

    @property
    def contains_value(self) -> bool:
        return self.value is not None

    def bind(self, f: Callable) -> MaybeMonad:
        if not self.contains_value:
            return MaybeMonad(None)

        try:
            result = f(self.value)
            return MaybeMonad(result)
        except:  # noqa
            return MaybeMonad(None)
