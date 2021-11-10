from abc import ABC

from sqlalchemy.orm import Session


class _DatabaseTemplate(ABC):

    database = None  # Override in subclasses

    def _init_session(self) -> Session:
        return self.database.init_session()
