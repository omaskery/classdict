
# Overview

This library allows for quickly defining objects in Python that can be
converted to/from python dict objects. This allows objects to be passed easily
to json, msgpack, mongodb drivers, etc.

This is a small library that is probably silly and has probably been done
1000+ times already,
but a brief amount of googling couldn't find what I needed - so I made it!

# Usage

See the tests for more examples of expected usage/behaviour, but a brief
example is:


```python
from objdict import *

class Person(ObjDict):
	name = FieldType(expected_type=str, required=True)
	age = FieldType(expected_type=int)

class Business(ObjDict):
	name = FieldType(expected_type=str, required=True)
	owner = EmbeddedFieldType(Person, required=True)

owner = Person(name="Bob", age=999)
business = Business(name="Fake Company Inc.", owner=owner)

some_dict = to_blob(business)
# some_dict == {
#   "name": "Fake Company Inc.",
#   "owner": {
#     "name": "Bob",
#     "age": 999
#   }
# }

result = from_blob(Business, some_dict)
# result should now be equivalent to business
```
