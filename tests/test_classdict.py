import unittest


from classdict import *


class Person(ClassDict):
    age = FieldType(expected_type=int)
    name = FieldType(expected_type=str)


class BusinessTag(ClassDict):
    name = FieldType(expected_type=str)


class Business(ClassDict):
    anything = FieldType()
    typed_tags = ListFieldType(expected_type=BusinessTag)
    years_existed = FieldType(required=True)
    owner = EmbeddedFieldType(Person, required=True)


class TestClassDict(unittest.TestCase):

    def test_expected_type(self):
        with self.assertRaises(ValidationError):
            Person(
                age=24,
                name=24.0
            )
        with self.assertRaises(ValidationError):
            Person(
                age="cats",
                name="bob"
            )
        with self.assertRaises(ValidationError):
            Business(
                years_existed="hello",
                owner=24
            )
        with self.assertRaises(ValidationError):
            Business(
                years_existed="hello",
                owner=Person(name="john connor", age=100),
                typed_tags=[BusinessTag(name="future saving"), 42]
            )
        with self.assertRaises(ValidationError):
            Business(
                years_existed="hello",
                owner=Person(name="john connor", age=100),
                typed_tags=24
            )

    def test_required(self):
        with self.assertRaises(RequiredFieldError):
            Business(
                years_existed=10,
            )
        with self.assertRaises(RequiredFieldError):
            Business(
                anything=10,
                owner=Person()
            )

    def test_to_dict(self):
        test_obj = Business(
            years_existed=10,
            anything="42",
            owner=Person(
                age=24,
                name="Bob"
            ),
            typed_tags=[
                BusinessTag(name="successful"),
                BusinessTag(name="etc"),
            ]
        )
        test_objects = [
            ("testing top level to_dict function", to_dict(test_obj)),
            ("testing classmethod to_dict function", test_obj.to_dict())
        ]
        for index, (msg, result) in enumerate(test_objects):
            with self.subTest(msg, i=index):
                self.assertDictEqual(result, dict(
                    years_existed=10,
                    anything="42",
                    owner=dict(
                        age=24,
                        name="Bob"
                    ),
                    typed_tags=[
                        dict(name="successful"),
                        dict(name="etc"),
                    ]
                ))

    def test_from_dict(self):
        blob = dict(
            years_existed=10,
            anything="42",
            owner=dict(
                age=24,
                name="Bob"
            ),
            typed_tags=[
                dict(name="successful"),
                dict(name="etc"),
            ]
        )
        test_objects = [
            ("testing top level from_dict function", from_dict(Business, blob)),
            ("testing classmethod from_dict function", Business.from_dict(blob))
        ]
        for index, (msg, obj) in enumerate(test_objects):
            with self.subTest(msg, i=index):
                self.assertEqual(obj.years_existed, blob["years_existed"])
                self.assertEqual(obj.anything, blob["anything"])
                self.assertEqual(obj.typed_tags[0].name, blob["typed_tags"][0]["name"])
                self.assertEqual(obj.typed_tags[1].name, blob["typed_tags"][1]["name"])
                self.assertEqual(obj.owner.age, blob["owner"]["age"])
                self.assertEqual(obj.owner.name, blob["owner"]["name"])
