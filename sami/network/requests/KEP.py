from __future__ import annotations

from typing import Optional

from ...cryptography.hashing import hash_object
from ...cryptography.serialization import serialize_bytes
from ...cryptography.symmetric import KeyPart
from ...messages import Conversation
from ...nodes import Node
from ...nodes.own import MasterNode
from ...structures import KEPStructure
from .base import Request


class KEP(Request):

    full_name = "Keys Exchange Protocol"
    to_store = True
    inner_struct = KEPStructure

    @staticmethod
    def validate_data(data: inner_struct) -> Optional[inner_struct]:
        # We do not validate the key part

        author = Node.from_data(data.author)
        if author is None:
            # Invalid author info
            return

        for potential_node in data.members:
            member = Node.from_data(potential_node)
            if member is None:
                return

        return data

    @classmethod
    def new(cls, key_part: KeyPart, to: Node, conversation: Conversation) -> KEP:
        master_node: MasterNode = MasterNode()

        key_part_str = serialize_bytes(key_part._key_part)
        se_en_half_aes_key = to.public_key.encrypt_asymmetric(key_part_str)
        h_object = hash_object(key_part_str)
        h_str = h_object.hexdigest()
        se_sig = master_node.private_key.get_signature(h_object)

        own_node = Node(
            master_node.public_key,
            master_node.sig,
        )

        return cls(
            KEPStructure(
                key_part=se_en_half_aes_key,
                hash=h_str,
                sig=se_sig,
                author=own_node.to_data(),
                members=[node.to_data() for node in conversation.get_members()],
            )
        )
