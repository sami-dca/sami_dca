# -*- coding: UTF8 -*-

from .utils import Utils
from .config import Config
from .message import Message
from .database import Database
from .encryption import Encryption


class Conversations:

    def __init__(self, repo: str = "db/", pre: str = "", db_name: str = "conversations.db"):
        """
        Initiate the Conversation object, as well as its database.

        :param str repo: Repository under which we will store the database. eg: "db/" (relative) | "/db/" (absolute)
        :param str pre: Prefix for the conversation database name. Usually, the node ID.
        :param str db_name: The database name. Gets appended to "pre".
        """
        self.db = ConversationsDatabase(repo + pre + db_name)

    # Conversations section

    def does_conversation_exist_with_node(self, node_id: str) -> bool:
        """
        Queries the database, and checks if a conversation already exists with a node.

        :param str node_id: A node ID.
        :return bool: True if the conversation exists, False otherwise.
        """
        return self.db.key_exists(self.db.keys_table, node_id)

    def get_all_conversations_ids(self) -> list:
        """
        Gets a list of all the Nodes IDs with whom a conversation has been established.
        Note: if a conversation exists with a node, this means that the AES keys have been successfully negotiated.

        :return list: List of conversation identifiers.
        """
        return list(self.db.query_column(self.db.conversation_table).keys())

    def get_all_messages_of_conversation_raw(self, conversation_id: str) -> dict:
        """
        Returns all messages of a conversation (still encrypted with our own AES key).

        :param str conversation_id: A node ID.
        :return dict: A dict of all the messages (as dictionaries) in the conversation.
        """
        # Messages are stored from the oldest to the latest, and we gather them in this order.
        return {k: v for k, v in self.db.query(self.db.conversation_table, conversation_id).items()}

    def get_all_messages_of_conversation(self, rsa_private_key, conversation_id: str) -> dict:
        """
        Returns a decrypted version of all messages of a conversation.

        :param rsa_private_key: A RSA private key object, used to decrypt the AES key and therefore the messages.
        :param str conversation_id: A node ID.
        :return dict: A dict of all the messages in the conversation, decrypted.
        """
        aes_key, nonce = self.get_decrypted_aes(rsa_private_key, conversation_id)
        messages: dict = self.get_all_messages_of_conversation_raw(conversation_id)
        for k, v in messages.items():
            messages[k] = Message.decrypt_message(aes_key, nonce, v)
        return messages

    def get_last_conversation_message(self, rsa_private_key, conversation_id: str) -> dict:
        """
        Gets the last message of a conversation.

        :param rsa_private_key: A RSA private key, used to decrypt the message.
        :param str conversation_id: A node ID.
        :return dict: A message, as a dict.
        """
        pass

    def store_new_message(self, rsa_private_key, conversation_id: str, message: Message) -> None:
        """
        Stores a new message in the database.

        :param rsa_private_key: A RSA private key object.
        :param str conversation_id: A conversation ID.
        :param Message message: A message object.
        :return:
        """
        aes_key, nonce = self.get_decrypted_aes(rsa_private_key, conversation_id)
        message_id = message.get_id()
        message_data = message.to_dict()
        message_data = Message.encrypt_message(aes_key, nonce, message_data)
        self.db.insert_dict(self.db.conversation_table, {message_id: message_data})

    def get_message_from_id(self, rsa_private_key, conversation_id: str, message_id: str) -> dict or None:
        """
        Returns the message with passed ID.

        :param rsa_private_key: A RSA private key object.
        :param str conversation_id: The ID of the conversation to search in.
        :param str message_id: A message ID.
        :return dict|None: Dictionary containing the message if it exists, None otherwise.
        """
        if not self.does_conversation_exist_with_node(conversation_id):
            return
        messages_raw = self.get_all_messages_of_conversation_raw(conversation_id)
        try:
            message: dict = messages_raw[message_id]
        except IndexError:
            return
        aes_key, nonce = self.get_decrypted_aes(rsa_private_key, conversation_id)
        de_message = Message.decrypt_message(aes_key, nonce, message)
        return de_message

    # Keys section

    def store_aes(self, rsa_public_key, key_id: str, key: bytes, timestamp: int) -> None:
        """
        This function is called at every step of the AKE negotiation to store the AES in the database.

        :param rsa_public_key: A RSA public key object.
        :param str key_id: A node ID
        :param bytes key: A key, as bytes, containing both the key and the nonce. It is either 16 or 48 bytes.
        :param int timestamp: The timestamp of the negotiation.
        """
        values = {
            Config.aes_keys_length / 2: "IN-PROGRESS",
            Config.aes_keys_length + Config.aes_keys_length / 2: "DONE"
        }

        status = values[len(key)]  # Tries to get the status from the above dictionary ; raises KeyError if invalid.
        key = Encryption.encrypt_asymmetric(rsa_public_key, key)

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

        :param str key_id: A key ID.
        :return dict: The key information as a dictionary.
        """
        # Get the key ; the AES is still encrypted.
        # However, this dict will allow us to access its other values.
        key: dict = self.db.get_aes(key_id)
        return key

    def get_decrypted_aes(self, rsa_private_key, key_id: str) -> tuple or None:
        """
        This function returns an AES cipher (aes_key and nonce) decrypted.

        :param rsa_private_key: RSA private key object.
        :param str key_id: A node ID.
        :return tuple|None: 2-tuple: (bytes: the AES key, bytes|None: the nonce) or None if the key doesn't exist.
        """
        key = self.get_aes(key_id)
        status = key["status"]
        # Decrypts and deserializes the key
        key = Encryption.decrypt_asymmetric(rsa_private_key, key["key"])

        # Unpacks the values.
        if status is "IN-PROGRESS":
            aes_key = key
            nonce = None
        elif status is "DONE":
            aes_key = key[:Config.aes_keys_length]
            nonce = key[Config.aes_keys_length:]
        else:
            raise ValueError

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

        if self.is_aes_negotiation_expired(key_id):
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
        if status == "IN_PROGRESS":
            return False
        elif status == "DONE":
            return True
        else:
            raise ValueError(f"The status is incorrect for key \"{key_id}\": \"{status}\".")

    def is_aes_negotiation_expired(self, key_id: str) -> bool:
        """
        Checks if a launched negotiation is expired.
        Does not check if the key exists ; this verification must be done beforehand.

        :param str key_id: A key ID.
        :return bool: True if it is expired, False otherwise.
        """
        key = self.get_aes(key_id)
        timestamp = key["timestamp"]
        return Config.ake_timeout > (Utils.get_timestamp() - timestamp)


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
            node_identifier: key  # Value containing the AES key and the nonce, encrypted and serialized]
        }
    }

    """

    def __init__(self, db_name: str):
        self.conversation_table = "conversations"
        self.keys_table = "keys"
        super().__init__(db_name, {self.conversation_table: dict, self.keys_table: dict})

    def store_new_aes(self, node_id: str, key_dict: str) -> None:
        """
        Stores a new aes key.
        Does not care if it already exists ; this verification must be done beforehand.

        :param bytes node_id: A node ID.
        :param str key_dict: A value containing the AES key and the nonce, encrypted and serialised for storage.
        """
        self.insert_dict("keys", {node_id: key_dict})

    def modify_aes(self, node_id: str, key: str):
        """
        Modifies an existing AES key.
        Does not care if it exists or not. This verification must be done beforehand.

        :param str node_id: A node ID.
        :param str key: A value containing the AES key and the nonce, encrypted and serialised for storage.
        :return:
        """
        self.update("keys", node_id, key)

    def get_aes(self, key_id: str) -> dict:
        """
        Returns the AES key stored in the database.
        Does not care if it exists. This must be checked beforehand.

        :param str key_id: A key ID.
        :return dict: The key, as a dictionary.
        """
        return self.query(self.db.keys_table, key_id)
