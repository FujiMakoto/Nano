import logging
from voluptuous import Schema, Required, Optional, All, Length, Range, Match
from database import DbSession
from database.models import Channel as ChannelModel, Network as NetworkModel
from src.validator import Validator


class Channel:
    """
    Create, modify, delete and retrieve IRC Channels from the database
    """
    # Attributes
    NAME = "name"
    CHANNEL_PASS = "channel_password"
    XOP = "xop_level"
    MANAGE_TOPIC = "manage_topic"
    TOPIC_SEP = "topic_separator"
    TOPIC_MODE = "topic_mode"
    TOPIC_MAX = "topic_max"
    LOG = "log"
    AUTOJOIN = "autojoin"

    validAttributes = [NAME, CHANNEL_PASS, XOP, MANAGE_TOPIC, TOPIC_SEP, TOPIC_MODE, TOPIC_MAX, LOG, AUTOJOIN]

    def __init__(self):
        """
        Initialize a new Channel instance
        """
        self.log = logging.getLogger('nano.irc.channel')
        self.dbs = DbSession()
        self.validate = ChannelValidators()

    def all(self, network=None, autojoin_only=True):
        """
        Return channels we should automatically join by default, or all channels when autojoin_only is False

        Args:
            network(database.models.Network or None, optional): The network to return channels for. Defaults to None
            autojoin_only(bool, optional): Return only the channels we should autojoin on startup

        Returns:
            list
        """
        self.log.info('Returning available channels')
        query = self.dbs.query(ChannelModel)

        # Apply filters
        if autojoin_only:
            self.log.debug('Returnng autojoin channels only')
            query.filter(ChannelModel.autojoin == True)
        if network and isinstance(network, NetworkModel):
            self.log.debug('Returning channels only on the network ' + network.name)
            query.filter(ChannelModel.network == network)

        return query.all()

    def exists(self, name, network):
        """
        Check whether a channel by the specified name on the specified network exists

        Args:
            name(str): The name of the channel
            network(database.models.Network or None, optional): The network to search on

        Returns:
            bool
        """
        self.log.info('Checking whether the channel {channel} exists on the network {network}'
                      .format(channel=name, network=network.name))

        return bool(self.dbs.query(ChannelModel).filter(ChannelModel.name == name, ChannelModel.network == network))

    def get(self, db_id=None, name=None, network=None):
        """
        Retrieve a network by its database ID, name and/or network

        Args:
            db_id(int or None, optional): The database ID of the network
            name(str or None, optional): The name of the channel
            network(database.models.Network or None, optional): The network to search on

        Returns:
            database.models.Channel
        """
        query = self.dbs.query(ChannelModel)

        # Make sure at at least one valid filter was set
        if not db_id and not name:
            raise ValueError('A db_id or name value must be supplied')

        # Apply filters
        if db_id:
            query = query.filter(ChannelModel.id == db_id)
        if name:
            query = query.filter(ChannelModel.name == name)
        if network:
            query = query.filter(ChannelModel.network == network)

        # Attempt to fetch the requested channel, or raise a Not Found exception if no results are returned
        channel = query.first()
        if not channel:
            raise ChannelNotFoundException

        return channel

    def create(self, name, network, **kwargs):
        """
        Create a new channel

        Args:
            name(str): The name of the channel
            network(database.models.Network): The network the channel is being assigned to
            channel_password(str, optional): The channel key/password
            xop_level(int): Nano's XOP level (0: Regular, 3: Voiced, 4: Halfop, 5: Operator, 10: Admin, 9999: Owner)
            manage_topic(bool): Whether or not Nano should manage the channels topic
            topic_separator(str): The separator to use for channel topics
            topic_mode(str): The channel topic mode
            topic_max(int): The maximum number of channel topics that can be assigned at once
            log(bool): Whether or not messages to this channel should be logged
            autojoin(bool): Should we automatically join this network on startup?

        Returns:
            database.models.Channel
        """
        # Set arguments
        kwargs = dict(name=name, network=network, **kwargs)
        kwargs = dict((key, value) for key, value in kwargs.items() if value)

        # Validate input
        self.validate.creation(**kwargs)

        # Set up a new Channel Model
        new_channel = ChannelModel(**kwargs)

        # Insert the new channel into our database
        self.dbs.add(new_channel)
        self.dbs.commit()

    def remove(self, channel):
        """
        Delete an existing channel

        Args:
            channel(database.models.Channel): The Channel to remove
        """
        self.dbs.delete(channel)
        self.dbs.commit()


class ChannelValidators(Validator):
    def __init__(self):
        # Run our parent Validator constructor
        super().__init__()

        # Set our validation rules
        self.rules = {
            'name': All(str, Length(max=50), Match(r'^\S+$')),
            'channel_password': All(str, Length(max=255)),
            'xop_level': All(int, Range(-2, 9999)),
            'manage_topic': All(bool),
            'topic_separator': All(str, Length(max=10)),
            'topic_mode': All(str, Length(max=20)),
            'topic_max': All(int, Range(1, 100)),
            'log': All(bool),
            'autojoin': All(bool)
        }

        # Set our validation messages
        self.messages = {
            'name': "The provided channel name is invalid. The channel name should not contain any spaces and can be "
                    "up to 50 characters in length.",
            'channel_password': "The provided channel password is invalid. The channel password may contain a maximum "
                                "of 255 characters.",
            'xop_level': "The provided XOP Level is invalid. The XOP Level must be an integer between -2 and 9999",
            'manage_topic': "The manage topic attribute must be a valid boolean.",
            'topic_separator': "The provided topic separator is invalid. The topic separator may contain a maximum of "
                               "10 characters.",
            'topic_mode': "The topic provided topic mode is invalid. The topic mode may contain a maximum of 20 "
                          "characters.",
            'topic_max': "The provided maximum topics is invalid. The maximum topics must be an integer between "
                         "1 and 100",
            'log': "The log attribute must be a valid boolean.",
            'autojoin': "The autojoin attribute must be a valid boolean."
        }

    def creation(self, **kwargs):
        schema = Schema({
            Required('name'): self.rules['name'],
            Optional('channel_password'): self.rules['channel_password'],
            Optional('xop_level'): self.rules['xop_level'],
            Optional('manage_topic'): self.rules['manage_topic'],
            Optional('topic_separator'): self.rules['topic_separator'],
            Optional('topic_mode'): self.rules['topic_mode'],
            Optional('topic_max'): self.rules['topic_max'],
            Optional('log'): self.rules['log'],
            Optional('autojoin'): self.rules['autojoin']
        })

        self.validate(schema, **kwargs)

    def single(self, **kwargs):
        schema = Schema({
            Optional('name'): self.rules['name'],
            Optional('channel_password'): self.rules['channel_password'],
            Optional('xop_level'): self.rules['xop_level'],
            Optional('manage_topic'): self.rules['manage_topic'],
            Optional('topic_separator'): self.rules['topic_separator'],
            Optional('topic_mode'): self.rules['topic_mode'],
            Optional('topic_max'): self.rules['topic_max'],
            Optional('log'): self.rules['log'],
            Optional('autojoin'): self.rules['autojoin']
        })

        self.validate(schema, **kwargs)


# Exceptions
class ChannelNotFoundException(Exception):
    pass