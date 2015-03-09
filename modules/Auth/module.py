import bcrypt
from database import DbSession, MemorySession
from database.models import UserSession
from .exceptions import *
from ..User.exceptions import UserDoesNotExistsError
from ..User import User

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class AuthSession:
    """
    Validates, creates and destroys user login sessions
    """
    def __init__(self):
        """
        Initialize a new Auth Sessions instance
        """
        self.dms = MemorySession()

    def attempt(self, email, password, hostmask, network):
        """
        Attempt to log a user in with the supplied credentials

        Args:
            email(str): Account login/email address
            password(str): Password being attempted
            hostmask(str): The hostmask of the authenticating client
            network(database.models.Network): The network we are authenticating on

        Returns:
            database.models.AuthSession

        Raises:
            AlreadyAuthenticatedError: The user is already logged in to an existing account
            UserDoesNotExistsError: The account we are attempting to authenticate to does not exist
            InvalidPasswordError: The account we are attempting to authenticate to exists, but our password is invalid
        """
        # Make sure we're not already logged in
        if self.exists(network, hostmask):
            raise AlreadyAuthenticatedError("Cannot authenticate a user with an existing active login session")

        # Retrieve the user we are attempting to authenticate as
        user = User().get(email)

        # Make sure the user exists
        if not user:
            raise UserDoesNotExistsError("Attempted to authenticate as a non-existing user")

        # Check our password
        password = password.encode('utf-8')
        valid_login = bcrypt.hashpw(password, user.password) == user.password

        if not valid_login:
            raise InvalidPasswordError("The supplied password did not match")

        # Create a new login session
        return self.create(user, network, hostmask)

    def exists(self, network, hostmask):
        """
        Return whether or not an active session currently exists for the specified hostmask

        Args:
            network(database.models.Network): The database ID of the current network
            hostmask(str): Hostmask the session should be mapped to

        Returns:
            bool
        """
        query = self.dms.query(UserSession).filter(UserSession.network_id == network.id).filter(
            UserSession.hostmask == hostmask)

        return bool(query.count())

    def get(self, network, hostmask):
        """
        Get the session for this hostmask, if one exists, otherwise return False

        Args:
            network(database.models.Network): The database ID of the current network
            hostmask(str): Hostmask the session should be mapped to

        Returns:
            database.models.UserSession.UserSession or False
        """
        query = self.dms.query(UserSession).filter(UserSession.network_id == network.id).filter(
            UserSession.hostmask == hostmask)

        return query.first()

    def get_user_id(self, network, hostmask):
        """
        Get the user ID for this hostmask's session, if one exists, otherwise return False

        Args:
            network(database.models.Network): The database ID of the current network
            hostmask(str): Hostmask the session should be mapped to

        Returns:
            int or False
        """
        session = self.get(network, hostmask)

        return int(session.user_id)

    def create(self, user, network, hostmask, expires=None):
        """
        Create a new user session after successfully authenticating a user

        Args:
            user(database.models.User): The database ID of the authenticated user
            network(database.models.Network): The database ID of the current network
            hostmask(str): Hostmask the session should be mapped to
            expires(DateTime, optional): The date and time this session should expire from inactivity
        """
        user_session = UserSession(user_id=user.id, network_id=network.id, hostmask=hostmask, expires=expires)
        self.dms.add(user_session)
        self.dms.commit()
        return user_session

    def destroy(self, user=None, network=None, hostmask=None):
        """
        Destroy an authenticated users session (if one exists), or clear out ALL active session without any filters

        Args:
            user(database.models.User, optional): The database ID of the authenticated user
            network(int, optional): The database ID of the current network
            hostmask(str, optional):   Hostmask the session should be mapped to
        """
        # Set up a new user session query
        query = self.dms.query(UserSession)

        # Which filters are we applying (if any)?
        if user:
            query.filter(UserSession.user_id == user.id)
        if network:
            query.filter(UserSession.network_id == network.id)
        if hostmask:
            query.filter(UserSession.hostmask == hostmask)

        # Destroy all matched user session entries
        query.delete()
