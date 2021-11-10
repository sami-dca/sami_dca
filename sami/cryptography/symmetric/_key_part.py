from __future__ import annotations

from typing import List, Optional

from Crypto.Random import get_random_bytes

from ...nodes import Node
from ...utils import get_id
from ...config import Identifier
from ..hashing import hash_object
from ...nodes.own import MasterNode
from ...config import aes_keys_length
from ...structures import KEPStructure
from ...database.base.models import KeyPartDBO
from ...database.private import KeyPartsDatabase
from ..serialization import serialize_bytes, deserialize_string, \
    encode_string

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...messages import Conversation

import logging as _logging
logger = _logging.getLogger('cryptography')


class KeyPart:

    """
    Attributes
    ----------

    id: Identifier
        Unique key part identifier.

    conversation_id: Identifier
        Conversation this incomplete key is part of.

    """

    def __init__(self, key_part: bytes, conversation_id: Identifier):
        self._key_part = key_part
        self.conversation_id = conversation_id
        self.id = self._compute_id()

    def __len__(self) -> int:
        return len(self._key_part)

    @classmethod
    def new(cls, conversation: Conversation) -> KeyPart:
        """
        Constructs a new key.
        Adopts the appropriate length depending on the number of members in the
        conversation.
        """
        def get_designated(value: Identifier,
                           possibilities: List[Identifier]) -> Identifier:
            """
            Designate a member for creating the filling key part.
            TODO
            """
            return possibilities[0]

        remainder = aes_keys_length % len(conversation.members)
        floor = aes_keys_length // len(conversation.members)

        identifiers = [node.id for node in conversation.members]
        identifiers.sort()
        common_identifier = get_id(hash_object(identifiers))

        designated_member = get_designated(common_identifier, identifiers)
        master_node = MasterNode()
        if designated_member == master_node.id:
            key_length = remainder + floor
        else:
            key_length = floor

        return cls(
            key_part=get_random_bytes(key_length),
            conversation_id=conversation.id,
        )

    @classmethod
    def from_id(cls, identifier: Identifier) -> Optional[KeyPart]:
        dbo = KeyPartsDatabase().get_incomplete_key(identifier)
        if dbo is None:
            return
        return cls.from_dbo(dbo)

    @classmethod
    def from_data(cls, key_part_data: KEPStructure) -> Optional[KeyPart]:
        """
        Takes a key part as an encrypted dictionary, and will try to decrypt it
        to return a KeyPart.
        If decryption fails, we return None.
        """
        from ...messages import Conversation
        enc_key_part = key_part_data.key_part
        part_hash = key_part_data.hash
        part_sig = key_part_data.sig

        members = [
            Node.from_data(member)
            for member in key_part_data.members
        ]
        if any([member is None for member in members]):
            # At least one of the specified nodes is invalid
            return
        conversation_id = Conversation([node.id for node in members]).id

        author_node = Node.from_data(key_part_data.author)
        if author_node is None:
            # Node data is invalid
            return

        master_node = MasterNode()
        key_part_str = master_node.private_key.decrypt_asymmetric(enc_key_part)
        if key_part_str is None:
            # The key part is not meant for us
            return

        key_part_bytes = encode_string(key_part_str)
        h = hash_object(key_part_bytes)
        if h.hexdigest() != part_hash:
            # Hashes do not match
            return

        if not author_node.public_key.is_signature_valid(h, part_sig):
            # Signature is invalid
            return

        return KeyPart(
            key_part=encode_string(key_part_str),
            conversation_id=conversation_id,
        )

    @classmethod
    def from_dbo(cls, dbo: KeyPartDBO):
        se_en_half_key = dbo.key_part

        master_node = MasterNode()
        half_key = master_node.private_key.decrypt_asymmetric(se_en_half_key)

        return cls(
            key_part=deserialize_string(half_key),
            conversation_id=dbo.conversation_id,
        )

    def to_dbo(self) -> KeyPartDBO:
        master_node: MasterNode = MasterNode()
        se_en_key_part = master_node.private_key.encrypt_asymmetric(
            serialize_bytes(self._key_part)
        )

        return KeyPartDBO(
            key_part=se_en_key_part,
            conversation_id=self.conversation_id,
        )

    def store(self) -> None:
        KeyPartsDatabase().store(self.to_dbo())

    def is_known(self) -> bool:
        return KeyPartsDatabase().is_known(self.id)

    def _compute_id(self) -> Identifier:
        return get_id(hash_object([self._key_part]))
