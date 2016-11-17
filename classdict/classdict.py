

from .toplevel import to_dict, from_dict
from .utils import list_members_of
from .errors import *


class ClassDict(object):

    def __init__(self, **kwargs):
        members = list_members_of(self.__class__)

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

    @staticmethod
    def is_classdict(cls):
        return issubclass(cls, ClassDict)

    def to_dict(self):
        members = list_members_of(self.__class__)
        result = {}
        for member_name, member_value in members:
            stored_value = getattr(self, member_name)
            if stored_value is not None:
                member_value.validate(stored_value)
                blob = member_value.to_dict(stored_value)
                result[member_name] = blob
        return result

    @classmethod
    def from_dict(cls, dict_like_object):
        members = list_members_of(cls)
        kwargs = {}

        for member_name, member_value in members:
            if member_name in dict_like_object:
                blob_value = dict_like_object[member_name]
                value = from_dict(member_value, blob_value)
                member_value.validate(value)
                kwargs[member_name] = value

        return cls(**kwargs)

    def diff(self, other, path=list()):
        differences = []
        for member_name, member_value in list_members_of(self.__class__):
            field_path = path + [member_name]
            field_diff = member_value.diff(
                getattr(self, member_name),
                getattr(other, member_name),
                field_path
            )
            if field_diff is not None:
                differences.append((field_path, field_diff))
        return differences

    def __str__(self):
        values = [
            "{name}={value}".format(
                name=member[0],
                value=repr(getattr(self, member[0]))
            )
            for member in list_members_of(self.__class__)
            ]
        return "{cls}({values})".format(
            cls=self.__class__.__name__,
            values=", ".join(values)
        )

    def __repr__(self):
        return str(self)
