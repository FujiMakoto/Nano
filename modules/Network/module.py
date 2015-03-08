from database import DbSession
from database.models import Network as NetworkModel
from .exceptions import *

__author__ = "Makoto Fujikawa"
__copyright__ = "Copyright 2015, Makoto Fujikawa"
__version__ = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Network:
    def __init__(self):
        self.dbs = DbSession()

    def all(self, autojoin_only=True):
        query = self.dbs.query(NetworkModel)

        if autojoin_only:
            query.filter(NetworkModel.autojoin == True)

        return query.all()

    def exists(self, name=None, host=None):
        if name:
            return bool(self.dbs.query(NetworkModel).filter(NetworkModel.name == name).count())

        if host:
            return bool(self.dbs.query(NetworkModel).filter(NetworkModel.host == host).count())

        raise MissingArgumentsError("You must specify either a network name or host to check")

    def get(self, name=None, host=None):
        if name:
            return self.dbs.query(NetworkModel).filter(NetworkModel.name == name).first()

        if host:
            return self.dbs.query(NetworkModel).filter(NetworkModel.host == host).first()

        raise MissingArgumentsError("You must specify either a network name or host to retrieve")

    def create(self, name, host, port=6667, server_password=None, nick="Nano", nick_password=None, has_services=True,
               autojoin=True):
        # Set up a new Network Model
        new_network = NetworkModel(name=name, host=host, port=port, server_password=server_password, nick=nick,
                                   nick_password=nick_password, has_services=has_services, autojoin=autojoin)
        
        # Insert the new network into our database
        self.dbs.add(new_network)
        self.dbs.commit()

        return new_network