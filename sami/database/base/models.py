"""
Defines the database models.
Note: docstrings are written with the numpy format.
See file `./_models_parser.py` for more information.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

CommonBase = declarative_base()
PrivateBase = declarative_base()


class ContactDBO(CommonBase):
    """
    Holds information about the ``Contacts`` we know

    Attributes
    ----------

    id : int
        Primary identifier

    uid : str
        Unique contact identifier

    address : str
        IP address or DNS name of the ``Contact``

    port : int
        Network port on which the ``Client`` is listening

    last_seen : int
        UNIX timestamp of the last time we interacted with this ``Contact``

    """

    __tablename__ = "contacts"

    id: int = Column(Integer, primary_key=True)
    uid: str = Column(String)
    address: str = Column(String(255))
    port: int = Column(Integer)
    last_seen: int = Column(Integer)


class NodeDBO(PrivateBase):
    """
    Holds information about the ``Nodes`` we know.

    Attributes
    ----------

    id : int
        Primary identifier

    uid : str
        Unique node identifier

    rsa_n : int
        RSA modulus used to reconstruct the public key

    rsa_e : int
        RSA public exponent used to reconstruct the public key

    hash : str
        Hash of `rsa_n` and `rsa_e`

    sig : str
        Cryptographic signature of `hash`

    """

    __tablename__ = "nodes"

    id: int = Column(Integer, primary_key=True)
    uid: str = Column(String)
    rsa_n: int = Column(Integer)
    rsa_e: int = Column(Integer)
    hash: str = Column(String)
    sig: str = Column(String)


class RequestDBO(CommonBase):
    """
    Keeps track of all the ``Requests`` we received.

    Attributes
    ----------

    id : int
        Primary identifier

    uid : str
        Unique request identifier

    protocol : str
        Name of the protocol

    data : str
        JSON-encoded content of the ``Request``

    timestamp : int
        UNIX timestamp of the moment the ``Request`` was sent

    """

    __tablename__ = "raw_requests"

    id: int = Column(Integer, primary_key=True)
    uid: str = Column(String)
    protocol: str = Column(String(8))
    data: str = Column(String)
    timestamp: int = Column(Integer)


class MessageDBO(PrivateBase):
    """
    Contains all the ``Messages`` that belong to the ``Conversations``
    we're part of.

    Attributes
    ----------

    id : int
        Primary identifier

    uid : str
        Message unique identifier

    content : str
        Symmetrically encrypted content of the ``Message``

    time_sent : int
        UNIX timestamp of the moment it was sent

    time_received : int
        UNIX timestamp of the moment we received it

    digest : str
        Cryptographic digest of the content

    author_id : int
        Identifier of the author ``Node``

    conversation_id : int
        Identifier of the conversation this ``Message`` is part of

    """

    __tablename__ = "messages"

    id: int = Column(Integer, primary_key=True)
    uid: str = Column(String)
    content: str = Column(String)
    time_sent: int = Column(Integer)
    time_received: int = Column(Integer)
    digest: str = Column(String)
    author_id = Column(ForeignKey("nodes.uid", ondelete="CASCADE"))
    conversation_id: str = Column(ForeignKey("conversations.uid", ondelete="CASCADE"))


class KeyDBO(PrivateBase):
    """
    Stores the asymmetrically encrypted symmetric encryption key.
    These keys are used to decrypt ``Conversations``.

    Attributes
    ----------

    id : int
        Primary identifier

    uid : str
        Unique key identifier

    key : str
        Asymmetrically encrypted symmetric key

    nonce : int
        Nonce derived from the key

    conversation_id : int
        Identifier of the ``Conversation`` this ``Key`` is linked to

    timestamp : int
        UNIX timestamp of the moment the key was reconstructed from
        the negotiated parts

    """

    __tablename__ = "keys"

    id: int = Column(Integer, primary_key=True)
    uid: str = Column(String)
    key: str = Column(String)
    nonce: str = Column(String)
    conversation_id: str = Column(ForeignKey("conversations.uid", ondelete="CASCADE"))
    timestamp: int = Column(Integer)


class KeyPartDBO(PrivateBase):
    """
    Stores the key parts we sent and received as part of *KEP* negotiations.

    Attributes
    ----------

    id : int
        Primary identifier

    uid : str
        Unique key part identifier

    key_part : str
        Asymmetrically encrypted symmetric key part

    conversation_id : int
        Identifier of the ``Conversation`` this ``KeyPart`` is linked to

    """

    __tablename__ = "key_parts"

    id: int = Column(Integer, primary_key=True)
    uid: str = Column(String)
    key_part: str = Column(String)
    conversation_id: str = Column(ForeignKey("conversations.uid", ondelete="CASCADE"))


class ConversationDBO(PrivateBase):
    """
    Registers all the conversations we're part of.

    Attributes
    ----------

    id : int
        Primary identifier

    uid : str
        Unique conversation identifier

    """

    __tablename__ = "conversations"

    id: int = Column(Integer, primary_key=True)
    uid: str = Column(String)


class ConversationMembershipDBO(PrivateBase):
    """
    Holds mappings defining which ``Nodes`` are members of which
    ``Conversations``.

    Attributes
    ----------

    id : int
        Primary identifier

    node_id : int
        Identifier of a ``Node``

    conversation_id : int
        Identifier of the ``Conversation`` `node_id` is part of

    """

    __tablename__ = "conversations_memberships"

    id: int = Column(Integer, primary_key=True)
    node_id: str = Column(ForeignKey("nodes.uid", ondelete="CASCADE"))
    conversation_id: str = Column(ForeignKey("conversations.uid", ondelete="CASCADE"))


all_models = [
    ContactDBO,
    NodeDBO,
    RequestDBO,
    MessageDBO,
    KeyDBO,
    KeyPartDBO,
    ConversationDBO,
    ConversationMembershipDBO,
]
