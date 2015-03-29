import re
import logging
from html.parser import unescape

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class MessageParser:
    """
    Universal message parsing for IRC and web based protocols
    """
    # Contextual controls
    IRC_BOLD = "\x02"
    IRC_ITALICS = "\x1D"
    IRC_UNDERLINE = "\x1F"
    IRC_COLOR = "\x03"

    _nameToContext = {
        'IRC_BOLD': IRC_BOLD,
        'IRC_ITALICS': IRC_ITALICS,
        'IRC_UNDERLINE': IRC_UNDERLINE,
        'IRC_COLOR': IRC_COLOR
    }
    _contextToName = {
        IRC_BOLD: 'IRC_BOLD',
        IRC_ITALICS: 'IRC_ITALICS',
        IRC_UNDERLINE: 'IRC_UNDERLINE',
        IRC_COLOR: 'IRC_COLOR'
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

        self.irc_bold = re.compile(self.IRC_BOLD, re.UNICODE)
        self.irc_italics = re.compile(self.IRC_ITALICS, re.UNICODE)
        self.irc_underline = re.compile(self.IRC_UNDERLINE, re.UNICODE)

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
        message = self.html_bold.sub(self.IRC_BOLD, message)
        message = self.html_italics.sub(self.IRC_ITALICS, message)
        message = self.html_underline.sub(self.IRC_UNDERLINE, message)

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
            message = message_template.format(color_ctrl=self.IRC_COLOR, fg_code=fg_color, bg_code=bg_color,
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
            irc(src.NanoIRC): The active IRC connection
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
            (irc.client.privmsg), irc.client.notice or irc.client.action)
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
        destination, message = response

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
            reply = self.irc.commander.execute(message, source, public)
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