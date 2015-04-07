import bcrypt
from voluptuous import Schema, Required, Optional, All, Length
from database import DbSession
from database.models import User as UserModel
from .validator import Validator


class User:
    """
    Register, validate, modify delete and retrieve User accounts from the database
    """
    # Attributes
    EMAIL = "email"
    PASSWORD = "password"
    NICK = "nick"
    IS_ADMIN = "is_admin"

    validAttributes = [EMAIL, PASSWORD, NICK, IS_ADMIN]

    def __init__(self):
        """
        Initialize a new User instance
        """
        self.dbs = DbSession()
        self.validate = UserValidators()

    def all(self):
        """
        Returns a list of all registered users

        Returns:
            list or None
        """
        return self.dbs.query(UserModel).all()

    def exists(self, email):
        """
        Check whether a user by the specified email exists

        Args:
            email(str): The email address to lookup

        Returns:
            bool
        """
        return bool(self.dbs.query(UserModel).filter(UserModel.email == email).count())

    def get(self, email):
        """
        Retrieve a user by their email / login

        Args:
            email(str): The users login / email address

        Returns:
            database.models.User
        """
        user = self.dbs.query(UserModel).filter(UserModel.email == email).first()

        if not user:
            raise UserNotFoundError

        return user

    def get_by_id(self, db_id):
        """
        Retrieve a user by their database ID

        Args:
            db_id(int): The database ID of the user

        Returns:
            database.models.User
        """
        user = self.dbs.query(UserModel).filter(UserModel.id == db_id).first()

        if not user:
            raise UserNotFoundError

        return user

    def create(self, email, nick, password, **kwargs):
        """
        Create a new user account

        Args:
            email(str): The users login / email address
            nick(str): The users nickname / display name
            password(str): The users password
        """
        # Set arguments
        kwargs = dict(email=email, nick=nick, password=password, **kwargs)
        kwargs = dict((key, value) for key, value in kwargs.items() if value)

        # Validate our user input
        self.validate.registration(**kwargs)

        # Make sure an account with this e-mail doesn't already exist
        if self.exists(email):
            raise UserAlreadyExistsError("An account with this e-mail address already exists")

        # Hash our supplied password
        kwargs['password'] = bcrypt.hashpw(kwargs['password'].encode('utf-8'), bcrypt.gensalt())

        # Set up a new User Model
        new_user = UserModel(**kwargs)

        # Insert the new user into our database
        self.dbs.add(new_user)
        self.dbs.commit()

    def remove(self, user):
        """
        Delete an existing user

        Args:
            user(database.models.User): The User to remove
        """
        self.dbs.delete(user)
        self.dbs.commit()


class UserValidators(Validator):
    def __init__(self):
        # Run our parent Validator constructor
        super().__init__()

        # Set our validation rules
        self.rules = {
            'email': All(str, self.Email(), Length(max=255)),
            'nick': All(str, Length(max=50)),
            'password': All(str, Length(min=6, max=1024)),
            'is_admin': All(bool)
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
            Required('password'): self.rules['password'],
            Optional('is_admin'): self.rules['is_admin']
        })

        self.validate(schema, **kwargs)

    def login(self, **kwargs):
        schema = Schema({
            Required('email'): self.rules['email'],
            Required('password'): self.rules['password']
        })

        self.validate(schema, **kwargs)

    def single(self, **kwargs):
        schema = Schema({
            Optional('email'): self.rules['email'],
            Optional('nick'): self.rules['nick'],
            Optional('password'): self.rules['password'],
            Optional('is_admin'): self.rules['is_admin']
        })

        self.validate(schema, **kwargs)


# Exceptions
class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class RegistrationValidationError(Exception):
    pass


class BadInstantiationError(Exception):
    pass