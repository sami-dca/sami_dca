from __future__ import annotations

import pydantic

from ...cryptography.hashing import hash_object
from ...cryptography.mix import EncryptedSymmetricKeyPart
from ...cryptography.serialization import serialize_bytes
from ...objects import Conversation, MasterNode, Node
from ._base import RequestData


class KEP(RequestData, pydantic.BaseModel):
    our_key_part: EncryptedSymmetricKeyPart
    hash: str
    sig: str
    author: Node
    members: set[Node]

    _full_name = "Keys Exchange Protocol"
    _to_store = True
    _waiting_for_answer = False

    class Config:
        allow_mutation = False

    @classmethod
    @pydantic.validator("hash")
    def _check_hash(cls, value: str, values: dict) -> str:
        assert hash_object(values["our_key_part"]).hexdigest() == value, "Invalid hash"
        return value

    @classmethod
    @pydantic.validator("sig")
    def _check_sig(cls, sig: str, values: dict) -> str:
        h = hash_object(values["our_key_part"])
        assert values["author"].public_key.is_signature_valid(
            h, sig
        ), "Invalid signature"
        return sig

    @classmethod
    def new(cls, conversation: Conversation, recipient: Node) -> KEP:
        master_node = MasterNode()

        our_key_part = [
            key for key in conversation.key if key.author.id == master_node.id
        ][0]

        key_part_value_str = serialize_bytes(our_key_part.value)
        se_en_value = recipient.public_key.encrypt_asymmetric(key_part_value_str)
        h_obj = hash_object(key_part_value_str)
        h_str = h_obj.hexdigest()
        se_sig = master_node.private_key.get_signature(h_obj)

        own_node = Node(
            public_key=master_node.public_key,
            sig=master_node.sig,
            pattern=master_node.pattern,
        )

        return cls(
            our_key_part=EncryptedSymmetricKeyPart(
                value=se_en_value,
                author=own_node,
            ),
            hash=h_str,
            sig=se_sig,
            author=own_node,
            members=conversation.members,
        )
