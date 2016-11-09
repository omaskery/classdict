import inspect


class FieldType(object):

    def __init__(self, expected_type=None, required=False):
        self.required = required
        self.type = expected_type

    def validate(self, value):
        if self.type is not None and not isinstance(value, self.type):
            raise ObjDictError("got value of unexpected type, expected: {type}".format(type=self.type))

    def to_blob(self, value):
        return value

    def from_blob(self, value):
        return value


class EmbeddedFieldType(FieldType):

    def __init__(self, objdict_class, **kwargs):
        if 'expected_type' not in kwargs:
            kwargs['expected_type'] = objdict_class
        super().__init__(**kwargs)
        self._class = objdict_class

    def to_blob(self, value):
        return to_blob(value)

    def from_blob(self, value):
        return from_blob(self._class, value)


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
            if member_name not in kwargs:
                if member_value.required:
                    raise ObjDictError(
                        "{member} is required but not passed to constructor".format(
                            member=member_name
                        )
                    )
                provided_value = None
            else:
                provided_value = kwargs[member_name]

            member_value.validate(provided_value)
            setattr(self, member_name, provided_value)


def to_blob(objdict_instance):
    members = _list_members_of(objdict_instance.__class__)
    result = {}
    for member_name, member_value in members:
        stored_value = getattr(objdict_instance, member_name)
        member_value.validate(stored_value)
        blob = member_value.to_blob(stored_value)
        result[member_name] = blob
    return result


def from_blob(objdict_class, dict_like_instance):
    members = _list_members_of(objdict_class)
    kwargs = {}

    for member_name, member_value in members:
        if member_name in dict_like_instance:
            blob_value = dict_like_instance[member_name]
            value = member_value.from_blob(blob_value)
            member_value.validate(value)
            kwargs[member_name] = value

    return objdict_class(**kwargs)


class ObjDictError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


__all__ = [
    "ObjDictError",
    "from_blob",
    "to_blob",
    "ClassDict",
    "FieldType",
    "EmbeddedFieldType",
]