# Introduction

**Sami** is the name of a decentralized communication app.  

It is an open-source project developed by Lilian Boulard, 
and publicly available for free on GitHub.

It currently allows for textual messages exchange.  
The network created by users is decentralized, meaning no one controls it.

It is mainly inspired from 
[Ethereum Whisper](https://geth.ethereum.org/docs/whisper/how-to-whisper),
the [Scuttlebutt protocol](https://ssbc.github.io/scuttlebutt-protocol-guide/) 
and [Jami](https://www.jami.net).

While the network is very resilient at medium and large scale, 
there can be some unexpected errors and problems at a very small scale (only a 
few users).  
Usually, the larger the network, the better.

# Keys and identities

The first and only thing a user needs to participate in the Sami network 
is an identity.

An identity is referred to as a ``Node`` and is an asymmetric key pair 
(a public key and a private key).  
It typically represents a person or a bot.  
It is normal for a person to have several identities.

Because identities are long and random, no coordination or permission is 
required to create a new one, which is essential to the network’s design.

A name is generated from the user's public key, giving it a human-readable 
identifier.

If a user loses their secret key or has it stolen, they will need to generate a 
new identity. Keys are ___only___ stored in the user's local files, and 
therefore **cannot** be recovered by any third-party.

The public key of any ``Node`` is publicly available and transmitted in some 
network protocols, as we'll see later in this document.

## Dark network

Sami adopts a *dark network* architecture.

This means that, by design, a ``Node`` (an identity on the Sami P2P network) 
and a ``Contact`` (an IP address, the user's identity on the Internet) 
cannot be linked.

# Attacks

In this section, we'll have a look at a few common attacks, as well as 
Sami-specific known attacks.

The goal of documenting attacks is for current and future maintainers to 
know where security and reliability can be improved in Sami.  
We are aware that documenting attacks might give ideas to some, but we hope
to interest security researchers to come up together with solutions.

## Sybil attacks

In a Sybil attack, an attacker takes over the network by creating numerous 
identities.  
Here, two situations apply:

### Node takeover

By *node takeover*, we mean that an attacker overloads the P2P network with 
Sami identities.

This simply has no effect on the P2P network.

### Contact takeover

On the other hand, *contact takeover* can be a problem.
This is because while a ``Node`` is a virtual identity, a ``Contact`` is a 
physical identity.

Note that technically, anybody with some computer skills could create 
at most 65535 ``Contacts`` on one network interface.  
Multiply this by the number of computers an attacker could have at his disposal,
and the number of network interfaces each can have, and it's easy to 
understand that *contact takeovers* is pretty simple.

Therefore, in the attacks we'll see further on, we'll talk about 
*contact takeover* and not *node takeover*.

## 51% attacks

A 51% attack refers to an attack on a decentralized network by a 
group of attackers controlling more than 50% of the network's workforce.

This type of attacks is not applicable to the Sami network.

There are two possible ways of seeing the situation:

### Configuration corruption

In this case, a group of attackers modifies their client's configuration to one 
that is insecure.  
This will result in a different network from the usual users' - a fork.  
This is due to the fact that Sami clients are very rigid regarding other nodes' 
configuration, and will discard any malformed requests.

### Attackers consensus

If a group of seemingly normal users controlled by attackers were to join the network, 
there is next to nothing they will be able to do, unless the network is very small, 
in which case the dark network architecture can be endangered.

To avoid this kind of situation, there is a built-in threshold of unique contacts ^1 
one must know before starting to send identifying requests.  
However, this preemptive measure will not be enough if 49 out of 50 clients are 
controlled by bad actors !

A simple measure against this type of attack is simply to have a group of 
legitimate users on the network.  
They don't even need to add up to 50% of the network or more ; for any 
additional user, it becomes exponentially harder to identify each one.

1. two contacts are considered unique if they have a different public 
address.
   The client will try to translate DNS names to IP addresses.
   Local network contacts are all considered unique.

## Flooding attacks

Flooding attacks consist in flooding the network with requests.  
At the moment, no solution is implemented, but is being actively worked on.

The easy way out would be to implement proof-of-work, and while it is
efficient pre-quantum, it has terrible effects on power consumption, 
and massively contributes to climate change (cf Bitcoin).

Another option would be to implement a per-``Contact`` measure,
which would ignore ``Requests`` sent by a ``Contact`` when spamming.

## Deny attacks

A deny attack consists, for an attacker, to not forward any or part of the 
requests he receives.  
While there are statistical ways of finding that (e.g. statistical association),
none is yet implemented.

However, a simple counter-measure is simply to have a significant part of 
legitimate users on the P2P network.

# Terms

### *Note on formatting*

In the structure definition, the format used is :
- `Type` `value_name` - A quick description of the value

Several times, "timestamps" are mentioned. They are formatted as UNIX seconds ;
[more on this subject](https://www.unixtimestamp.com/).

## Client

A ``Client`` is an instance of the Sami software, and an individual on the network.  
One ``Client`` can host multiple ``Nodes`` (identities), while not at the same time.  
It is a relay on the network, and is accessible via its ``Contact`` information.

## Node

A ``Node`` is person on the network, identified by a public key.

Its structure is defined as:

- `Integer` `rsa_n` - RSA modulus
- `Integer` `rsa_e` - RSA public exponent
- `String` `hash` - Serialized hash of the concatenated `rsa_n` and `rsa_e`
- `String` `sig` - Cryptographic signature of `hash` made by the author

Sending a ``Message`` to a ``Node`` is not instantaneous, 
unlike ``Contacts`` communication.

### Master node

A ``MasterNode`` is our own identity.  
Unlike the ``Node``, we have its asymmetric private key.

## Contact

You can see a ``Contact`` as a "link" to a ``Client`` on the network.  
Several ``Contacts`` can link to a single client: one ``Contact`` is 
created by network interface.

If the ``Contact``'s address is a DNS name, it will be stored as-is, 
and the IP address will be resolved each time we interact with it, 
making it dynamic.

The network's design prevents a ``Contact`` information to be linked to 
a ``Node`` information.

If the recipient ``Client`` is running, a communication with 
a ``Contact`` is instantaneous.

## Message

A ``Message`` is... a... message. I know, shocking !

It is encrypted and signed by its author, and sent as part of a ``Conversation``.

## Conversation

A ``Conversation`` is a set of ``Messages`` distributed to a list of ``Nodes``.  

To exchange encrypted messages, all the members of a ``Conversation``
must have negotiated a common ``SymmetricKey``.

Its identifier is deterministically computed based on its members, 
making it common.

Paranoia note: an attacker could create a rainbow table of all the existing 
``Conversations`` IDs based on the ``Nodes`` he knows, and could figure out the 
members of any ``Conversation`` (given that he knows all the ``Nodes`` part 
of it).

## SymmetricKey

*Note to the reader: symmetric encryption means using the same key 
for encrypting and decrypting data.*

A ``SymmetricKey``, is a symmetric cipher used to encrypt ``Messages``
of any given ``Conversation``.

They are negotiated via the *Keys Exchange Protocol* (*KEP*)

Currently, we use the *Advanced Encryption Standard* (*AES*), as it is 
*military-grade* (woo! buzzword!) with 256-bits keys.
It provides very good security for the pre-quantum era.

## AsymmetricKey

*Note to the reader: symmetric encryption means using different keys 
for encrypting and decrypting data. The public key can encrypt, 
and the private key can decrypt*

An ``AsymmetricKey`` is an asymmetric cipher used to encrypt ``SymmetricKeys``
in the database, as well as to cryptographically sign data in some protocols.

We currently use the *Rivest-Shamir-Adleman* (*RSA*) cryptosystem, 
with 4096-bits keys. It provides very good security for the pre-quantum era.

# Discovery

After a user has generated its identity, it needs to find some peers.  
To connect to somebody, you need to know its ``Contact`` information.  
The list of discovered ``Contacts`` will appear in the ``Client``'s user interface.

There a several ways of discovering a ``Contact``:

## Beacons

A ``Beacon`` is a standard ``Client`` that is assured to run at all time.  
They are hard-coded inside the configuration and managed by the project maintainers.  

While this goes against the decentralized design, it is common practice (e.g., 
Bitcoin), and a good way to discover new ``Contacts`` and ``Nodes`` without 
flooding the network.

## Local network

Once the Sami ``Client`` is opened, and if it doesn't know enough ``Contacts``,
it will broadcast over the network a *Broadcast Contact Protocol* (*BCP*) 
``Request`` containing its own ``Contact`` information, while listening for others.  
It will do so regularly (depending on the local configuration).

When catching a *BCP* ``Request``, the ``Client`` will save the information if it
doesn't know it already.

# Protocols

All ``Requests`` have a common structure:

- `String` `status` - The request type
- `Dictionary` `data` - The content of the `Request`
- `Integer` `timestamp` - The timestamp of the time when the `Request` was built

In the following ``Requests``' definition, we'll be explaining the structure of 
the `data` field.
The `status` is the name of the section. 
E.g., for *Node Publication Protocol - NPP*, `status = NPP`.

In the diagrams:
- Boxes in *italic* designate entry points of the protocol,
  otherwise said, the events that triggers the process
- Boxes in **bold** designate final actions

## Broadcast Contact Protocol - "BCP"
This protocol is used for sharing ``Contact`` information with peers
on a local network.  
![BCP diagram](./doc/BCP.png)
### Request structure
- `Contact` `author` - Our own ``Contact`` information

## Contact Sharing Protocol - "CSP"
This protocol is used when we want to share ``Contacts`` with a peer.  
![CSP diagram](./doc/CSP.png)
### Request structure
- `List[Contact]` `contacts` - The list of ``Contacts`` we know.

## Discover Contacts Protocol - "DCP"
Asks a peer for a list of ``Contacts``.
### Request structure
- `Contact` `author` - Our own ``Contact`` information

## Discover Nodes Protocol - "DNP"
Asks a ``Contact`` for a list of ``Nodes``.
It is triggered regularly, reinforcing the distributed network each time.
### Request structure
- `Contact` `author` - Our own ``Contact`` information

## Keys Exchange Protocol - "KEP"
This protocol is used when negotiating a new ``SymmetricKey`` 
for a new ``Conversation``.
The protocol is implemented in such a way that all members of a 
``Conversation`` are partly in charge of negotiating a common key.  
By default, we launch a *KEP* handshake with each ``Node`` we discover.
It allows the user to be able to speak with every ``Node`` he knows.  
We never send the full key nor the nonce over the network.  
If the protocol has been respected by all parties, they should have the same 
key and nonce.  
![KEP diagram](./doc/KEP.png)
### Request structure
- `String` `part` - The key part, encrypted with the target member's 
                     public key
- `String` `hash` - The hexadecimal digest of the clear key part
- `String` `sig` - The cryptographic signature of `hash`
- `Node` `author` - The ``Node`` information of the author of this key part
- `List[Node]` `members` - The list of ``Nodes`` member of this conversation
### Technical notes
#### Hash
The ``hash`` is computed from the clear key part because if it was on its
encrypted counterpart, anybody could claim the request to be theirs.
#### Determine target
We can know whether the key is addressed to us 
by trying to decrypt the key part.
#### Members
``members`` is a list of ``Nodes``, which is heavy, but assures that everyone 
knows each other.
#### Key partitioning
If `N / M` doesn't return a round integer - for example `N = 32` 
(the key is 32 bytes long) and `M = 5` (there are 5 members in the 
``Conversation``), `32 / 5 = 6.4` - we follow this process:
1. Let `r` be the remainder: `r = 32 % 5 = 2` and `f` be the floor division 
   result: `f = 32 // 5 = 6`
2. Let `K` be the list of the ``Node`` identifiers
3. Sort `K` in ascending order, concatenate them, and hash the result
4. We then get the member identifier which is the closest to this value: he
   is the one designated for creating the key part left. 
5. If we are the designated member, we create a key of length `r + f`
   (`2 + 6 = 8`), otherwise we create a key of length `f`

## Message Propagation Protocol - "MPP".
This protocol is used for transmitting a ``Message``.
### Request structure
- `Message` `message` - The ``Message`` to propagate
- `String` `conversation` - The ID of the ``Conversation`` this ``Message`` 
  is part of

## Node Publication Protocol - "NPP"
This protocol is used for sending ``Nodes`` over the network.  
![NPP diagram](./doc/NPP.png)
### Request structure
- `List[Node]` `nodes` - The list of ``Nodes`` we know (including ours).

## What's Up Protocol - "WUP"
This protocol is used to gather all the ``Requests`` we missed while we were 
offline.
### INI
![WUP_INI diagram](./doc/WUP_INI.png)
#### Request structure
- `Integer` `beginning` - A timestamp specifying the beginning of the interval
- `Integer` `end` - A timestamp specifying the end of the interval
- `Contact` `author` - Our own ``Contact`` information

### REP
![WUP_REP diagram](./doc/WUP_REP.png)
#### Request structure
- `List[Request]` `requests` - The list of `Requests` found in the specified interval

## Tables

### `contacts`
Holds information about the ``Contacts`` we know
- `int` `id` - Primary identifier
- `str` `uid` - Unique contact identifier
- `str` `address` - IP address or DNS name of the ``Contact``
- `int` `port` - Network port on which the ``Client`` is listening
- `int` `last_seen` - UNIX timestamp of the last time we interacted with this ``Contact``

### `nodes`
Holds information about the ``Nodes`` we know.
- `int` `id` - Primary identifier
- `str` `uid` - Unique node identifier
- `int` `rsa_n` - RSA modulus used to reconstruct the public key
- `int` `rsa_e` - RSA public exponent used to reconstruct the public key
- `str` `hash` - Hash of `rsa_n` and `rsa_e`
- `str` `sig` - Cryptographic signature of `hash`

### `raw_requests`
Keeps track of all the ``Requests`` we received.
- `int` `id` - Primary identifier
- `str` `uid` - Unique request identifier
- `str` `protocol` - Name of the protocol
- `str` `data` - JSON-encoded content of the ``Request``
- `int` `timestamp` - UNIX timestamp of the moment the ``Request`` was sent

### `messages`
Contains all the ``Messages`` that belong to the ``Conversations`` we're part of.
- `int` `id` - Primary identifier
- `str` `uid` - Message unique identifier
- `str` `content` - Symmetrically encrypted content of the ``Message``
- `int` `time_sent` - UNIX timestamp of the moment it was sent
- `int` `time_received` - UNIX timestamp of the moment we received it
- `str` `digest` - Cryptographic digest of the content
- `int` `author_id` - Identifier of the author ``Node``
- `int` `conversation_id` - Identifier of the conversation this ``Message`` is part of

### `keys`
Stores the asymmetrically encrypted symmetric encryption key. These keys are used to decrypt ``Conversations``.
- `int` `id` - Primary identifier
- `str` `uid` - Unique key identifier
- `str` `key` - Asymmetrically encrypted symmetric key
- `int` `nonce` - Nonce derived from the key
- `int` `conversation_id` - Identifier of the ``Conversation`` this ``Key`` is linked to
- `int` `timestamp` - UNIX timestamp of the moment the key was reconstructed from the negotiated parts

### `key_parts`
Stores the key parts we sent and received as part of *KEP* negotiations.
- `int` `id` - Primary identifier
- `str` `uid` - Unique key part identifier
- `str` `key_part` - Asymmetrically encrypted symmetric key part
- `int` `conversation_id` - Identifier of the ``Conversation`` this ``KeyPart`` is linked to

### `conversations`
Registers all the conversations we're part of.
- `int` `id` - Primary identifier
- `str` `uid` - Unique conversation identifier

### `conversations_memberships`
Holds mappings defining which ``Nodes`` are members of which ``Conversations``.
- `int` `id` - Primary identifier
- `int` `node_id` - Identifier of a ``Node``
- `int` `conversation_id` - Identifier of the ``Conversation`` `node_id` is part of

