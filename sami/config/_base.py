import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..design import Singleton

# TODO: fix type hinting, see in __init__.py why that's a problem


@dataclass
class Setting:
    def __init__(
        self,
        *,
        default_value: Any,
        description: str,
        hint: Optional[str] = None,
    ):
        self.default_value = self._value = default_value
        self.description = description
        self.hint = hint

    def __repr__(self):
        return f"<Setting {self._value!r}>"

    def set(self, new_value: Any) -> None:
        self._value = new_value

    def get(self) -> Any:
        return self._value


class Settings(Singleton):
    _settings: Dict[str, Setting]
    _settings_file: Path = Path(__file__).parent.parent / "settings.pkl"

    def init(self):
        self.__dict__.update({"_settings": {}})
        self._settings = self._load()

    def _load(self) -> Dict[str, Setting]:
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

    def __getitem__(self, item: str):
        return self.__getattr__(item)

    def __setitem__(self, key: str, value: Union[Any, Setting]):
        self.__setattr__(key, value)

    def __getattr__(self, item: str):
        if item in self.__dict__:
            return self.__dict__[item]
        return self._settings[item].get()

    def __setattr__(self, key: str, value: Union[Any, Setting]):
        if key in self.__dict__:
            self.__dict__.update({key: value})
            return
        if isinstance(value, Setting):
            if key not in self._settings:
                self._settings.update({key: value})
        else:
            self._settings[key].set(value)
