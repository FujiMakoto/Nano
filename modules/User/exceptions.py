class UserAlreadyAuthenticatedError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class RegistrationValidationError(Exception):
    pass


class BadInstantiationError(Exception):
    pass