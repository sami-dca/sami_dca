from typing import List, Optional

from sqlalchemy import exists

from ...config import Identifier
from ...utils.network import DNSName, get_address_object, host_dns_name
from .._template.common import CommonDatabaseTemplate
from ..base.models import ContactDBO


class ContactsDatabase(CommonDatabaseTemplate):
    def nunique(self) -> int:
        """
        Returns the number of unique contacts we know.
        By "unique contact", we mean unique network interface.
        A single interface can have multiple contacts if it hosts multiple
        Sami instances on different ports.
        FIXME: Right now, we use IPs to differentiate, but we should instead
         want to use MAC addresses as AFAIK a NIC can have multiple IPs.
        """
        contacts_dbo = self.get_all()

        # Convert to network objects
        names = [get_address_object(dbo) for dbo in contacts_dbo]
        # Convert DNS names to IPs
        names = [host_dns_name(name) if name is DNSName else name for name in names]
        # Remove duplicates
        names = set(names)

        return len(names)

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
            q = session.query(ContactDBO).where(ContactDBO.uid == uid).one_or_none()
            if q is not None:
                session.delete(q)

    def get_contact(self, uid: Identifier) -> Optional[ContactDBO]:
        with self._init_session() as session:
            contact = (
                session.query(ContactDBO)
                .where(ContactDBO.uid == uid)
                .one_or_none()
            )
            session.expunge_all()
        return contact

    def get_all(self) -> List[ContactDBO]:
        """
        Lists all contacts we know.
        """
        with self._init_session() as session:
            contacts = session.query(ContactDBO).all()
            session.expunge_all()
        return contacts

    def is_known(self, uid: Identifier) -> bool:
        with self._init_session() as session:
            return session.query(exists().where(ContactDBO.uid == uid)).scalar()  # noqa
