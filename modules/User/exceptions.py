class UserAlreadyExistsError(Exception):
    pass


class UserDoesNotExistsError(Exception):
    pass


class RegistrationValidationError(Exception):
    pass


class BadInstantiationError(Exception):
    pass