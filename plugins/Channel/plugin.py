from database import DbSession
from database.models import Channel as ChannelModel

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Channel:
    def __init__(self):
        self.dbs = DbSession()

    def all(self, network=None, autojoin_only=True):
        query = self.dbs.query(ChannelModel)

        if network:
            query.filter(ChannelModel.network == network)

        if autojoin_only:
            query.filter(ChannelModel.autojoin == True)

        return query.all()

    def exists(self, name, network):
        return bool(self.dbs.query(ChannelModel).filter(ChannelModel.name == name).filter(
            ChannelModel.network == network).count())

    def get(self, name, network):
        return self.dbs.query(ChannelModel).filter(ChannelModel.name == name).filter(
            ChannelModel.network == network).first()

    def create(self, network, name, channel_password=None, xop_level=0, manage_topic=False, topic_separator='#',
               topic_mode='STATIC', topic_max=5, log=True, autojoin=True):
        # Set up a new Network Model
        new_channel = ChannelModel(network=network, name=name, channel_password=channel_password, xop_level=xop_level,
                                   manage_topic=manage_topic, topic_separator=topic_separator, topic_mode=topic_mode,
                                   topic_max=topic_max, log=log, autojoin=autojoin)

        # Insert the new network into our database
        self.dbs.add(new_channel)
        self.dbs.commit()

        return new_channel