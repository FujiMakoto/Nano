"""
net_irc.py: Establish a new IRC connection
"""
import logging
from configparser import ConfigParser
import irc.bot
import irc.strings
import irc.events
import irc.client
from .irc import IRC
from .irc_utils import MessageParser, Postmaster
from modules import Commander
from .language import Language
from .logger import IRCChannelLogger, IRCQueryLogger, IRCLoggerSource

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


# noinspection PyMethodMayBeStatic
class NanoIRC(IRC):
    """
    Establishes a new connection to the configured IRC server
    """

    def __init__(self, network, channel):
        """
        Initialize a new Nano IRC instance

        Args:
            channel(str):  The channel to join
            nickname(str): The nick to use
            server(str):   The server to connect to
            port(int):     The server port number
        """
        super().__init__(network, channel)
        # Load our configuration

        # Setup
        self.network = network
        self.channel = channel
        self.lang = Language()
        self.command = Commander(self)
        self.postmaster = Postmaster(self)
        self.message_parser = MessageParser()
        self.log = logging.getLogger('nano.irc')

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
        if source.nick in self.query_loggers:
            return self.query_loggers[source.nick]

        # Set up a new query logger instance
        self.query_loggers[source.nick] = IRCQueryLogger(self, IRCLoggerSource(source.nick, source.host))
        return self.query_loggers[source.nick]

    ################################
    # Numeric / Response Events    #
    ################################

    def on_nick_in_use(self, c, e):
        """
        Attempt to regain access to a nick in use if we can, otherwise append an underscore and retry

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # TODO: Ghost using nickserv if possible
        nick = c.get_nickname() + "_"
        self.log.info('Nickname {nick} in use, retrying with {new_nick}'.format(nick=c.get_nickname(), new_nick=nick))
        c.nick(nick)

    def on_service_info(self, c, e):
        """
        ???

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_welcome(self, c, e):
        """
        Join our specified channels once we get a welcome to the server

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # TODO: Multi-channel support
        self.log.info('Joining channel: ' + self.channel.name)
        c.join(self.channel.name)

    def on_feature_list(self, c, e):
        """
        Parse and save the servers supported IRC features for later reference

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # TODO
        # feature_pattern = re.compile("^([A-Z]+)(=(\S+))?$")
        pass

    def on_cannot_send_to_channel(self, c, e):
        """
        Handle instances where we cannot send a message to a channel we are in (generally when we are banned)

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_too_many_channels(self, c, e):
        """
        Handle instances where we attempt to join more channels than the server allows

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_erroneous_nick(self, c, e):
        """
        Handle instances where the nickname we want to use is considered erroneous by the server

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_unavailable_resource(self, c, e):
        """
        Handle instances where the nickname we want to use is not in use but unavailable (Release from nickserv?)

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Release nick from nickserv
        pass

    def on_channel_is_full(self, c, e):
        """
        If we try and join a channel that is full, wait before attempting to join the channel again

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Wait XX seconds and attempt to join
        pass

    def on_key_set(self, c, e):
        """
        Handle instances where we try and join a channel that is key protected (and we don't have a key saved)

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_bad_channel_key(self, c, e):
        """
        Handle instances where our key for a channel is returned invalid

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_invite_only_channel(self, c, e):
        """
        If we attempt to join a channel that is invite only, see if we can knock to request access

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Knock knock
        pass

    def on_banned_from_channel(self, c, e):
        """
        Handle instances where we are banned from a channel we are trying to join

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_ban_list_full(self, c, e):
        """
        Handle instances where we are unable to ban a user because the channels banlist is full

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_chanop_privs_needed(self, c, e):
        """
        Handle instances where we attempt to perform an action that requires channel operate privileges

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    ################################
    # Protocol Events              #
    ################################

    def on_public_message(self, c, e):
        """
        Handle public channel messages

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Log the message
        self.channel_logger.log(self.channel_logger.MESSAGE, e.source.nick, e.source.host, e.arguments[0])

        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.lang.set_name(source[1], e.source.nick)
        whois = self.connection.whois(e.source.nick)

        # Are we trying to call a command directly?
        if self.command.trigger_pattern.match(e.arguments[0]):
            self.log.info('Acknowledging public command request from ' + e.source.nick)
            reply = self._execute_command(e.arguments[0], e.source, True)
        else:
            self.log.debug('Querying language engine for a response to ' + e.source.nick)
            reply = self.lang.get_reply(source[1], e.arguments[0])

        if reply:
            self.log.debug('Delivering response messages')
            self.postmaster.deliver(reply, e.source, self.channel)
        else:
            self.log.debug('No response received')

        # Fire our module events
        event_replies = self.command.event(self.command.EVENT_PUBMSG, e)

        if event_replies:
            self.postmaster.deliver(event_replies, e.source, self.channel)

    def on_whoisuser(self, c, e):
        print(e.arguments)

    def on_action(self, c, e):
        """
        Handle actions (from both public channels AND queries)

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Log the action
        if e.target == c.get_nickname():
            logger = self.query_logger(e.source)
            logger.log(logger.ACTION, IRCLoggerSource(e.source.nick, e.source.host), e.arguments[0])
        else:
            self.channel_logger.log(self.channel_logger.ACTION, e.source.nick, e.source.host, e.arguments[0])

    def on_public_notice(self, c, e):
        """
        Handle public channel notices

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        self.channel_logger.log(self.channel_logger.NOTICE, e.source.nick, e.source.host, e.arguments[0])

    def on_private_message(self, c, e):
        """
        Handle private messages (queries)

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Log the message
        logger = self.query_logger(e.source)
        logger.log(logger.MESSAGE, IRCLoggerSource(e.source.nick, e.source.host), e.arguments[0])

        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.lang.set_name(source[1], e.source.nick)

        # Are we trying to call a command directly?
        if self.command.trigger_pattern.match(e.arguments[0]):
            self.log.info('Acknowledging private command request from ' + e.source.nick)
            reply = self._execute_command(e.arguments[0], e.source, False)
        else:
            self.log.debug('Querying language engine for a response to ' + e.source.nick)
            reply = self.lang.get_reply(source[1], e.arguments[0])

        if reply:
            self.log.debug('Delivering response messages')
            self.postmaster.deliver(reply, e.source, self.channel, False)
        else:
            self.log.info(e.source.nick + ' sent me a query I didn\'t know how to respond to')

    def on_private_notice(self, c, e):
        """
        Handle private notices

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Log the notice
        logger = self.query_logger(e.source)
        logger.log(logger.NOTICE, IRCLoggerSource(e.source.nick, e.source.host), e.arguments[0])

    def on_join(self, c, e):
        """
        Handle user join events

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        self.channel_logger.log(self.channel_logger.JOIN, e.source.nick, e.source.host)

    def on_part(self, c, e):
        """
        Handle user part events

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        if not len(e.arguments):
            e.arguments.append(None)

        self.channel_logger.log(self.channel_logger.PART, e.source.nick, e.source.host, e.arguments[0])

    def on_quit(self, c, e):
        """
        Handle channel exits

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # TODO: Clear login sessions
        if not len(e.arguments):
            e.arguments.append(None)

        self.channel_logger.log(self.channel_logger.QUIT, e.source.nick, e.source.host, e.arguments[0])

        # Fire our module events
        event_replies = self.command.event(self.command.EVENT_QUIT, e)

        if event_replies:
            self.postmaster.deliver(event_replies, e.source, self.channel)

    def on_kick(self, c, e):
        """
        Handle channel kick events

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass