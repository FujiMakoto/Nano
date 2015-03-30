import bcrypt
from voluptuous import Schema, Required, All, Length, MultipleInvalid
from database import DbSession
from database.models import User as UserModel
from .validator import Validator, ValidationError

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class User:
    def __init__(self, network=None, client_hostmask=None):
        self.dbs = DbSession()
        self.validate = UserValidators()
        self.network = network
        self.client_hostmask = client_hostmask

    def exists(self, email):
        return bool(self.dbs.query(UserModel).filter(UserModel.email == email).count())

    def get(self, email):
        return self.dbs.query(UserModel).filter(UserModel.email == email).first()

    def get_by_id(self, id):
        return self.dbs.query(UserModel).filter(UserModel.id == id).first()

    def create(self, email, nick, password):
        # Hash our supplied password
        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Set up a new User Model
        new_user = UserModel(email=email, nick=nick, password=password)

        # Insert the new user into our database
        self.dbs.add(new_user)
        self.dbs.commit()

    def register(self, email, nick, password):
        # Make sure we instantiated with our network and client host
        if not self.network or not self.client_hostmask:
            raise BadInstantiationError("User must be instantiated with network and client_hostmask to use this method")

        # Validate our user input
        self.validate.registration(email=email, nick=nick, password=password)

        # Make sure an account with this e-mail doesn't already exist
        if self.exists(email):
            raise UserAlreadyExistsError("An account with this e-mail address already exists")

        # Process the registration request
        self.create(email, nick, password)


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


# Exceptions
class UserAlreadyExistsError(Exception):
    pass


class UserDoesNotExistsError(Exception):
    pass


class RegistrationValidationError(Exception):
    pass


class BadInstantiationError(Exception):
    pass