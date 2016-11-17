

def can_become_dict(obj):
    return hasattr(obj, 'to_dict')


def can_consume_dict(cls):
    return hasattr(cls, 'from_dict')


def to_dict(obj):
    if can_become_dict(obj):
        result = obj.to_dict()
    else:
        result = obj
    return result


def from_dict(cls, obj):
    if can_consume_dict(cls):
        result = cls.from_dict(obj)
    else:
        result = obj
    return result

