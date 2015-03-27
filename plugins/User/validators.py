from voluptuous import Schema, Required, All, Length, MultipleInvalid
from src.validator import Validator, ValidationError

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class UserValidators(Validator):
    def __init__(self):
        # Run our parent Validator constructor
        super().__init__()

        # Set our validation rules
        self.rules = {
            'email': All(str, self.Email(), Length(max=255)),
            'nick': All(str, Length(max=50)),
            'password': All(str, Length(min=6, max=1024))
        }

        # Set our validation messages
        self.messages = {
            'email': "The e-mail you provided does not appear to be valid. Please check your input and try again.",
            'nick': "The nick you provided does not appear to be valid. Nicks may only contain alphanumeric characters."
                    " Please check your input and try again.",
            'password': "The password you provided does not appear to be valid. Passwords must be at least"
                        " 6 characters in length. Please check your input and try again."
        }

    def registration(self, **kwargs):
        schema = Schema({
            Required('email'): self.rules['email'],
            Required('nick'): self.rules['nick'],
            Required('password'): self.rules['password']
        })

        self.validate(schema, **kwargs)

    def login(self, **kwargs):
        schema = Schema({
            Required('email'): self.rules['email'],
            Required('password'): self.rules['password']
        })

        self.validate(schema, **kwargs)