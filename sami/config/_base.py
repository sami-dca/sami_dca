import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Literal, TypeVar

from ..design import Singleton

_T = TypeVar("_T")


@dataclass
class Setting(Generic[_T]):
    def __init__(
        self,
        *,
        default_value: _T,
        description: str,
        hint: str | None = None,
        user_settable: Literal["yes", "advanced", "no"] = "yes",
    ):
        self.default_value = self._value = default_value
        self.description = description
        self.hint = hint
        self.user_settable = user_settable

    def __repr__(self):
        return f"<Setting {self._value!r}>"

    def set(self, new_value: _T) -> None:
        self._value = new_value

    def get(self) -> _T:
        return self._value


_S = TypeVar("_S")


class Settings(Singleton):
    # TODO: return value directly with correct type hinting.

    _settings: dict[str, Setting]
    _settings_file: Path = Path(__file__).parent.parent / "settings.pkl"

    def init(self):
        self.__dict__.update({"_settings": {}})
        self._settings = self._load()

    def _load(self) -> dict[str, Setting]:
        """
        Tries to read the settings from disk.
        """
        if self._settings_file.is_file():
            # TODO: validate schema
            return pickle.load(self._settings_file.open("rb"))
        else:
            return {}

    def save(self) -> None:
        """
        Writes the settings to the disk.
        """
        pickle.dump(self._settings, self._settings_file.open("wb"))

    def __repr__(self):
        return f"Settings: {self._settings!r}"

    def __getitem__(self, item: str) -> Setting[_S]:
        return self.__getattr__(item)

    def __setitem__(self, key: str, value: _S | Setting[_S]):
        self.__setattr__(key, value)

    def __getattr__(self, item: str) -> Setting[_S]:
        if item in self.__dict__:
            return self.__dict__[item]
        return self._settings[item]

    def __setattr__(self, key: str, value: _S | Setting[_S]):
        if key in self.__dict__:
            self.__dict__.update({key: value})
        else:
            if isinstance(value, Setting):
                if key not in self._settings:
                    self._settings.update({key: value})
            else:
                self._settings[key].set(value)
        self.save()
