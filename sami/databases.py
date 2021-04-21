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

        self.are_node_specific_databases_open: bool = False
        self.master_node = None
        self.conversations = None

    def open_node_databases(self, master_node):
        self.master_node = master_node
        identifier = self.master_node.get_id()
        logging.info(f'Requesting node-specific database(s) with ID {identifier!r}')
        self.conversations = Conversations(self.master_node, pre=identifier + "_")
        self.are_node_specific_databases_open = True
        # TODO: Load KEP and NPP requests we didn't process. Note: SQL query on `status` to find KEP requests.
