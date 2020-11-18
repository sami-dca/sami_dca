# Introduction

Sami is a decentralized communication application.
\
This application allows for text message exchange.
\
The network is decentralized, meaning no one can control it.

It is inspired by [Ethereum Whisper](https://geth.ethereum.org/docs/whisper/how-to-whisper)
and the [Scuttlebutt protocol](https://ssbc.github.io/scuttlebutt-protocol-guide/).


# Keys and identities

The first thing a user needs to participate 
in the Sami network is an identity.
\
An identity is called a "node" and is a 
RSA key pair that typically represents a person, 
a device, a server or a bot.
\
It’s normal for a person to have several identities.

Because identities are long and random, 
no coordination or permission is required to create a new one,
which is essential to the network’s design.

A name is generated from the user's RSA keys, 
giving it a readable identifier among other nodes.

If a user loses their secret key or 
has it stolen they will need to generate a new identity.

The public key of a node is presented to users and 
transmitted in some parts of the network protocol. 
For more information on this topic, 
please refer to the "Node" terms section.

A node and a contact should not be linked together ; 
it's the way the network is designed.


# Terms

## Client

A ``client`` is an instance of the Sami software.
\
One ``client`` can host multiple ``nodes``, 
while not at the same time.
\
It is a relay on a network via 
its information (an address and a port) :

```json
{
  "address": "127.0.0.1:1234"
}
```

## Node

### "Simple" node

A ``node`` is an individual on the network, 
identified by a RSA public key.
Note: Two values are derived from this key 
(modulus (n) and public exponent (e)):
  - Its ID ; which length is defined 
    by the config attribute ``id_len``.
  - Its name ; a series of words 
    picked the file ``lib/dictionary``.

Its structure is defined as:

```json
{
  "rsa_n": "1234567890",
  "rsa_e": "123456",
  "hash": "Hash_of_the_above_information",
  "sig": "Signature of the above hash"
}
```

### Master node

A ``master node`` is our own client.
\
Unlike the simple ``node``, 
we have the RSA private key.

## Contact

A ``contact`` is a client's identity on the network.
\
It is defined by an address (IP or DNS name) and a port.

The network design prevents a ``contact`` information 
to be linked to a ``node`` information.

## Messages

A ``message`` is a... message. 
\
I know, shocking right !

It carries sensitive information, namely a user-specified value.

Theses messages are structured as follows:

```json
{
  "content": "aes_encrypted_message",
  "meta": {
    "time_sent": "123456780",
    "hash": "message_hash",
    "digest": "hash_digest"
  },
  "author": ...node_architecture...
}
```

## Conversation

A ``conversation`` is a stream of 
``messages`` exchanged with a ``node``.
\
The ``conversation``'s ID is 
the same as the ``node``'s ID.
\
To exchange encrypted messages (and be able to decrypt them),
two ``nodes`` must have negotiated an AES key 
with the ``Keys Exchange Protocol`` (``KEP``).

# Discovery

After a user has generated their identity 
they need to find some peers to connect to.
\
To connect to a peer, you need to know 
its address (IP or DNS name) and a port number ; 
this pair is called a `contact`.
\
The ``client`` will show discovered ``nodes`` 
in the ``client``'s user interface.

There a several ways to discover a node:

## Beacons

A beacon is a standard node that is 
assured to run a client at all time.
They are hard-coded inside the project and 
added and/or removed by the project maintainers.

While this goes against the decentralized design, 
it is common use (e.g. Bitcoin) and a good way 
to discover new nodes without flooding the network.

## Local network

Once a ``node`` is registered on a ``client`` 
(see "Terms" section for more information),
the ``client`` will broadcast over the network 
a specific packet, while listening for answers.
\
The client will send a packet every 10 seconds.

When a peer sees another peer’s broadcast packet 
they will save the ``client``'s information 
to exchange requests later.

## Invite code

Not implemented.

## Peer connections

Not implemented.


# Protocols

Every request made over the network has this structure:

```json
{
  "status": "REQUEST_NAME",
  "data": {
    ...information...
  },
  "timestamp": "timestamp"
}
```

## What's Up Protocol - "WUP"

1. We wake up: the user launched the ``client`` 
   and loaded his RSA private key.
2. We read the ``raw_requests`` database, 
   and we get the most recent ``time_sent``.
3. We send a ``WUP_INI request`` (with below structure) 
   to preferably a ``beacon``, otherwise a regular 
   ``node``, with ``timestamp`` as the most recent 
   ``time_sent`` found in the database, and
   ``author`` as our own ``contact`` information.

```json
{
  "status": "WUP_INI",
  "data": {
    "timestamp": "timestamp",
    "author": ...contact_structure...
  },
  "timestamp": "timestamp"
}
```

1. We receive a ``WUP_INI request``.
2. We loop through the ``raw_requests`` database, 
   and for each ``request``, we check if its 
   ``time_sent`` <= ``request_timestamp`` ;
   if it is, then we send it to the specific 
   ``contact`` with the below structure.

```json
{
  "status": "WUP_REP",
  "data": {
    ...request_structure...
  },
  "timestamp": "timestamp"
}
```

## Keys Exchange Protocol - "KEP"

This protocol is used when negotiating AES keys for a ``conversation``.
\
This is similar to the Diffie-Hellman protocol.
This avoids having one ``node`` 
in charge of deciding the AES key.

1. We detect a new ``node`` on the network 
   (we therefore have its public key)
2. We choose a random 16 bytes key 
   (precisely, AES keys length / 2).
3. We send over the network a new 
   ``KEP request`` with the below structure:

```json
{
  "status": "KEP",
  "data": {
    "key": {
      "value": "16_bytes_rsa_encrypted_AES_key",
      "hash": "hash_of_the_key",
      "sig": "signature_of_the_above_hash"
    },
    "author": ...node_structure...,
    "recipient": ...node_structure...
  },
  "timestamp": "timestamp"
}
```

4. While waiting for the reply, we store 
the request in the ``conversation`` database
with the status ``WAITING``.
5. Once we get a response to this ``request``, 
we verify its content and assemble the 
two binary keys, then derive a nonce from the key.
\
We never give that key over the network.
\
If the protocol has been respected by both party,
they should both have the same key and nonce.

1. We receive a new ``KEP request`` 
   (we have not sent one yet).
2. We verify its content.
3. We then generate a new 16 bytes random value, 
   and send it over with the same structure as above.
4. We construct the key and derive the nonce, 
   then we store it.
5. At this point, we have a working key, 
   and so should the recipient.

1. If the key is already defined 
   (it has already been negotiated with the node before)
2. We deny the negotiation, but we send 
   our key part to the node. **!!! WARNING !!!**

1. We sent our key part to the node, 
   but we didn't get any response.
2. If the timestamp is greater than 3 months, 
   we delete the entry.

## Message Propagation Protocol - "MPP".

This protocol is called when a ``message`` is received.
A typical ``MPP request`` looks like this:

```json
{
  "status": "MPP",
  "data": {
    ...message_structure...
  },
  "timestamp": "timestamp"
}
```

Requirements:
\
The AES keys negotiation must be complete 
with the ``conversation`` ``node``.

1. We receive a ``message``.
2. We check if we already received that ``message``.
3. If not, we broadcast it.
4. We store the ``request`` in the ``raw_requests`` database.
5. We try to decrypt the content.
6. If we're able to access the decrypted content,
we re-encrypt the message with our own AES key, 
and we store it in the "``onversations`` database.

## Node Publication Protocol - "NPP"

This protocol is used when sending 
a ``node`` identity over the network.

1. We receive a ``DNP`` request.
2. We broadcast it with this request form:

```json
{
  "status": "NPP",
  "data": {
    ...node_structure...
  },
  "timestamp": "timestamp"
}
```

## Contact Sharing Protocol - "CSP"

This protocol is used when we want to 
share a ``contact`` with another ``contact``.

1. We receive a ``Discover Contacts Protocol request``.
2. For every contact we know 
(we query the ``contacts`` database),
we send the following ``request`` to
the ``contact`` that made the original ``request``:

```json
{
  "status": "CSP",
  "data": {
    ...contact_structure...
  },
  "timestamp": "timestamp"
}
```

## Discover Nodes Protocol - "DNP"

This ``request`` asks for a  list of 
``nodes`` to a specific ``contact``.

It is constructed as follows:

```json
{
  "status": "DNP",
  "data": {
    "author": ...node_structure...
  },
  "timestamp": "timestamp"
}
```

## Discover Contacts Protocol - "DCP"

This ``request`` asks for a list of 
``contacts`` to a specific ``contact``.

It is constructed as follows:

```json
{
  "status": "DCP",
  "data": {
    "author": ...node_structure...
  },
  "timestamp": "timestamp"
}
```


# Databases

## Raw requests database

This database contains every single
``request`` received and sent by the ``client``.
When stored, these requests looks like this:

```json
{
  "requests": {
    "request_id": {
      ...request_structure...
    }
  }
}
```

## Conversations database

\
Note that this key is only used to encrypt and 
decrypt ``message`` for network communication.
\
Once we decrypt a ``message`` using a negotiated AES key, 
we encrypt it with our own AES key and store it.
\
Therefore, a unique AES key is used to 
encrypt all messages of all conversations.

Note: our own AES key is stored under our ID in the database.

This database contains each ``node``'s 
``conversation`` (``messages`` and AES keys).
``Messages`` are stored in the ``conversations`` table 
and AES keys are stored in the ``keys`` table.
  - The "key" is the 32 bytes key concatenated 
    with the 16 bytes nonce (48 bytes in total).
  - Each key is unique to the conversation.
  - Keys are negotiated with an asynchronous handshake.
    More on that in the ``Keys Exchange Protocol`` section.

The database is structured as follows:

```json
{
  "conversations": {
    "node_identifier": {
      "message_identifier": {
        "content": "aes_encrypted_message",
        "meta": {
          "time_sent": "123456780",
          "time_received": "123456789",
          "digest": "hash_digest",
          "id": "identifier"
        }
      }
    }
  },
  "keys": {
    "node_identifier": {
      "key": "aes_key",
      "status": "DONE | IN_PROGRESS",
      "timestamp": "123456789"
    }
  }
}
```

## Contacts database

This database holds information 
about all the ``contacts`` we know.

The database is structured as follows:

```json
{
  "contacts": {
    "contact_identifier": {
      "address": "address:port",
      "last_seen": "timestamp"
    }
  }
}
```
