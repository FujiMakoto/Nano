from database import DbSession
from database.models import Network as NetworkModel
from .exceptions import *

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Network:
    """
    Create, modify, delete and retrieve IRC Networks from the database
    """
    def __init__(self):
        """
        Initialize a new Network instance
        """
        self.dbs = DbSession()

    def all(self, autojoin_only=True):
        """
        Return networks we should automatically join by default, or all networks when autojoin_only is False

        Args:
            autojoin_only(bool, optional): Return only the networks we should autojoin on startup. Defaults to True

        Returns:
            list
        """
        query = self.dbs.query(NetworkModel)

        if autojoin_only:
            query.filter(NetworkModel.autojoin == True)

        return query.all()

    def exists(self, name=None, host=None):
        """
        Check whether a network by the specified name -OR- host exists

        Args:
            name(str, optional): The name/alias for the network
            host(str, optional): The networks host

        Returns:
            bool

        Raises:
            MissingArgumentsError: Neither the network name or host were passed as arguments
        """
        if name:
            return bool(self.dbs.query(NetworkModel).filter(NetworkModel.name == name).count())

        if host:
            return bool(self.dbs.query(NetworkModel).filter(NetworkModel.host == host).count())

        raise MissingArgumentsError("You must specify either a network name or host to check")

    def get(self, name=None, host=None):
        """
        Retrieve a network by its name or host

        Args:
            name(str, optional): The name/alias for the network
            host(str, optional): The networks host

        Returns:
            database.models.Network

        Raises:
            MissingArgumentsError: Neither the network name or host were passed as arguments
        """
        if name:
            return self.dbs.query(NetworkModel).filter(NetworkModel.name == name).first()

        if host:
            return self.dbs.query(NetworkModel).filter(NetworkModel.host == host).first()

        raise MissingArgumentsError("You must specify either a network name or host to retrieve")

    def create(self, name, host, port=6667, server_password=None, nick=None, user_password=None, has_services=True,
               autojoin=True):
        """
        Create a new network

        Args:
            name(str): The name/alias for the network
            host(str): The host to connect to
            port(int, optional): The port number to connect to. Defaults to 6667
            server_password(str, optional): The server password (if required). Defaults to None
            nick(str, optional): A custom IRC nick to use on this server. Defaults to None
            nick_password(str, optional): The password used to identify to network services. Defaults to None
            has_services(bool, optional): Whether or not the network has a services engine. Defaults to True
            autojoin(bool, optional): Should we automatically join this network on startup? Defaults to True

        Returns:
            database.models.Network
        """
        # Set up a new Network Model
        new_network = NetworkModel(name=name, host=host, port=port, server_password=server_password, nick=nick,
                                   user_password=user_password, has_services=has_services, autojoin=autojoin)

        # Insert the new network into our database
        self.dbs.add(new_network)
        self.dbs.commit()

        return new_network