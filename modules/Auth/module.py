from database import DbSession, MemorySession
from database.models import User, UserSession

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
        self.dbs = MemorySession()

    def exists(self, network_id, hostmask):
        """
        Return whether or not an active session currently exists for the specified hostmask

        Args:
            network_id(int): The database ID of the current network
            hostmask(str):   Hostmask the session should be mapped to

        Returns:
            bool
        """
        query = self.dbs.query(UserSession).filter(UserSession.network_id == network_id).filter(
            UserSession.hostmask == hostmask)

        return bool(query.count())

    def get(self, network_id, hostmask):
        """
        Get the session for this hostmask, if one exists, otherwise return False

        Args:
            network_id(int): The database ID of the current network
            hostmask(str):   Hostmask the session should be mapped to

        Returns:
            database.models.UserSession.UserSession or False
        """
        query = self.dbs.query(UserSession).filter(UserSession.network_id == network_id).filter(
            UserSession.hostmask == hostmask)

        return query.first()

    def get_user_id(self, network_id, hostmask):
        """
        Get the user ID for this hostmask's session, if one exists, otherwise return False

        Args:
            network_id(int): The database ID of the current network
            hostmask(str):   Hostmask the session should be mapped to

        Returns:
            int or False
        """
        session = self.get(network_id, hostmask)

        return int(session.user_id)

    def create(self, user_id, network_id, hostmask, expires=None):
        """
        Create a new user session after successfully authenticating a user

        Args:
            user_id(int):    The database ID of the authenticated user
            network_id(int): The database ID of the current network
            hostmask(str):   Hostmask the session should be mapped to
            expires(DateTime, optional): The date and time this session should expire from inactivity
        """
        user_session = UserSession(user_id=user_id, network_id=network_id, hostmask=hostmask, expires=expires)
        self.dbs.add(user_session)
        self.dbs.commit()

    def destroy(self, user_id=None, network_id=None, hostmask=None):
        """
        Destroy an authenticated users session (if one exists), or clear out ALL active session without any filters

        Args:
            user_id(int, optional):    The database ID of the authenticated user
            network_id(int, optional): The database ID of the current network
            hostmask(str, optional):   Hostmask the session should be mapped to
        """
        # Set up a new user session query
        query = self.dbs.query(UserSession)

        # Which filters are we applying (if any)?
        if user_id:
            query.filter(UserSession.user_id == user_id)
        if network_id:
            query.filter(UserSession.network_id == network_id)
        if hostmask:
            query.filter(UserSession.hostmask == hostmask)

        # Destroy all matched user session entries
        query.delete()
