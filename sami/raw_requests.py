# -*- coding: UTF8 -*-

from .config import Config
from .message import Message
from .request import Request
from .database import Database


class RawRequests:

    def __init__(self, db_name: str = "db/raw_requests.db"):
        """
        :param str db_name: The database path.
        """
        self.db = RawRequestsDatabase(db_name)

    def purge_oldest(self, lifespan: int = Config.max_request_lifespan) -> None:
        """
        This function will remove every request that is older than the specified lifespan.

        :param int lifespan: Lifespan in seconds. Please refer to Config.max_request_lifespan.
        """
        raise NotImplemented

    def add_new_raw_request(self, request: Request) -> None:
        """
        Adds a new message to the database.

        :param Message request: A Request object.
        """
        if self.db.key_exists(self.db.requests_table, request.get_id()):
            # In this case, the message is either a duplicate (we already received it)
            # or there was a collision (very unlikely).
            return

        d = request.to_dict()

        if not Request.is_request_valid(d):
            return

        self.db.add_new_raw_request(d)

    def get_all_raw_requests(self) -> dict:
        """
        Queries the database to get all request we registered.

        :return dict: A dictionary with all requests. The key is the ID of the request, its value is the raw request.
        """
        return self.db.query_column(self.db.requests_table)

    def get_all_raw_requests_since(self, timestamp: int) -> dict:
        """
        Takes a timestamp and returns a dictionary containing every request with their timestamp between now and then.

        :param int timestamp: A timestamp, as POSIX seconds.
        :return dict: Requests: each key is a unique identifier for the request, the value is its raw content.
        """
        all_requests = self.get_all_raw_requests()
        for k, v in all_requests.items():
            if int(v["timestamp"]) < timestamp:
                all_requests.pop(k)
        return all_requests

    def get_raw_request(self, request_id: str) -> dict:
        """
        Returns the request with passed ID.

        :param str request_id: A request ID.
        :return: A dictionary. It will be empty if the ID is unknown.
        """
        if self.db.key_exists(self.db.requests_table, request_id):
            return self.db.query(self.db.requests_table, request_id)
        return {}

    def is_request_known(self, identifier: str) -> bool:
        """
        Checks if a request with passed id is already known in database.

        :param str identifier: A message identifier, as a string.
        :return bool: True if it is, False otherwise.
        """
        return self.db.key_exists(self.db.requests_table, identifier)


class RawRequestsDatabase(Database):

    """

    This database holds information on every requests received.

    Database structure:

    self.db = dict{
        requests: dict{
            request_id: dict{
                ...request_structure...
            }
        }
    }

    """

    def __init__(self, db_name: str) -> None:
        self.requests_table = "requests"
        super().__init__(db_name, {self.requests_table: dict})

    def add_new_raw_request(self, raw_request: dict) -> None:
        """
        Low-level method to add a request to the database.

        :param dict raw_request: A raw request to store, as a dictionary.
        """
        self.db.insert_dict(self.requests_table, raw_request)
