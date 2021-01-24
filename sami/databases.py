# -*- coding: UTF8 -*-

import logging

from .nodes import Nodes
from .contacts import Contacts
from .raw_requests import RawRequests
from .conversations import Conversations


class Databases:

    def __init__(self):
        self.raw_requests = RawRequests()
        self.contacts = Contacts()
        self.nodes = Nodes()

        self.conversations = None

    def open_node_databases(self, identifier):
        logging.info(f'Requesting node-specific database(s) with ID {identifier!r}')
        self.conversations = Conversations(pre=identifier + "_")
