# -*- coding: UTF8 -*-

import os

from .node import Node
from .config import Config
from .database import Database

from typing import List


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

    def get_all_nodes(self) -> List[Node]:
        """
        Lists all known nodes.

        :return List[Node]: A list of nodes.
        """
        nodes = []
        for node_id in self.get_all_node_ids():
            node_info = self._get_node_info(node_id)
            nodes.append(Node.from_dict(node_info))
        return nodes

    def get_node_info(self, node_id: str) -> dict or None:
        """
        Takes a node ID and queries the database to retrieve its information.

        :param str node_id: A node ID.
        :return dict|None: A dictionary containing the node's information if it exists, None otherwise.
        """
        if self.node_exists(node_id):
            return self.db.query(self.db.nodes_table, node_id)

    def _get_node_info(self, node_id: str) -> dict:
        """
        Takes a node ID and queries the database to retrieve its information.
        Bypasses the verification, as it assumes the node exists in the database.

        :param str node_id: A node ID.
        :return dict: A dictionary containing the node's information.
        """
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

    def __init__(self, db_path: str):
        self.nodes_table = "nodes"
        super().__init__(db_path, {self.nodes_table: dict})
