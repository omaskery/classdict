classdict
=======================

This is a silly little library for serialising and deserialising python objects
to and from dictionaries, due to how prevalent dictionary-based serialisation
is (see json, msgpack, mongodb, etc). Rather than having various libraries
converting from python objects to json/msgpack/mongodb, why not just transfer
into dictionaries which can be passed-to/read-from them all?

Probably lots of good reasons, but I've made this library anyway!

