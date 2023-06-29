from __future__ import annotations

from abc import abstractmethod
from typing import Callable, TypeVar

_T = TypeVar("_T")


class Monad:
    @abstractmethod
    def bind(self, f: Callable) -> Monad:
        pass


class Maybe(Monad):
    def __init__(self, value: _T = None):
        self.value = value

    def contains_value(self) -> bool:
        return self.value is not None

    def bind(self, f: Callable[[_T], _T]) -> Maybe:
        if not self.contains_value():
            return Maybe(None)

        try:
            result = f(self.value)
            return Maybe(result)
        except Exception:
            return Maybe(None)
