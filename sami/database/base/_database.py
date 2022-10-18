import logging as _logging
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from ...config import settings
from .models import all_models

logger = _logging.getLogger("database")


class Database:
    # _instance = None
    engine = None
    session = None
    base = None  # Inherited must override
    name: str  # Inherited must override

    def init(self):
        settings.databases_directory.mkdir(parents=True, exist_ok=True)
        db_path = (
            Path(__file__).parent.parent.parent
            / settings.databases_directory
            / f"{self.name}.db"
        )
        self.engine = create_engine(f"sqlite:///{db_path!s}")
        self.session = sessionmaker(bind=self.engine)
        self.init_db()

    def init_db(self):
        logger.info("Initiating database")

        try:
            # Getting the count of each table,
            # so we can check if there are empty ones.
            count = self.get_tables_counts()
        except (sqlite3.OperationalError, OperationalError):
            # If we could not query the tables,
            # we must create the tables and insert the default values.
            delete_tables = False
            create_tables = True
            insert_values = True
        else:
            # If we could query the tables, no need to create nor delete them.
            delete_tables = False
            create_tables = False
            if any([v == 0 for v in count]):
                # If any of the tables are empty
                insert_values = True
            else:
                insert_values = False

        if delete_tables:
            self.delete_tables()
        if create_tables:
            self.create_tables()
        if insert_values:
            self.insert_values()

    def create_tables(self) -> None:
        """
        Create default tables (will be empty)
        """
        self.base.metadata.create_all(bind=self.engine)
        logger.info("Created all tables")

    def delete_tables(self) -> None:
        """
        Delete all the tables and their content
        """
        self.base.metadata.drop_all(bind=self.engine)
        logger.info("Deleted all tables")

    def insert_values(self):
        """
        Insert default values in the database
        """
        pass

    def init_session(self) -> Session:
        return self.session.begin()

    def get_tables_counts(self) -> dict:
        counts = {}
        with self.init_session() as session:
            for dbo in all_models:
                name = dbo.__tablename__
                count = session.query(dbo.id).count()

                counts.update({name: count})

        return counts
