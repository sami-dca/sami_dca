# -*- coding: UTF8 -*-

import os

from typing import List

from .config import Config
from .contact import Contact
from .database import Database


class Contacts:

    def __init__(self, db_name: str = "contacts.db"):
        db_path = os.path.join(Config.databases_directory, db_name)
        self.db = ContactsDatabase(db_path)

    def add_contact(self, contact: Contact) -> None:
        """
        Adds a new contact to the database.

        :param Contact contact: A contact object, the one to store.
        """
        contact_id = contact.get_id()
        if not self.contact_exists(contact_id):
            self.db.insert_dict(self.db.contacts_table, {contact_id: contact.to_dict()})

    def remove_contact(self, contact_id: str) -> None:
        if self.contact_exists(contact_id):
            self.db.drop(self.db.contacts_table, contact_id)

    def get_all_contacts_info(self) -> dict:
        """
        :return dict: A dictionary containing as keys contact IDs and as values their information
        """
        return self.db.query_column(self.db.contacts_table)

    def get_all_contacts_ids(self, exclude: List[str] = None) -> List[str]:
        """
        Get all IDs of the database.
        Each entry represent a contact ID.

        :return List[str]: A list of contact IDs.
        """
        if not exclude:
            exclude = list()
        all_contacts = list(self.db.query_column(self.db.contacts_table).keys())
        all_contacts = set(all_contacts)
        for identifier in exclude:
            if identifier in all_contacts:
                all_contacts.remove(identifier)
        return list(all_contacts)

    def get_contact_info(self, contact_id: str) -> dict or None:
        """
        Tries to get the information of a contact.

        :param str contact_id: A contact ID.
        :return dict|None: A dictionary containing the contact's information if it exists, None otherwise.
        """
        if self.contact_exists(contact_id):
            return self.db.query(self.db.contacts_table, contact_id)

    def _get_contact_info(self, contact_id: str) -> dict:
        """
        Returns the information of a contact.
        Only used locally ; does not check for contact existence.

        :param str contact_id: A contact ID.
        :return dict: A dictionary containing the contact's information.
        """
        return self.db.query(self.db.contacts_table, contact_id)

    def get_all_contacts(self, exclude: List[str] = None) -> List[Contact]:
        """
        Get all contacts we know, except listed in `exclude`

        :param List[str] exclude: A list of IDs, which we will exclude from the contacts list.
        """
        contacts = []
        for contact_id, contact_info in self.get_all_contacts_info():
            contacts.append(Contact.from_dict(contact_info))

        contact_ids = self.get_all_contacts_ids(exclude)
        contacts = list()
        for contact_id in contact_ids:
            contacts.append(Contact.from_dict(self._get_contact_info(contact_id)))
        return contacts

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

    def __init__(self, db_path: str):
        self.contacts_table = "contacts"
        super().__init__(db_path, {self.contacts_table: dict})
