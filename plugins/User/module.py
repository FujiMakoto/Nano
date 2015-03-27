import bcrypt
from .validators import UserValidators
from .exceptions import *
from database import DbSession
from database.models import User as UserModel

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