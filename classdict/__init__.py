import inspect


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
        return value

    def from_dict(self, value):
        return value


class EmbeddedFieldType(FieldType):

    def __init__(self, objdict_class, **kwargs):
        if 'expected_type' not in kwargs:
            kwargs['expected_type'] = objdict_class
        super().__init__(**kwargs)
        self._class = objdict_class

    def to_dict(self, value):
        return to_dict(value)

    def from_dict(self, value):
        return from_dict(self._class, value)


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


def _list_members_of(objdict_class):
    return (
        member
        for member in
        inspect.getmembers(objdict_class, lambda a: not(inspect.isroutine(a)))
        if not member[0].startswith("__") and not member[0].endswith("__")
    )


class ClassDict(object):

    def __init__(self, **kwargs):
        members = _list_members_of(self.__class__)

        for member_name, member_value in members:
            member_value.set_name(member_name)
            if member_name not in kwargs:
                if member_value.required:
                    raise RequiredFieldError(
                        "{member} is required but not passed to constructor".format(
                            member=member_name
                        )
                    )
                provided_value = None
            else:
                provided_value = kwargs[member_name]
                member_value.validate(provided_value)

            setattr(self, member_name, provided_value)

    def to_dict(self):
        return to_dict(self)

    @classmethod
    def from_dict(cls, dict_like_object):
        return from_dict(cls, dict_like_object)

    def __str__(self):
        values = [
            "{name}={value}".format(
                name=member[0],
                value=repr(getattr(self, member[0]))
            )
            for member in _list_members_of(self.__class__)
        ]
        return "{cls}({values})".format(
            cls=self.__class__.__name__,
            values=", ".join(values)
        )

    def __repr__(self):
        return str(self)


def to_dict(objdict_instance):
    members = _list_members_of(objdict_instance.__class__)
    result = {}
    for member_name, member_value in members:
        stored_value = getattr(objdict_instance, member_name)
        if stored_value is not None:
            member_value.validate(stored_value)
            blob = member_value.to_dict(stored_value)
            result[member_name] = blob
    return result


def from_dict(objdict_class, dict_like_instance):
    members = _list_members_of(objdict_class)
    kwargs = {}

    for member_name, member_value in members:
        if member_name in dict_like_instance:
            blob_value = dict_like_instance[member_name]
            value = member_value.from_dict(blob_value)
            member_value.validate(value)
            kwargs[member_name] = value

    return objdict_class(**kwargs)


class ObjDictError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ValidationError(ObjDictError):
    pass


class RequiredFieldError(ObjDictError):
    pass


__all__ = [
    "ObjDictError",
    "ValidationError",
    "RequiredFieldError",
    "from_dict",
    "to_dict",
    "ClassDict",
    "FieldType",
    "EmbeddedFieldType",
    "ListFieldType",
    "TupleFieldType",
]