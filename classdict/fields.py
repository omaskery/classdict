

from .toplevel import to_dict, from_dict, can_consume_dict, can_become_dict
from .errors import *


class FieldType(object):

    def __init__(self, expected_type=None, required=False):
        self.required = required
        self.type = expected_type
        self._name = None

    def set_name(self, name):
        self._name = name

    def validate(self, value):
        if value is None and self.required:
            raise RequiredFieldError(
                "field {name} absent but is required".format(
                    name=self._name
                )
            )
        if self.type is not None and value is not None and not isinstance(value, self.type):
            raise ValidationError(
                "field {name} got value of unexpected type {got}, expected: {type}".format(
                    got=type(value),
                    name=self._name,
                    type=self.type
                )
            )

    def to_dict(self, value):
        return to_dict(value)

    def from_dict(self, value):
        return from_dict(self.type, value)


class EmbeddedFieldType(FieldType):

    def __init__(self, objdict_class, **kwargs):
        if 'expected_type' not in kwargs:
            kwargs['expected_type'] = objdict_class
        super().__init__(**kwargs)
        self._class = objdict_class


class ListFieldType(FieldType):

    def validate(self, value):
        if not isinstance(value, list):
            raise ValidationError(
                "field {name} got value of unexpected type {got}, expected a list of {type}".format(
                    got=type(value),
                    name=self._name,
                    type=self.type
                )
            )
        list(map(super().validate, value))

    def to_dict(self, value):
        return list(map(to_dict, value))

    def from_dict(self, value):
        return list(map(lambda x: from_dict(self.type, x), value))


class TupleFieldType(FieldType):

    def __init__(self, *args, **kwargs):
        if 'expected_type' in kwargs:
            raise ObjDictError("expected type is not compatible with TupleFieldType, specify element types as *args")
        kwargs['expected_type'] = args
        super().__init__(**kwargs)

    def validate(self, value):
        if not isinstance(value, (tuple, list)):
            raise ValidationError(
                "field {name} got value of unexpected type {got}, expected a tuple of types ({type})".format(
                    name=self._name,
                    got=type(value),
                    type=", ".join(map(str, self.type))
                )
            )
        if len(value) != len(self.type):
            raise ValidationError(
                "field {name} expected a tuple of length {len}, got tuple of length {got}".format(
                    name=self._name,
                    len=len(self.type),
                    got=len(value)
                )
            )
        for index, (expected, got) in enumerate(zip(self.type, value)):
            if not isinstance(got, expected):
                raise ValidationError("field {name} expected element {nth} to be {type}, got type {got}".format(
                    name=self._name,
                    nth=index,
                    type=expected,
                    got=type(got)
                ))

    def to_dict(self, value):
        return tuple(map(to_dict, value))

    def from_dict(self, value):
        return tuple([
                         cls.from_dict(element)
                         for element, cls in zip(value, self.type)
                         ])

