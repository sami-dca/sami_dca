# -*- coding: UTF8 -*-

import os

from typing import List, Set

from .config import Config
from .message import Message
from .database import Database
from .utils import get_timestamp
from .encryption import Encryption


class Conversations:

    def __init__(self, master_node, directory: str = Config.databases_directory, pre: str = "",
                 db_name: str = "conversations.db"):
        """
        Initiate the Conversation object, as well as its database.

        :param master_node: The master node object. Will be used to encrypt and decrypt the database.
        :param str directory: Directory under which we will store the database. eg: "db/" (relative) | "/db/" (absolute)
        :param str pre: Prefix for the conversation database name. Usually, the node ID.
        :param str db_name: The database name. Gets appended to "pre".
        """
        db_path = os.path.join(directory, pre + db_name)
        self.db = ConversationsDatabase(db_path)
        self.master_node = master_node

    # Conversations section

    def does_conversation_exist_with_node(self, node_id: str) -> bool:
        """
        Queries the database, and checks if a conversation exists with a node.

        :param str node_id: A node ID.
        :return bool: True if the conversation exists, False otherwise.
        """
        return self.db.key_exists(self.db.keys_table, node_id)

    def get_all_available_conversations_ids(self) -> Set[str]:
        """
        Returns a list of all the Nodes IDs with whom we can start a conversation.
        This means that for a node to be listed here, we must have negotiated an AES key.
        Includes the ones we already have started a conversation with.
        """
        return set(self.db.query_column(self.db.keys_table).keys())

    def get_all_conversations_ids(self) -> Set[str]:
        """
        Gets a list of all the Nodes IDs with whom we have started a conversation.
        """
        return set(self.db.query_column(self.db.conversation_table).keys())

    def get_all_messages_of_conversation_raw(self, conversation_id: str) -> dict:
        """
        Returns all messages of a conversation (still encrypted).

        :param str conversation_id: A node ID.
        :return dict: A dict of all the messages (as dictionaries) in the conversation.
        """
        # Messages are stored from the oldest to the latest, and we gather them in this order.
        return {k: v for k, v in self.db.query(self.db.conversation_table, conversation_id).items()}

    def get_all_messages_of_conversation(self, conversation_id: str) -> List[Message]:
        """
        Returns all messages of a conversation, decrypted.

        :param str conversation_id: A node ID.
        :return list: A list of all the messages in the conversation, decrypted.
        """
        aes_key, nonce = self.get_decrypted_aes(conversation_id)
        messages = self.get_all_messages_of_conversation_raw(conversation_id)
        messages_list = []
        for k, v in messages.items():
            messages_list.append(Message.from_dict_encrypted(aes_key, nonce, v))
        return messages_list

    def get_last_conversation_message(self, conversation_id: str) -> Message:
        """
        Gets the last message of a conversation, decrypted.

        :param str conversation_id: A node ID.
        :return dict: A decrypted message.
        """
        aes_key, nonce = self.get_decrypted_aes(conversation_id)
        messages = self.get_all_messages_of_conversation_raw(conversation_id)
        last_index = list(messages.keys())[-1]
        return Message.from_dict_encrypted(aes_key, nonce, messages[last_index])

    def store_new_message(self, conversation_id: str, message: Message) -> None:
        """
        Stores a new message in the database.
        IMPORTANT: This message must be encrypted.

        :param str conversation_id: The ID of the conversation the message belongs to.
        :param Message message: An encrypted message object.
        """
        # Get conversation AES key
        message_id = message.get_id()
        message_data = message.to_dict()
        self.db.insert_dict(self.db.conversation_table, {conversation_id: {message_id: message_data}})

    def get_message_from_id(self, conversation_id: str, message_id: str) -> Message or None:
        """
        Returns the decrypted message with passed ID.

        :param str conversation_id: The ID of the conversation to search in.
        :param str message_id: A message ID.
        :return Message|None: The decrypted message if it exists, None otherwise.
        """
        if not self.does_conversation_exist_with_node(conversation_id):
            return
        messages_raw = self.get_all_messages_of_conversation_raw(conversation_id)
        try:
            message: dict = messages_raw[message_id]
        except IndexError:
            return
        aes_key, nonce = self.get_decrypted_aes(conversation_id)
        de_message = Message.from_dict_encrypted(aes_key, nonce, message)
        return de_message

    # Keys section

    def store_aes(self, key_id: str, key: bytes, timestamp: int) -> None:
        """
        This function is called at every step of the KEP negotiation to store the AES in the database.

        :param str key_id: The ID under which the AES key will be referenced.
        :param bytes key: A key, as bytes, containing both the key and the nonce. It is either 16 or 48 bytes.
        :param int timestamp: The timestamp of the negotiation.
        """
        values = {
            # 16 bytes because we only have a half-key.
            Config.aes_keys_length / 2: Config.status_1,
            # 48 bytes because we are concatenating the key and the nonce.
            Config.aes_keys_length + Config.aes_keys_length / 2: Config.status_2
        }

        status = values[len(key)]  # Tries to get the status from the above dictionary ; raises KeyError if invalid.
        key = Encryption.encrypt_asymmetric(self.master_node.rsa_public_key, key)

        key_dict = {
            "key": key,
            "status": status,
            "timestamp": timestamp
        }

        self.update_aes(key_dict, key_id)

    def aes_key_exists(self, key_id: str) -> bool:
        """
        Checks if an AES key exists in the database.
        Does not care if the key has been fully negotiated or not.

        :param str key_id: The key ID to look for.
        :return bool: True if it exists, False otherwise.
        """
        return self.db.key_exists(self.db.keys_table, key_id)

    def update_aes(self, aes_key: dict, key_id: str) -> None:
        """
        Updates an AES key if it exists in the database, creates it otherwise.

        :param aes_key: A
        :param dict key_id:
        :return:
        """
        if self.aes_key_exists(key_id):
            self.db.modify_aes(key_id, aes_key)
        else:
            self.db.store_new_aes(key_id, aes_key)

    def get_aes(self, key_id: str) -> dict:
        """
        Gets an AES key from the database.
        The AES key values are still encrypted, however, we can access its other values.
        Does not check if the key exists ; this verification must be done beforehand.

        :param str key_id: A key ID.
        :return dict: The key information as a dictionary.
        """
        key: dict = self.db.get_aes(key_id)
        return key

    def get_decrypted_aes(self, key_id: str) -> tuple:
        """
        This function returns an AES cipher (aes_key and nonce) decrypted.

        :param str key_id: A node ID.
        :return tuple|None: 2-tuple: (bytes: the AES key, bytes|None: the nonce) or None if the key doesn't exist.
        """
        if not self.is_aes_negotiation_launched(key_id):
            return None, None
        key = self.get_aes(key_id)
        status = key["status"]
        # Decrypts and deserializes the key
        key = Encryption.decrypt_asymmetric(self.master_node.get_rsa_private_key(), key["key"])

        # Unpacks the values.
        if status == Config.status_1:
            aes_key = key
            nonce = None
        elif status == Config.status_2:
            aes_key = key[:Config.aes_keys_length]
            nonce = key[Config.aes_keys_length:]
        else:
            raise ValueError(f'Invalid status: {status!r}')

        return aes_key, nonce

    def remove_aes_key(self, key_id: str) -> None:
        """
        Removes from the database the AES key identified by "node_id".

        :param str key_id: A node ID.
        """
        if self.db.column_exists(self.db.keys_table):
            if self.db.key_exists(self.db.keys_table, key_id):
                self.db.drop(self.db.keys_table, key_id)

    def remove_aes_key_if_expired(self, key_id: str) -> None:
        """
        Removes the specified AES key if it is expired.
        Otherwise, does nothing.

        :param str key_id: A key ID.
        """
        if not self.aes_key_exists(key_id):
            return

        # If the key as been negotiated, end.
        if self.is_aes_negotiated(key_id):
            return

        if self.is_aes_negotiation_launched(key_id) and self.is_aes_negotiation_expired(key_id):
            self.remove_aes_key(key_id)

    def is_aes_negotiation_launched(self, node_id: str) -> bool:
        """
        Checks if the key identified by node_id is set in the database.
        If it isn't, this means the negotiation has not been launched yet.

        :param str node_id: A node ID.
        :return bool: True if it is set, False otherwise.
        """
        return self.db.key_exists(self.db.keys_table, node_id)

    def is_aes_negotiated(self, key_id: str) -> bool:
        """
        This function checks if an AES key has been negotiated with specified node.

        :param str key_id: A key ID.
        :return bool: True if it is negotiated, False otherwise.
        """
        if not self.aes_key_exists(key_id):
            return False

        key = self.db.get_aes(key_id)

        status = key["status"]
        if status == Config.status_1:
            return False
        elif status == Config.status_2:
            return True
        else:
            raise ValueError(f"The status is incorrect for key {key_id!r}: {status!r}.")

    def is_aes_negotiation_expired(self, key_id: str) -> bool:
        """
        Checks if a launched negotiation is expired.
        Does not check if the key exists ; this verification must be done beforehand.
        Also returns False if the negotiation is done.

        :param str key_id: A key ID.
        :return bool: True if it is expired, False otherwise.
        """
        key = self.get_aes(key_id)
        timestamp = int(key["timestamp"])
        status = key["status"]
        # If the negotiation is still in progress.
        if status == Config.status_1:
            return Config.kep_decay < (get_timestamp() - timestamp)
        else:
            return False


