# -*- coding: UTF8 -*-

from .contact import Contact
from .database import Database


class Contacts:

    def __init__(self, db_name: str = "db/contacts.db"):
        self.db = ContactsDatabase(db_name)

    def add_contact(self, contact: Contact) -> None:
        """
        Adds a new contact to the database.

        :param Contact contact: A contact object, the one to store.
        """
        contact_id = contact.get_id()
        if not self.db.key_exists(self.db.contacts_table, contact_id):
            self.db.insert_dict(self.db.contacts_table, {contact_id: contact.to_dict()})

    def get_all_contacts_ids(self) -> list:
        """
        Get all IDs of the database.
        Each entry represent a contact ID.

        :return list: A list of contact IDs.
        """
        return list(self.db.query_column(self.db.contacts_table).keys())

    def get_contact_info(self, contact_id: str) -> dict:
        """
        Tries to get the information of a contact.
        Takes care of the situation if the contact does not exist yet.

        :param str contact_id: A contact ID.
        :return: A dictionary containing the node's information.
        """
        if self.contact_exists(contact_id):
            return self.db.query(self.db.contacts_table, contact_id)
        else:
            return {}

    def contact_exists(self, contact_id: str) -> bool:
        """
        Checks if a contact exists in the database.

        :param str contact_id: A node ID.
        :return: True if it exists, False otherwise.
        """
        return self.db.key_exists(self.db.contacts_table, contact_id)


class ContactsDatabase(Database):

    """

    This database holds information about the contacts we know.
    it is shared among identities on this computer.
    This includes: address, port and last seen timestamp.

    Database structure:

    self.db = dict{
        contacts: dict{
            contact_identifier: dict{
                "address": "address:port"  # An IP address and a port.
                "last_seen": "timestamp"  # Timestamp of the last time the node was seen.
            }
        }
    }

    """

    def __init__(self, db_name: str):
        self.contacts_table = "contacts"
        super().__init__(db_name, {self.contacts_table: dict})
