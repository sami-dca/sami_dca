# Introduction

**Sami** is a decentralized communication application.
\
It currently allows for textual messages exchange.
\
The network created by users is decentralized, meaning no one controls it.

It is mainly inspired from [Ethereum Whisper](https://geth.ethereum.org/docs/whisper/how-to-whisper),
the [Scuttlebutt protocol](https://ssbc.github.io/scuttlebutt-protocol-guide/) and
[Jami](https://www.jami.net).

While the network is very resilient at medium and large scale, 
there can be some unexpected errors and problems at a very small scale (only a few users).
\
Usually, the larger the network, the better.

# Keys and identities

The first thing a user needs to participate in the Sami network is an identity.
\
An identity is referred to as a ``node`` and is a RSA key pair (a public key and a private key). 
\
It typically represents a person or a bot.
\
It is normal for a person to have several identities.

Because identities are long and random, no coordination or permission is required to create a new one,
which is essential to the network’s design.

A name is generated from the user's RSA keys, giving it a human-readable identifier.

If a user loses their secret key or has it stolen, they will need to generate a new identity.

The public key of a ``node`` is presented to users and transmitted in some network protocols, 
as we'll see later on in this document.

## Dark network

Sami adopts a "dark network" architecture.

This means that, by design, a ``node`` (an identity on the Sami P2P network) 
and a ``contact`` (an IP address) cannot be linked together while the Sami network maintains a consensus.

# Attacks

In this section, we'll have a look at a few common attacks, as well as Sami-specific known attacks.

## Sybil attacks

In a Sybil attack, an attacker takes over the network by creating numerous identities.  
Here, two situations apply:

### Node takeover

By *node takeover*, we mean that an attacker overloads the P2P network with Sami identities.

This simply has no effect on the network.

### Contact takeover

On the other hand, *contact takeover* can be a problem.
This is because while a ``node`` is a virtual identity, a ``contact`` is a physical identity.

Therefore, in the attacks we'll see further on, we'll talk about *contact takeover* and not *node takeover*.

## 51% attacks

A 51% attack refers to an attack on a decentralized network by a 
group of attackers controlling more than 50% of the network.

This type of attacks is not applicable to the Sami network.

There are two possible ways of seeing the situation:

### Configuration corruption

In this case, a group of attackers modifies their clients' configuration to one that is insecure or dangerous.  
If that ever happens, a different network will emerge from the usual users' - what we call a fork.  
This is due to the fact that Sami clients are very rigid regarding other nodes' configuration, 
and will discard any malformed request.

### Attackers consensus

If a group of seemingly normal users join a network but are controller by attackers, 
there is next to nothing they will be able to do, unless the network is very small, 
in which case the dark network architecture can be endangered.

To avoid this kind of situation, there is a built-in threshold of contacts one 
must know before starting to send identifying requests.  
However, this preemptive measure will not be enough if 49 out of 50 clients are controlled by a bad actor !

A simple measure against this type of attack is simply to have a group of normal users on the network.  
They don't even need to add up to 50% of the network or more ; as long as there is a dozen of them, 
it becomes unfeasible to identify each one.

## Flooding attacks

Flooding attacks consist of flooding the network with requests.  
At the moment, no solution is implemented, but is being actively worked on.

The easy way out would be to implement proof-of-work, and while it is very efficient pre-quantum,
it has terrible effects on power consumption, and therefore global environment (*ya know, global warming and all*).

## Deny attacks

A deny attack consists, for an attacker, to not forward any or part of the requests.  
It is pretty hard to find out whether a client denies requests, and the effects of this attack can be various.

No solution is yet implemented.

However, a simple counter-measure is simply to have a significant part of good users on the P2P network.

### And many more attacks yet to be documented...

# Terms

## Client

A ``client`` is an instance of the Sami software, and an individual on the network.  
One ``client`` can host multiple ``nodes`` (identities), while not at the same time.  
It is a relay on the network, and is accessible via its ``contact`` information.

It can also be referred to as a ``peer`` later in this paper.

## Node

### Node

A ``node`` is a person on the network, and is identified by an RSA public key.

Note: Two values are derived from this key (modulus ``n`` and public exponent ``e``):
  - Its ID ; which length is defined by the config attribute ``id_len``.
  - Its name ; a series of words picked from the file ``sami/lib/dictionary``.

Its structure is defined as:

    {
      "rsa_n": "modulus",
      "rsa_e": "public_exponent",
      "hash": "hash_of_the_above_information",
      "sig": "signature_of_the_above_hash"
    }

Sending a ``message`` to a ``node`` is not instantaneous, unlike ``contacts`` communication.

### Master node

A ``master node`` is our own identity.  
Unlike the ``node``, we have its RSA private key.

## Contact

You can see a ``contact`` as a "link" to a ``client`` on the network.  
It is defined by an address (IP or DNS name) and a port:

    {
      "address": "127.0.0.1:1234"
    }

The network design prevents a ``contact`` information to be linked to a ``node`` information.

A communication with a contact is almost instantaneous, unless it is disconnected.

## Messages

A ``message`` is... a... message. I know, shocking !

It carries sensitive information, namely a user-specified value.

A ``message`` ``request`` is structured as follows:

    {
      "content": "aes_encrypted_message",
      "meta": {
        "time_sent": "timestamp",
        "digest": "message_digest"
      },
      "author": ...node_structure...
    }

## Conversation

A ``conversation`` is a list of ``messages`` exchanged with a ``node``.  
We consider that we have a single conversation with a ``node``, 
therefore the ``conversation``'s ID is the same as the ``node``'s ID.  
To exchange encrypted messages (and be able to decrypt them), 
two ``nodes`` must have negotiated an AES key with the *Keys Exchange Protocol* (*KEP*).

# Discovery

After a user has generated its identity, it needs to find some peers to connect to.  
To connect to somebody, you need to know its ``contact`` information (or someone that knows it, and so on).  
The list of discovered ``nodes``will appear in the ``client``'s user interface.

There a several ways to discover a ``node``:

## Beacons

A ``beacon`` is a standard ``client`` that is assured to run at all time.  
They are hard-coded inside the configuration and managed by the project maintainers.  
They can also be added on private networks.

While this goes against the decentralized design, 
it is common use (e.g. Bitcoin), and a good way to discover new ``nodes`` without flooding the network.

## Local network

Once the Sami ``client`` is opened, and if it doesn't know enough ``contacts``,
it will broadcast over the network a specific packet containing its own ``contact`` information, 
while listening for others.  
It will do so regularly (depending on the local configuration).

When a ``client`` sees another’s broadcast packet they will save its ``contact`` information.

# Protocols

All ``requests`` have a common structure:

    {
      "status": "REQUEST_NAME",
      "data": {
        ...information...
      },
      "timestamp": "timestamp"
    }

## What's Up Protocol - "WUP"

This protocol is used to get all the ``requests`` we missed while we were offline.

### INI

1. We wake up: the user launched his ``client``.
2. We read the ``raw_requests`` database to get the most recent ``time_sent``.
3. We send a ``WUP_INI`` ``request`` (with below structure) to a ``beacon``, otherwise a regular ``node``, 
   with ``timestamp`` being the most recent ``time_sent`` found in the database, 
   and ``author`` being our own ``contact`` information.

        {
          "status": "WUP_INI",
          "data": {
            "timestamp": "timestamp",
            "author": ...contact_structure...
          },
          "timestamp": "timestamp"
        }

### REP

1. We receive a ``WUP_INI`` ``request``.
2. We retrieve all ``requests`` from the ``raw_requests`` database which were sent after ``timestamp``,
   and send each one to the ``contact`` specified.

        {
          "status": "WUP_REP",
          "data": {
            ...request_structure...
          },
          "timestamp": "timestamp"
        }

## Keys Exchange Protocol - "KEP"

This protocol is used when negotiating a new AES key for a new ``conversation``.

This negotiation avoids having one ``node`` in charge of deciding the AES key for both parts.

1. We detect a new ``node`` on the network, or we tried to negotiate a key earlier, but it didn't work, so we try again.
2. We create a random 16 bytes key (precisely, half the AES key length).
3. We send over the network a new *KEP* ``request`` with the below structure:

        {
          "status": "KEP",
          "data": {
            "key": {
              "value": "16_bytes_rsa_encrypted_aes_key",
              "hash": "hash_of_the_encrypted_key",
              "sig": "signature_of_the_above_hash"
            },
            "author": ...node_structure...,
            "recipient": ...node_structure...
          },
          "timestamp": "timestamp"
        }

4. While waiting for the reply, we store our half-key in the conversation database with the status ``IN-PROGRESS``.
5. Once we receive a response to this ``request``, we verify its content and assemble the two keys, 
   then derive a nonce from that shared key.

The other way around:

1. We receive a new *KEP* ``request`` (we did not send one yet).
2. We verify its content.
3. We then generate a new 16 bytes random value, and send it over with the same structure as above.
4. We construct the key and derive the nonce, then we store it.
5. At this point, we have a working key, and so should the recipient.

We never send the full key nor nonce over the network.

If the protocol has been respected by both party, they should have the same key and nonce.

Also, if we don't get any response:

1. We sent our part of the key to the ``node``, but we didn't get any response.
2. If the timestamp is greater than 1 month, we delete the entry from the database.
   If the ``node`` comes back to life, we will have to negotiate a new key.

## Message Propagation Protocol - "MPP".

This protocol is called when a ``message`` is received.
A typical *MPP* ``request`` looks like this:

    {
      "status": "MPP",
      "data": {
        ...message_structure...
      },
      "timestamp": "timestamp"
    }

1. We receive a ``message`` ``request``.
2. We check if we already received that ``request``.
3. If not, we broadcast it.
4. We try to decrypt the content of the message.
5. If we're able to access the decrypted content, we store it in the ``conversations`` database.

## Node Publication Protocol - "NPP"

This protocol is used for sending a ``node`` identity over the network.

1. We receive a *Discover Node* ``request`` (*DNP*).
2. If we know at least `x` ``nodes`` (default is 5), for each one (including ours), 
   we send it back with this structure:

        {
          "status": "NPP",
          "data": {
            ...node_structure...
          },
          "timestamp": "timestamp"
        }

## Contact Sharing Protocol - "CSP"

This protocol is used when we want to share a ``contact`` with a ``peer``.

1. We receive a *Discover Contact* ``request`` (*DCP*).
2. If we know at least `x` ``contacts`` (default is 5), for every contact (including ours), 
   we send the following ``request`` to the author:

        {
          "status": "CSP",
          "data": {
            ...contact_structure...
          },
          "timestamp": "timestamp"
        }

## Broadcast Protocol

This protocol is used for local network broadcasting.

It is constructed as follows:

      {
         "status": "BCP",
         "data": ...contact_structure...,
         "timestamp": "timestamp"
      }

1. When we wake up (the user opens a client), we check if we know enough contacts 
   (set by a configuration variable).
2. If we don't, we broadcast our information on the local network with the above structure.

If we receive one, we simply check if we know the contact, and if we don't, we store its information.

## Discover Nodes Protocol - "DNP"

This ``request`` asks a ``contact`` for a list of ``nodes``.

It is constructed as follows:

    {
      "status": "DNP",
      "data": {
        "author": ...node_structure...
      },
      "timestamp": "timestamp"
    }

It is triggered regularly

## Discover Contacts Protocol - "DCP"

This ``request`` asks for a list of ``contacts`` to a specific ``contact``.

It is constructed as follows:

    {
      "status": "DCP",
      "data": {
        "author": ...node_structure...
      },
      "timestamp": "timestamp"
    }

# Databases

## Raw requests database

This database contains every single ``request`` processed by our ``client``.  
It is not ``node``-encrypted, meaning every identity on a client has access to it.  
When stored, these requests look like this:

    {
      "requests": {
        "request_id": {
          ...request_structure...
        }
      }
    }

## Conversations database

``Messages`` are stored in the database with their respective negotiated AES key.

This database contains each ``node``'s ``conversation`` (``messages`` and AES keys).
``Messages`` are stored in the ``conversations`` table and AES keys are stored in the ``keys`` table.
  - The "key" is the 32 bytes key concatenated with the 16 bytes nonce (48 bytes in total) if the negotiation is done,
    otherwise it is 16 bytes (half the key length)
  - Each key is unique to the conversation.
  - Keys are negotiated with a synchronous handshake. More on that in the ``Keys Exchange Protocol`` section.

The database is structured as follows:

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
            },
            "author": ...node_structure...
          }
        }
      },
      "keys": {
        "node_identifier": {
          "key": "rsa_encrypted_aes_key",
          "status": "DONE | IN_PROGRESS",
          "timestamp": "123456789"
        }
      }
    }

## Nodes database

This database holds information about all the ``nodes`` one knows.

It is not ``node``-encrypted, meaning every identity on a client can have access to it.

It is structured as follows:

    {
      "nodes": {
        "node_identifier": {
          ...node_structure...,
          "last_seen": "timestamp"
        }
      }
    }

## Contacts database

This database holds information about all the ``contacts`` one knows.

It is not ``node``-encrypted, meaning every identity on a client can have access to it.

It is structured as follows:

    {
      "contacts": {
        "contact_identifier": {
          ...contact_structure...,
          "last_seen": "timestamp"
        }
      }
    }