class ConversationsDatabase(Database):

    """

    This database holds information about conversations with known nodes.
    This includes: aes key and nonce and messages (content, timestamps, hash, sig, etc)

    Database structure:

    self.db = dict{
        conversations: dict{
            node_identifier: dict{
                message_identifier: dict{
                    ...message_structure...
                }
            }
        },
        keys: dict{
            node_identifier: {
                "key",  # Value containing the AES key and the nonce, encrypted and serialized]
                "status",
                "timestamp"
            }
        }
    }

    """

    def __init__(self, db_path: str):
        self.conversation_table = "conversations"
        self.keys_table = "keys"
        super().__init__(db_path, {self.conversation_table: dict, self.keys_table: dict})

    def store_new_aes(self, node_id: str, key_dict: dict) -> None:
        """
        Stores a new aes key.
        Does not care if it already exists ; this verification must be done beforehand.

        :param bytes node_id: A node ID.
        :param dict key_dict: A value containing the AES key and the nonce, encrypted and serialised for storage.
        """
        self.insert_dict(self.keys_table, {node_id: key_dict})

    def modify_aes(self, node_id: str, key_dict: dict):
        """
        Modifies an existing AES key.
        Does not care if it exists or not. This verification must be done beforehand.

        :param str node_id: A node ID.
        :param str key_dict: A value containing the AES key and the nonce, encrypted and serialised for storage.
        :return:
        """
        self.update(self.keys_table, node_id, key_dict)

    def get_aes(self, key_id: str) -> dict:
        """
        Returns the AES key stored in the database.
        Does not care if it exists. This must be checked beforehand.

        :param str key_id: A key ID.
        :return dict: The key, as a dictionary.
        """
        return self.query(self.keys_table, key_id)
