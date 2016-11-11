from classdict import *


class Person(ClassDict):
    name = FieldType(expected_type=str, required=True)
    age = FieldType(expected_type=int)


class Business(ClassDict):
    name = FieldType(expected_type=str, required=True)
    owner = EmbeddedFieldType(Person, required=True)


owner = Person(name="Bob", age=999)
business = Business(name="Fake Company Inc.", owner=owner)


some_dict = business.to_dict()
print(some_dict)
# some_dict == {
#   "name": "Fake Company Inc.",
#   "owner": {
#     "name": "Bob",
#     "age": 999
#   }
# }


result = Business.from_dict(some_dict)
print(result)
# result should now be equivalent to business
