

from .utils import list_members_of


def to_dict(objdict_instance):
    members = list_members_of(objdict_instance.__class__)
    result = {}
    for member_name, member_value in members:
        stored_value = getattr(objdict_instance, member_name)
        if stored_value is not None:
            member_value.validate(stored_value)
            blob = member_value.to_dict(stored_value)
            result[member_name] = blob
    return result


def from_dict(objdict_class, dict_like_instance):
    members = list_members_of(objdict_class)
    kwargs = {}

    for member_name, member_value in members:
        if member_name in dict_like_instance:
            blob_value = dict_like_instance[member_name]
            value = member_value.from_dict(blob_value)
            member_value.validate(value)
            kwargs[member_name] = value

    return objdict_class(**kwargs)
