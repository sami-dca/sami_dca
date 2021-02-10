# -*- coding: UTF8 -*-

import os

from .config import Config
from .message import Message
from .request import Request
from .database import Database
from .utils import get_timestamp

from typing import List


class RawRequests:

    def __init__(self, db_name: str = "raw_requests.db"):
        """
        :param str db_name: The database path.
        """
        db_path = os.path.join(Config.databases_directory, db_name)
        self.db = RawRequestsDatabase(db_path)

    def purge_oldest(self, lifespan: int = Config.max_request_lifespan) -> None:
        """
        This function will remove every request older than the specified lifespan.

        :param int lifespan: Lifespan in seconds. Please refer to Config.max_request_lifespan.
        """
        now = get_timestamp()
        threshold = now - lifespan
        for req in self.get_all_raw_requests():
            if req.timestamp < threshold:
                self.remove_raw_request(req.get_id())

    def remove_raw_request(self, identifier: str) -> None:
        """
        Takes an ID and removes it from the database.

        :param str identifier: A request identifier
        """
        self.db.drop(self.db.requests_table, identifier)

    def add_new_raw_request(self, request: Request) -> None:
        """
        Adds a new message to the database.

        :param Message request: A Request object.
        """
        if not self.db.key_exists(self.db.requests_table, request.get_id()):
            self.db.add_new_raw_request(request)

    def get_all_raw_requests(self) -> List[Request]:
        """
        :return List[Request]: All the requests we know, as objects.
        """
        requests = []
        for req_id, req_info in self.get_all_raw_requests_info().items():
            req = Request.from_dict(req_info)
            actual_id = req.get_id()
            if actual_id != req_id:  # Verify the ID is the same
                raise ValueError(f'Inconsistency in the raw_requests database: got ID {req_id}, computed {actual_id}')
            requests.append(req)
        return requests

    def get_all_raw_requests_info(self) -> dict:
        """
        Queries the database to get all request we registered.

        :return dict: A dictionary with all requests. The key is the ID of the request, its value is the raw request.
        """
        return self.db.query_column(self.db.requests_table)

    def get_all_raw_requests_since(self, timestamp: int) -> List[Request]:
        """
        :param int timestamp: A timestamp, as POSIX seconds.
        :return List[Request]: The requests received since the specified timestamp, as a list of Request objects.
        """
        all_requests = self.get_all_raw_requests()
        for index, req in enumerate(all_requests):
            if req.timestamp < timestamp:
                all_requests.pop(index)
        return all_requests

    def get_raw_request(self, request_id: str) -> dict or None:
        """
        Returns the request with passed ID ; nothing if the ID is unknown.

        :param str request_id: A request ID.
        :return dict|None: A dictionary or None.
        """
        if self.is_request_known(request_id):
            return self.db.query(self.db.requests_table, request_id)

    def get_last_received(self) -> Request:
        """
        :return Request: The last request we received, as a Request object).
        """
        requests = self.get_all_raw_requests_info()
        last_index = list(requests.keys())[-1]
        return Request.from_dict(requests[last_index])

    def is_request_known(self, identifier: str) -> bool:
        """
        Checks if the request ID passed is known.

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

    def __init__(self, db_path: str) -> None:
        self.requests_table = "requests"
        super().__init__(db_path, {self.requests_table: dict})

    def add_new_raw_request(self, raw_request: Request) -> None:
        """
        Low-level method to add a request to the database.

        :param dict raw_request: A raw request to store, as a dictionary.
        """
        self.insert_dict(self.requests_table, {raw_request.get_id(): raw_request.to_dict()})
