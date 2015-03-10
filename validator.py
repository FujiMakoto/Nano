import re
from voluptuous import MultipleInvalid, Invalid

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Validator:
    def __init__(self):
        self.rules = {}
        self.messages = {}

    def validate(self, schema, **kwargs):
        input = {}
        if kwargs is not None:
            for key, value in kwargs.items():
                input[key] = value

        try:
            schema(input)
        except MultipleInvalid as e:
            raise ValidationError(str(e), e.path[0], self.messages)

    # noinspection PyPep8Naming
    def Email(msg=None):
        """
        Validate whether or not the input contains a valid e-mail address
        """
        def validate(msg=None):
            msg = str(msg)
            if re.match("[\w\.\-_\+]*@[\w\.\-_\+]*\.\w+", msg):
                return msg
            else:
                raise Invalid(msg or "Incorrect email address")
        return validate


class ValidationError(Exception):
    def __init__(self, message, path, error_messages=None):
        # Call the base class constructor with the parameters it needs
        super(ValidationError, self).__init__(message)

        # Define our custom exception parameters
        self.path = path
        self.error_message = "Invalid input provided."

        # Apply any custom error messages
        if isinstance(error_messages, dict):
            for key, message in error_messages.items():
                if key == path:
                    self.error_message = message
                    break