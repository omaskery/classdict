import unittest


import objdict


class SubTestObj(objdict.ObjDict):
    age = objdict.FieldType(expected_type=int)
    name = objdict.FieldType(expected_type=str)


class TestObj(objdict.ObjDict):
    some_value = objdict.FieldType()
    some_required_value = objdict.FieldType(required=True)
    some_sub_object = objdict.EmbeddedFieldType(SubTestObj, required=True)


class TestObjdict(unittest.TestCase):

    def test_expected_type(self):
        with self.assertRaises(objdict.ObjDictError):
            SubTestObj(
                age=24,
                name=24.0
            )
        with self.assertRaises(objdict.ObjDictError):
            SubTestObj(
                age="cats",
                name="bob"
            )
        with self.assertRaises(objdict.ObjDictError):
            TestObj(
                some_required_value="hello",
                some_sub_object=24
            )

    def test_required(self):
        with self.assertRaises(objdict.ObjDictError):
            TestObj(
                some_value=10,
                some_required_value="42"
            )
        with self.assertRaises(objdict.ObjDictError):
            TestObj(
                some_value=10,
                some_sub_object=SubTestObj()
            )

    def test_to_blob(self):
        test_obj = TestObj(
            some_value=10,
            some_required_value="42",
            some_sub_object=SubTestObj(
                age=24,
                name="Bob"
            )
        )
        result = objdict.to_blob(test_obj)
        self.assertDictEqual(result, dict(
            some_value=10,
            some_required_value="42",
            some_sub_object=dict(
                age=24,
                name="Bob"
            )
        ))

    def test_from_blob(self):
        blob = dict(
            some_value=10,
            some_required_value="42",
            some_sub_object=dict(
                age=24,
                name="Bob"
            )
        )
        obj = objdict.from_blob(TestObj, blob)
        self.assertEqual(obj.some_value, blob["some_value"])
        self.assertEqual(obj.some_required_value, blob["some_required_value"])
        self.assertEqual(obj.some_sub_object.age, blob["some_sub_object"]["age"])
        self.assertEqual(obj.some_sub_object.name, blob["some_sub_object"]["name"])
