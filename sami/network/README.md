# Implementing a new protocol

## Choosing a name for your protocol

Notes: 
- By "full name" or "name", we refer to the full protocol name, e.g.
  *Broadcast Contact Protocol*
- By "status", we refer to the acronym of the full name, e.g., *BCP*


### Conventions for defining a protocol name
- Protocol names are usually three words long, e.g., *Broadcast Contact Protocol*
- Protocol names always end with *Protocol*
- The acronym used as status should be 3 characters long, 
  representing the first letters of the full name
- Exceptions on this last rule can be made for "sub-requests", for example with
  the *What's Up Protocol*, which has sub-functionalities *INI* and *REP*.
  In this case, we split the two parts with an underscore.

### Your TODO

For this example, let's say you want to create the *Super Cool Protocol*.

Here is your todo list:
1. Create a new file with the status name, i.e. `SCP.py` in the directory 
  `network/requests/`
2. Construct the content of this file as explained in `network/requests/README.md`
3. Create a new structure by following the guide at `structures/README.md`
4. Implement your logic in `network/_network.py`