

class ObjDictError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ValidationError(ObjDictError):
    pass


class RequiredFieldError(ObjDictError):
    pass
