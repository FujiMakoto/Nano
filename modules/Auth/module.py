import bcrypt
from database import MemorySession
from database.models import UserSession
from .exceptions import *
from ..User.exceptions import UserDoesNotExistsError
from ..User import User

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Auth:
    def __init__(self):
        """
        Initialize a new Auth instance
        """
        self.session = AuthSession()

    def check(self, hostmask, network):
        """
        Check whether or not the specified host is authenticated

        Args:
            network(database.models.Network): The network we are checking
            hostmask(str): The hostmask we are checking

        Returns:
            bool
        """
        return self.session.exists(network, hostmask)

    def user(self, hostmask, network):
        """
        Retrieve the authenticated user

        Args:
            hostmask(str): The hostmask of the authenticated client
            network(database.models.Network): The network we are authenticated on

        Returns:
            database.models.User

        Raises:
            NotAuthenticatedError: No login session exists for this host on this network
        """
        # Retrieve our session and make sure we're actually logged in
        user_session = self.session.get(network, hostmask)
        if not user_session:
            raise NotAuthenticatedError("Host not authenticated, no user to retrieve")

        # Return the user associated with this login session
        return User().get_by_id(user_session.user_id)

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
        if self.session.exists(network, hostmask):
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
        return self.session.create(user, network, hostmask)

    def login(self, email, hostmask, network):
        """
        Login as the supplied user

        Args:
            email(str): Account login/email address
            hostmask(str): The hostmask of the client to authenticate
            network(database.models.Network): The network we are authenticating on

        Raises:
            UserDoesNotExistsError: The account we are attempting to login as doesn't exist
        """
        # Retrieve the user we are attempting to log in as
        user = User().get(email)

        # Make sure the user exists
        if not user:
            raise UserDoesNotExistsError("Attempted to login as a non-existing user")

        return self.session.create(user, network, hostmask)

    def logout(self, hostmask, network):
        """
        Destroy an existing login session

        Args:
            hostmask(str): The hostmask of the authenticated client
            network(database.models.Network): The network we are logging out on

        Raises:
            NotAuthenticatedError: No login session exists for this host on this network
        """
        # Make sure we're actually logged in
        if not self.session.exists(network, hostmask):
            raise NotAuthenticatedError("Attempted to logout when we ware not logged in")

        # Destroy this hosts login session
        self.session.destroy(network=network, hostmask=hostmask)


class AuthSession:
    """
    Validates, creates and destroys user login sessions
    """
    def __init__(self):
        """
        Initialize a new Auth Sessions instance
        """
        self.dms = MemorySession()

    def exists(self, network, hostmask):
        """
        Return whether or not an active session currently exists for the specified hostmask

        Args:
            network(database.models.Network): The network we are checking
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
            network(database.models.Network): The network we are retrieving a session from
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
            network(database.models.Network): The network we are retrieving a session from
            hostmask(str): Hostmask the session should be mapped to

        Returns:
            int or False
        """
        session = self.get(network, hostmask)

        if not session:
            return False

        return int(session.user_id)

    def create(self, user, network, hostmask, expires=None):
        """
        Create a new user session after successfully authenticating a user

        Args:
            user(database.models.User): The authenticated user
            network(database.models.Network): The network we are authenticating on
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
            user(database.models.User, optional): The authenticated user
            network(int, optional): The network we are destroying a session out on
            hostmask(str, optional): Hostmask the session should be mapped to
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
