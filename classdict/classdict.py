

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
            for member in list_members_of(self.__class__)
            ]
        return "{cls}({values})".format(
            cls=self.__class__.__name__,
            values=", ".join(values)
        )

    def __repr__(self):
        return str(self)
