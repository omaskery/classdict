import inspect


def list_members_of(objdict_class):
    return (
        member
        for member in
        inspect.getmembers(objdict_class, lambda a: not(inspect.isroutine(a)))
        if not member[0].startswith("__") and not member[0].endswith("__")
    )
