# -*- coding: UTF8 -*-

import os

from .config import Config
from .database import Database


class Nodes:

    def __init__(self, db_name: str = "nodes.db"):
        db_path = os.path.join(Config.databases_directory, db_name)
        self.db = NodesDatabase(db_path)

    def add_node(self, node) -> None:
        """
        Stores a node information in the database if it does not exist already.

        :param Node node: A node object, the one to store.
        """
        node_id = node.get_id()
        if not self.node_exists(node_id):
            self.db.insert_dict(self.db.nodes_table, {node_id: node.to_dict()})

    def get_all_node_ids(self) -> list:
        """
        Lists all known nodes' IDs.

        :return list: A list of all the nodes ID we know.
        """
        return list(self.db.query_column(self.db.nodes_table).keys())

    def get_node_info(self, node_id: str) -> dict or None:
        """
        Gets a node ID and query the database to retrieve the node's information.
        If the key doesn't exist in the database, returns None.

        :param str node_id: A node ID.
        :return dict|None: A dictionary containing the information of the node.
        """
        if self.node_exists(node_id):
            return self.db.query(self.db.nodes_table, node_id)

    def node_exists(self, node_id: str) -> bool:
        """
        Checks whether we know this node or not.

        :param str node_id: A node ID.
        :return bool: True if we know it, False otherwise.
        """
        return self.db.key_exists(self.db.nodes_table, node_id)


class NodesDatabase(Database):

    """

    This database holds information about the nodes we know (our P2P network).

    Database structure:

    self.db = dict{
        nodes: dict{
            node_identifier: dict{
                "rsa_n": 123456789,
                "rsa_e": 123456,
                "hash": "hexdigest",
                "sig": "signature"
            }
        }
    }

    """

    def __init__(self, db_name: str):
        self.nodes_table = "nodes"
        super().__init__(db_name, {self.nodes_table: dict})
