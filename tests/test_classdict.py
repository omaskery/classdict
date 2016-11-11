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


class RpcMethod(ClassDict):
    args = TupleFieldType(Person, Business, required=True)


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

    def test_optional(self):
        person = Person(name="Bob")
        d = person.to_dict()
        self.assertEqual(d["name"], "Bob")
        self.assertTrue('age' not in d.keys())

        person_again = Person.from_dict(d)
        self.assertEqual(person_again.name, "Bob")
        self.assertIsNone(person_again.age)

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

    def test_tuples(self):
        test_obj = RpcMethod(args=(
            Person(name="Kate", age=30),
            Business(owner=Person(name="Eve", age=40), years_existed=20)
        ))
        d = test_obj.to_dict()
        self.assertDictEqual(d, dict(
            args=(
                dict(name="Kate", age=30),
                dict(owner=dict(name="Eve", age=40), years_existed=20)
            )
        ))
        obj_again = RpcMethod.from_dict(d)
        self.assertEqual(test_obj.args[0].name, obj_again.args[0].name)
        self.assertEqual(test_obj.args[0].age, obj_again.args[0].age)
        self.assertEqual(test_obj.args[1].years_existed, obj_again.args[1].years_existed)
        self.assertEqual(test_obj.args[1].owner.name, obj_again.args[1].owner.name)
        self.assertEqual(test_obj.args[1].owner.age, obj_again.args[1].owner.age)

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
