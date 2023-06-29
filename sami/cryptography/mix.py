import pydantic

from ..objects import MasterNode, Node, is_private_key_loaded
from .serialization import deserialize_string
from .symmetric import SymmetricKey, SymmetricKeyPart


class EncryptedSymmetricKeyPart(pydantic.BaseModel):
    """
    Asymmetrically encrypted symmetric encryption value part.
    """

    value: str
    author: Node

    def to_clear(self) -> SymmetricKeyPart | None:
        if not is_private_key_loaded():
            return
        master_node = MasterNode()
        clear_value = master_node.private_key.decrypt_asymmetric(self.value)
        if clear_value is None:
            return
        return SymmetricKeyPart(
            value=deserialize_string(clear_value), author=self.author
        )


class EncryptedSymmetricKey(pydantic.BaseModel):
    """
    Asymmetrically encrypted symmetric encryption value.
    """

    value: str
    nonce: str

    def to_clear(self) -> SymmetricKey:
        master_node = MasterNode()
        clear_value = master_node.private_key.decrypt_asymmetric(self.value)
        clear_nonce = master_node.private_key.decrypt_asymmetric(self.nonce)
        return SymmetricKey(
            value=deserialize_string(clear_value),
            nonce=deserialize_string(clear_nonce),
        )
