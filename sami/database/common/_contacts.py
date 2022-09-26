from sqlalchemy import exists
from typing import List, Optional

from ...config import Identifier
from ..base.models import ContactDBO
from ...utils.network import host_dns_name
from .._template.common import CommonDatabaseTemplate


class ContactsDatabase(CommonDatabaseTemplate):

    def nunique(self) -> int:
        """
        Returns the number of unique contacts we know.
        By "unique contact", we mean unique network interface.
        A single interface can have multiple contacts if it hosts multiple
        Sami instances on different ports.
        """
        contacts_dbo = self.get_all()

        # TODO
        # Resolve DNS names
        host_dns_name()
        # Compare IP addresses

    def store(self, contact: ContactDBO) -> None:
        """
        Adds a new contact to the database if it doesn't already exist.
        """
        if not self.is_known(contact.uid):
            with self._init_session() as session:
                session.add(contact)

    def remove(self, uid: Identifier) -> None:
        if not self.is_known(uid):
            return
        with self._init_session() as session:
            q = session.query(ContactDBO)\
                .where(ContactDBO.uid == uid)\
                .one_or_none()
            if q is not None:
                session.delete(q)

    def get_contact(self, uid: Identifier) -> Optional[ContactDBO]:
        with self._init_session() as session:
            contact = session.query(ContactDBO)\
                .where(ContactDBO.uid == uid)\
                .one_or_none()
            session.expunge_all()
        return contact

    def get_all(self) -> List[ContactDBO]:
        """
        Get all contacts we know, except ones with IDs listed in `exclude`.
        """
        with self._init_session() as session:
            contacts = session.query(ContactDBO).all()
            session.expunge_all()
        return contacts

    def is_known(self, uid: Identifier) -> bool:
        with self._init_session() as session:
            return session.query(exists().where(ContactDBO.uid == uid))\
                .scalar()
