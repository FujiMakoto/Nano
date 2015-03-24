"""
net_irc.py: Establish a new IRC connection
"""
import re
import logging
from html.parser import unescape
from configparser import ConfigParser
import irc.bot
import irc.strings
import irc.events
from modules import Commander
from .language import Language
from .logger import IRCChannelLogger, IRCQueryLogger, IRCLoggerSource

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class NanoIRC(irc.bot.SingleServerIRCBot):
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
        irc.bot.SingleServerIRCBot.__init__(self, [(network.host, network.port)], network.nick, network.nick)
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

    def on_nicknameinuse(self, c, e):
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

    def on_serviceinfo(self, c, e):
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

    def on_featurelist(self, c, e):
        """
        Parse and save the servers supported IRC features for later reference

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # TODO
        # feature_pattern = re.compile("^([A-Z]+)(=(\S+))?$")
        pass

    def on_cannotsendtochan(self, c, e):
        """
        Handle instances where we cannot send a message to a channel we are in (generally when we are banned)

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_toomanychannels(self, c, e):
        """
        Handle instances where we attempt to join more channels than the server allows

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_erroneusnickname(self, c, e):
        """
        Handle instances where the nickname we want to use is considered erroneous by the server

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_unavailresource(self, c, e):
        """
        Handle instances where the nickname we want to use is not in use but unavailable (Release from nickserv?)

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Release nick from nickserv
        pass

    def on_channelisfull(self, c, e):
        """
        If we try and join a channel that is full, wait before attempting to join the channel again

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Wait XX seconds and attempt to join
        pass

    def on_keyset(self, c, e):
        """
        Handle instances where we try and join a channel that is key protected (and we don't have a key saved)

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_badchannelkey(self, c, e):
        """
        Handle instances where our key for a channel is returned invalid

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_inviteonlychan(self, c, e):
        """
        If we attempt to join a channel that is invite only, see if we can knock to request access

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        # Knock knock
        pass

    def on_bannedfromchan(self, c, e):
        """
        Handle instances where we are banned from a channel we are trying to join

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_banlistfull(self, c, e):
        """
        Handle instances where we are unable to ban a user because the channels banlist is full

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        pass

    def on_chanoprivsneeded(self, c, e):
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

    def on_pubmsg(self, c, e):
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

    def on_pubnotice(self, c, e):
        """
        Handle public channel notices

        Args:
            c(irc.client.ServerConnection): The active IRC server connection
            e(irc.client.Event): The event response data
        """
        self.channel_logger.log(self.channel_logger.NOTICE, e.source.nick, e.source.host, e.arguments[0])

    def on_privmsg(self, c, e):
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

    def on_privnotice(self, c, e):
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


class MessageParser:
    """
    Universal message parsing for IRC and web based protocols
    """
    # Contextual controls
    BOLD = "\x02"
    ITALICS = "\x1D"
    UNDERLINE = "\x1F"
    COLOR = "\x03"

    _nameToContext = {
        'BOLD': BOLD,
        'ITALICS': ITALICS,
        'UNDERLINE': UNDERLINE,
        'COLOR': COLOR
    }
    _contextToName = {
        BOLD: 'BOLD',
        ITALICS: 'ITALICS',
        UNDERLINE: 'UNDERLINE',
        COLOR: 'COLOR'
    }

    # Color formatting codes
    WHITE = "00"
    BLACK = "01"
    BLUE = "02"
    GREEN = "03"
    RED = "04"
    BROWN = "05"
    PURPLE = "06"
    ORANGE = "07"
    YELLOW = "08"
    LIME = "09"
    TEAL = "10"
    AQUA = "11"
    ROYAL = "12"
    PINK = "12"
    GREY = "14"
    SILVER = "15"

    _nameToColor = {
        'WHITE': WHITE,
        'BLACK': BLACK,
        'BLUE': BLUE,
        'GREEN': GREEN,
        'RED': RED,
        'BROWN': BROWN,
        'PURPLE': PURPLE,
        'ORANGE': ORANGE,
        'YELLOW': YELLOW,
        'LIME': LIME,
        'TEAL': TEAL,
        'AQUA': AQUA,
        'ROYAL': ROYAL,
        'PINK': PINK,
        'GREY': GREY,
        'SILVER': SILVER
    }
    _colorToName = {
        WHITE: 'WHITE',
        BLACK: 'BLACK',
        BLUE: 'BLUE',
        GREEN: 'GREEN',
        RED: 'RED',
        BROWN: 'BROWN',
        PURPLE: 'PURPLE',
        ORANGE: 'ORANGE',
        YELLOW: 'YELLOW',
        LIME: 'LIME',
        TEAL: 'TEAL',
        AQUA: 'AQUA',
        ROYAL: 'ROYAL',
        PINK: 'PINK',
        GREY: 'GREY',
        SILVER: 'SILVER'
    }

    def __init__(self):
        """
        Initialize a new Message Parser instance
        """
        # Bold, Italics, Underline
        self.html_bold = re.compile("(<strong>|<\/strong>)", re.UNICODE)
        self.html_italics = re.compile("(<em>|<\/em>)", re.UNICODE)
        self.html_underline = re.compile("(<u>|<\/u>)", re.UNICODE)

        self.irc_bold = re.compile(self.BOLD, re.UNICODE)
        self.irc_italics = re.compile(self.ITALICS, re.UNICODE)
        self.irc_underline = re.compile(self.UNDERLINE, re.UNICODE)

        # Color formatting
        self.html_fg_color = re.compile("(?P<opening_tag><p(\s.*)?\sclass=[\"'](.*\s)?fg-(?P<fg_color>[A-Za-z]+)(\s.*)?"
                                        "[\"'](\s.*)?>)(?P<message>.+)(?P<closing_tag><\/p>)", re.UNICODE)
        self.html_bg_color = re.compile("(?P<opening_tag><p(\s.*)?\sclass=[\"'](.*\s)?bg-(?P<bg_color>[A-Za-z]+)(\s.*)?"
                                        "[\"'](\s.*)?>)(?P<message>.+)(?P<closing_tag><\/p>)", re.UNICODE)

    def html_to_irc(self, message):
        """
        Replaces HTML contextual formatting with IRC control codes

        Args:
            message(str): The message to format

        Returns:
            str
        """
        # Bold, Italics, Underline
        message = self.html_bold.sub(self.BOLD, message)
        message = self.html_italics.sub(self.ITALICS, message)
        message = self.html_underline.sub(self.UNDERLINE, message)

        # Match foreground / background colors
        fg_match = self.html_fg_color.match(message)
        bg_match = self.html_bg_color.match(message)

        # Set foreground / background colors
        fg_color = self.BLACK
        bg_color = None

        # Foreground
        if fg_match:
            fg_color_name = fg_match.group('fg_color').upper()
            if fg_color_name in self._nameToColor:
                fg_color = self._nameToColor[fg_color_name]
        # Background
        if bg_match:
            bg_color_name = bg_match.group('bg_color').upper()
            if bg_color_name in self._nameToColor:
                bg_color = self._nameToColor[bg_color_name]

        # Apply foreground / background colors
        if fg_match or bg_match:
            # Set the first available match to pull our message from later
            color_match = fg_match if fg_match else bg_match

            # Foreground and background or foreground only?
            if bg_color:
                message_template = "{color_ctrl}{fg_code},{bg_code}{message}{color_ctrl}"
            else:
                message_template = "{color_ctrl}{fg_code}{message}{color_ctrl}"

            # Format the message template
            message = message_template.format(color_ctrl=self.COLOR, fg_code=fg_color, bg_code=bg_color,
                                              message=color_match.group('message'))

        # Unescape HTML entities
        message = unescape(message)

        # Return the formatted message
        return message


class Postmaster:
    """
    Handles message deliveries
    """
    # Explicit destinations
    PRIVATE = "private"
    PRIVATE_NOTICE = "private_notice"
    PRIVATE_ACTION = "private_action"
    PUBLIC = "public"
    PUBLIC_NOTICE = "public_notice"
    PUBLIC_ACTION = "public_action"

    # Implicit destinations
    ACTION = "action"

    # Special destinations
    COMMAND = "command"

    _nameToDestination = {
        'PRIVATE': PRIVATE,
        'PRIVATE_NOTICE': PRIVATE_NOTICE,
        'PRIVATE_ACTION': PRIVATE_ACTION,
        'PUBLIC': PUBLIC,
        'PUBLIC_NOTICE': PUBLIC_NOTICE,
        'PUBLIC_ACTION': PUBLIC_ACTION,
        'ACTION': ACTION,
        'COMMAND': COMMAND
    }
    _destinationToName = {
        PRIVATE: 'PRIVATE',
        PRIVATE_NOTICE: 'PRIVATE_NOTICE',
        PRIVATE_ACTION: 'PRIVATE_ACTION',
        PUBLIC: 'PUBLIC',
        PUBLIC_NOTICE: 'PUBLIC_NOTICE',
        PUBLIC_ACTION: 'PUBLIC_ACTION',
        ACTION: 'ACTION',
        COMMAND: 'COMMAND'
    }

    def __init__(self, irc):
        """
        Initialize a new Postmaster instance

        Args:
            irc(NanoIRC): The active IRC connection
        """
        self.log = logging.getLogger('nano.irc.postmaster')
        self.irc = irc
        self.privmsg = getattr(irc.connection, 'privmsg')
        self.notice = getattr(irc.connection, 'notice')
        self.action = getattr(irc.connection, 'action')

    def _get_handler(self, response):
        """
        Returns the message handler for the supplied message's destination

        Args:
            response(tuple or str): The response message to parse

        Returns:
            (irc.client.privmsg, irc.client.notice or irc.client.action)
        """
        # Set the default handler and return if we have no explicit destination
        default_handler = self.privmsg
        if not isinstance(response, tuple):
            return default_handler

        # Retrieve our message destination
        # http://docs.python-guide.org/en/latest/writing/gotchas/#mutable-default-arguments
        # destination, message = message.popitem()
        destination, message = response

        # Channel / query responses
        if destination in [self.PRIVATE, self.PUBLIC]:
            self.log.debug('Setting the message handler to privmsg')
            return self.privmsg

        # Notice responses
        if destination in [self.PRIVATE_NOTICE, self.PUBLIC_NOTICE]:
            self.log.debug('Setting the message handler to notice')
            return self.notice

        # Action responses
        if destination in [self.PRIVATE_ACTION, self.PUBLIC_ACTION, self.ACTION]:
            self.log.debug('Setting the message handler to action')
            return self.action

        # Return our default handler if we don't recognize the request
        return default_handler

    def _get_destination(self, response, source, channel, public):
        """
        Returns the destination a supplied message should be delivered to

        Args:
            response(tuple or str): The response message to parse
            source(irc.client.NickMask): The NickMask of our client
            channel(database.models.Channel): The channel we are currently active in
            public(bool): Whether or not we are responding to a public message

        Returns:
            str
        """
        # Set the default destination and return if we have no explicit destination
        default_destination = source.nick if not public else channel.name
        if not isinstance(response, tuple):
            return default_destination

        # Retrieve our message destination
        destination, response = response

        # Debug logging stuff
        if destination in self._destinationToName:
            self.log.debug('Registering message destination as ' + self._destinationToName[destination])
        else:
            self.log.debug('Registering message destination as DEFAULT ({default})'.format(default=default_destination))

        # If we're sending an implicit action, send it to our default destination
        if destination == self.ACTION:
            return default_destination

        # If we're sending a command response, return COMMAND to trigger a firing event
        if destination == self.COMMAND:
            return self.COMMAND

        # Send private responses to the clients nick
        if destination in [self.PRIVATE, self.PRIVATE_NOTICE, self.PRIVATE_ACTION]:
            return source.nick

        # Send public responses to the active channel
        if destination in [self.PUBLIC, self.PUBLIC_NOTICE, self.PUBLIC_ACTION]:
            return channel.name

        # Return our default destination if we don't recognize the request
        return default_destination

    def _fire_command(self, message, source, channel, public):
        """
        Fire a command and cycle back to deliver its response message(s)

        Args:
            message(str): The response message or "command string"
            source(irc.client.NickMask): The NickMask of our client
            channel(database.models.Channel): The channel we are currently active in
            public(bool): Whether or not we are responding to a public message. Defaults to True
        """
        # Attempt to execute the command
        self.log.info('Attempting to execute a command from a response message')
        try:
            reply = self.irc.command.execute(message, source, public)
        except Exception as e:
            self.log.warn('Exception thrown when executing command "{cmd}": {exception}'
                          .format(cmd=message, exception=str(e)))
            return

        self.log.info('Cycling back to deliver a command response')
        self.deliver(reply, source, channel, public)

    def _parse_response_message(self, response):
        """
        Retrieve the message from a response and apply formatting to it

        Args:
            response(tuple or str): The response to retrieve a message from

        Returns:
            str
        """
        # Get our message from the response
        message = response[1] if isinstance(response, tuple) else str(response)

        # Format and return the message string
        message = self.irc.message_parser.html_to_irc(message)
        return message

    def deliver(self, responses, source, channel, public=True):
        """
        Deliver supplied messages to their marked destinations and recipients

        Args:
            responses(list, tuple or str): The message(s) to deliver
            source(irc.client.NickMask): The NickMask of our client
            channel(database.models.Channel): The channel we are currently active in
            public(bool, optional): Whether or not we are responding to a public message. Defaults to True
        """
        # Make sure we have a list of messages to iterate through
        if not isinstance(responses, list):
            responses = [responses]

        # Iterate through our messages
        for response in responses:
            # Get our message handler and destination
            handler = self._get_handler(response)
            destination = self._get_destination(response, source, channel, public)

            # Fetch a formatted message from the response
            message = self._parse_response_message(response)

            # Is our destination the command handler?
            if destination is self.COMMAND:
                self._fire_command(message, source, channel, public)
                continue

            # Deliver the message!
            self.log.info('Delivering message')
            handler(destination, message)


class IRCFeatureList:
    def __init__(self):
        pass