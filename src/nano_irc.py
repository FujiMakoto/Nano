"""
net_irc.py: Establish a new IRC connection
"""
import logging
from configparser import ConfigParser
from .irc import IRC
from .irc_utils import MessageParser, Postmaster
from .commander import Commander
from .logger import IRCChannelLogger, IRCQueryLogger, IRCLoggerSource
from .ignore import IgnoreList

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


# noinspection PyMethodMayBeStatic
class NanoIRC(IRC):
    """
    Establishes a new connection to the configured IRC server
    """

    def __init__(self, network, channel, plugins=None, language=None):
        """
        Initialize a new Nano IRC instance

        Args:
            network(database.models.Network): The IRC Network to connect to
            channel(database.models.channel): The channel to join
            plugins(src.plugins.PluginManager or None, optional):
                Plugins to bind to this Network instance. Defaults to None (no plugins)
            language(src.language.Language or None, optional):
                Language engine to bind to this Network instance: Defaults to None (no language parsing)
        """
        super().__init__(network, channel)
        # Setup
        self.log = logging.getLogger('nano.irc')
        self.network = network
        self.channel = channel

        # Bind plugins
        if plugins:
            self.log.debug('Binding plugins to Network {name} ({id})'.format(name=network.name, id=id(plugins)))
        else:
            self.log.debug('Not binding any plugins to Network {name}'.format(name=network.name))
        self.plugins = plugins

        # Bind language
        if language:
            self.log.debug('Binding language to Network {name} ({id})'.format(name=network.name, id=id(language)))
        else:
            self.log.debug('Not binding any language to Network {name}'.format(name=network.name))
        self.lang = language

        # Set up our Commander, Postmaster and MessageParser instances
        self.commander = Commander(self)
        self.postmaster = Postmaster(self)
        self.message_parser = MessageParser()

        # Load our client ignore list
        self.ignore_list = IgnoreList()

        # Network feature list
        self.network_features = {}

        # Set up our channel and query loggers
        self.channel_logger = IRCChannelLogger(self, IRCLoggerSource(channel.name), bool(self.channel.log))
        self.query_loggers  = {}

    @staticmethod
    def config(network=None):
        """
        Static method that returns the logger configuration

        Returns:
            ConfigParser
        """
        config = ConfigParser()
        config.read('config/irc.cfg')

        if network:
            return config[network]

        return config

    def query_logger(self, source):
        """
        Retrieve a query logger instance for the specified client

        Args:
            source(irc.client.NickMask): NickMask of the client

        Returns:
            logger.IRCQueryLogger
        """
        # Do we already have a query logging instance for this user?
        logger_formatted_nick = str(source.nick).lower().capitalize()
        if logger_formatted_nick in self.query_loggers:
            return self.query_loggers[logger_formatted_nick]

        # Set up a new query logger instance
        self.query_loggers[logger_formatted_nick] = IRCQueryLogger(self, IRCLoggerSource(source.nick, source.host))
        return self.query_loggers[logger_formatted_nick]

    def _log_message(self, event, log_format, public):
        """
        Log a channel or query event message

        Args:
            event(irc.client.Event): The IRC event instance
            log_format(str): The log format to use
            public(bool): This message was sent from a public channel
        """
        if public:
            self.channel_logger.log(log_format, event.source.nick, event.source.host, event.arguments[0])
        else:
            logger = self.query_logger(event.source)
            logger.log(log_format, IRCLoggerSource(event.source.nick, event.source.host), event.arguments[0])

    def _get_replies(self, event, public):
        """
        Query available sources for a reply to an event message

        Args:
            event(irc.client.Event): The IRC event instance
            public(bool): This message was sent from a public channel

        Returns:
            list, tuple, str or None
        """
        # Make sure this client isn't on our ignore list
        if self.ignore_list.exists(event.source):
            self.log.info('Not responding to a message from ' + event.source)
            return False

        # Are we trying to call a command directly?
        if self.commander.trigger_pattern.match(event.arguments[0]):
            self.log.info('Acknowledging {pub_or_priv} command request from {nick}'
                          .format(pub_or_priv='public' if public else 'private', nick=event.source.nick))
            return self.commander.execute(event.arguments[0], event.source, public)

        # Query the language engine for a response
        self.lang.set_name(event.source.host, event.source.nick)

        self.log.debug('Querying language engine for a response to ' + event.source.nick)
        reply = self.lang.get_reply(event.source.host, event.arguments[0])

        # Return our reply
        return reply

    def _handle_replies(self, event, replies=None, public=True, command_event=None):
        """
        Deliver event replies or fire plugin events if no replies have been received

        Args:
            event(irc.client.Event): The event instance
            replies(list, tuple, str or None. Optional): The event replies to process
            comment_event(str or None, Optional): The command event to trigger if there are no replies
        """
        if replies:
            self.log.debug('Delivering response messages')
            self.postmaster.deliver(replies, event.source, self.channel, public)
        else:
            self.log.debug('No response received')
            if command_event and replies is not False:
                self._fire_plugin_event(command_event, event)

    def _fire_plugin_event(self, event_name, event):
        """
        Args:
            event_name(str): The name of the event being fired
            event(irc.client.Event): The IRC event instance
        """
        event_replies = self.commander.event(event_name, event)

        if event_replies:
            self.postmaster.deliver(event_replies, event.source, self.channel)

    ################################
    # Numeric / Response Events    #
    ################################

    def on_nick_in_use(self, connection, event):
        """
        Attempt to regain access to a nick in use if we can, otherwise append an underscore and retry

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # TODO: Ghost using nickserv if possible
        nick = connection.get_nickname() + "_"
        self.log.info('Nickname {nick} in use, retrying with {new_nick}'
                      .format(nick=connection.get_nickname(), new_nick=nick))
        connection.nick(nick)

    def on_service_info(self, connection, event):
        """
        ???

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    def on_welcome(self, connection, event):
        """
        Join our specified channels once we get a welcome to the server

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # TODO: Multi-channel support
        self.log.info('Joining channel: ' + self.channel.name)
        connection.join(self.channel.name)

    def on_feature_list(self, connection, event):
        """
        Parse and save the servers supported IRC features for later reference

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # TODO
        # feature_pattern = re.compile("^([A-Z]+)(=(\S+))?$")
        pass

    def on_cannot_send_to_channel(self, connection, event):
        """
        Handle instances where we cannot send a message to a channel we are in (generally when we are banned)

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    def on_too_many_channels(self, connection, event):
        """
        Handle instances where we attempt to join more channels than the server allows

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    def on_erroneous_nick(self, connection, event):
        """
        Handle instances where the nickname we want to use is considered erroneous by the server

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    def on_unavailable_resource(self, connection, event):
        """
        Handle instances where the nickname we want to use is not in use but unavailable (Release from nickserv?)

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # Release nick from nickserv
        pass

    def on_channel_is_full(self, connection, event):
        """
        If we try and join a channel that is full, wait before attempting to join the channel again

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # Wait XX seconds and attempt to join
        pass

    def on_key_set(self, connection, event):
        """
        Handle instances where we try and join a channel that is key protected (and we don't have a key saved)

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    def on_bad_channel_key(self, connection, event):
        """
        Handle instances where our key for a channel is returned invalid

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    def on_invite_only_channel(self, connection, event):
        """
        If we attempt to join a channel that is invite only, see if we can knock to request access

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # Knock knock
        pass

    def on_banned_from_channel(self, connection, event):
        """
        Handle instances where we are banned from a channel we are trying to join

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    def on_ban_list_full(self, connection, event):
        """
        Handle instances where we are unable to ban a user because the channels banlist is full

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    def on_chanop_privs_needed(self, connection, event):
        """
        Handle instances where we attempt to perform an action that requires channel operate privileges

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass

    ################################
    # Protocol Events              #
    ################################

    def on_public_message(self, connection, event):
        """
        Handle public channel messages

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # Log the message
        self._log_message(event, self.channel_logger.MESSAGE, True)

        # Query for replies and fire plugin events
        replies = self._get_replies(event, True)
        self._handle_replies(event, replies, True, self.commander.EVENT_PUBMSG)

    def on_action(self, connection, event):
        """
        Handle actions (from both public channels AND queries)

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # Was this action sent from a public channel or private query?
        public = (event.target != connection.get_nickname)
        command_event = self.commander.EVENT_PUBACTION if public else self.commander.EVENT_PRIVACTION
        log_format = self.channel_logger.ACTION if public else self.query_logger(event.source).ACTION

        # Log the action
        self._log_message(event, log_format, public)

        # Query for replies and fire plugin events
        replies = self._get_replies(event, public)
        self._handle_replies(event, replies, public, command_event)

    def on_public_notice(self, connection, event):
        """
        Handle public channel notices

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # Log the notice
        self._log_message(event, self.channel_logger.NOTICE, True)

        # Fire plugin events
        self._handle_replies(event, public=True, command_event=self.commander.EVENT_PUBNOTICE)

    def on_private_message(self, connection, event):
        """
        Handle private messages (queries)

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # Log the message
        self._log_message(event, self.query_logger(event.source).MESSAGE, False)

        # Query for replies and fire plugin events
        replies = self._get_replies(event, False)
        self._handle_replies(event, replies, False, self.commander.EVENT_PRIVMSG)

    def on_private_notice(self, connection, event):
        """
        Handle private notices

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # Log the notice
        self._log_message(event, self.query_logger(event.source).NOTICE, False)

        # Fire plugin events
        self._handle_replies(event, public=False, command_event=self.commander.EVENT_PRIVNOTICE)

    def on_join(self, connection, event):
        """
        Handle user join events

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        self.channel_logger.log(self.channel_logger.JOIN, event.source.nick, event.source.host)

    def on_part(self, connection, event):
        """
        Handle user part events

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        if not len(event.arguments):
            event.arguments.append(None)

        self.channel_logger.log(self.channel_logger.PART, event.source.nick, event.source.host, event.arguments[0])

    def on_quit(self, connection, event):
        """
        Handle channel exits

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        # TODO: Clear login sessions
        if not len(event.arguments):
            event.arguments.append(None)

        self.channel_logger.log(self.channel_logger.QUIT, event.source.nick, event.source.host, event.arguments[0])

        # Fire plugin events
        event_replies = self.commander.event(self.commander.EVENT_QUIT, event)

        if event_replies:
            self.postmaster.deliver(event_replies, event.source, self.channel)

    def on_kick(self, connection, event):
        """
        Handle channel kick events

        Args:
            connection(irc.client.ServerConnection): The active IRC server connection
            event(irc.client.Event): The event response data
        """
        pass