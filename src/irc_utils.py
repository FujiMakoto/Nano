import re
import logging
from html.parser import unescape

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class MessageParser:
    """
    Universal message parsing for the CLI, IRC and web based protocols
    """
    # IRC Contextual controls
    IRC_BOLD = "\x02"
    IRC_ITALICS = "\x1D"
    IRC_UNDERLINE = "\x1F"
    IRC_COLOR = "\x03"

    _nameToIRCContext = {
        'IRC_BOLD': IRC_BOLD,
        'IRC_ITALICS': IRC_ITALICS,
        'IRC_UNDERLINE': IRC_UNDERLINE,
        'IRC_COLOR': IRC_COLOR
    }
    _IRCContextToName = {
        IRC_BOLD: 'IRC_BOLD',
        IRC_ITALICS: 'IRC_ITALICS',
        IRC_UNDERLINE: 'IRC_UNDERLINE',
        IRC_COLOR: 'IRC_COLOR'
    }

    # IRC color formatting codes
    IRC_WHITE = "00"
    IRC_BLACK = "01"
    IRC_BLUE = "02"
    IRC_GREEN = "03"
    IRC_RED = "04"
    IRC_BROWN = "05"
    IRC_PURPLE = "06"
    IRC_ORANGE = "07"
    IRC_YELLOW = "08"
    IRC_LIME = "09"
    IRC_TEAL = "10"
    IRC_AQUA = "11"
    IRC_ROYAL = "12"
    IRC_PINK = "12"
    IRC_GREY = "14"
    IRC_SILVER = "15"

    _nameToIRCColor = {
        'IRC_WHITE': IRC_WHITE,
        'IRC_BLACK': IRC_BLACK,
        'IRC_BLUE': IRC_BLUE,
        'IRC_GREEN': IRC_GREEN,
        'IRC_RED': IRC_RED,
        'IRC_BROWN': IRC_BROWN,
        'IRC_PURPLE': IRC_PURPLE,
        'IRC_ORANGE': IRC_ORANGE,
        'IRC_YELLOW': IRC_YELLOW,
        'IRC_LIME': IRC_LIME,
        'IRC_TEAL': IRC_TEAL,
        'IRC_AQUA': IRC_AQUA,
        'IRC_ROYAL': IRC_ROYAL,
        'IRC_PINK': IRC_PINK,
        'IRC_GREY': IRC_GREY,
        'IRC_SILVER': IRC_SILVER
    }
    _IRCColorToName = {
        IRC_WHITE: 'IRC_WHITE',
        IRC_BLACK: 'IRC_BLACK',
        IRC_BLUE: 'IRC_BLUE',
        IRC_GREEN: 'IRC_GREEN',
        IRC_RED: 'IRC_RED',
        IRC_BROWN: 'IRC_BROWN',
        IRC_PURPLE: 'IRC_PURPLE',
        IRC_ORANGE: 'IRC_ORANGE',
        IRC_YELLOW: 'IRC_YELLOW',
        IRC_LIME: 'IRC_LIME',
        IRC_TEAL: 'IRC_TEAL',
        IRC_AQUA: 'IRC_AQUA',
        IRC_ROYAL: 'IRC_ROYAL',
        IRC_PINK: 'IRC_PINK',
        IRC_GREY: 'IRC_GREY',
        IRC_SILVER: 'IRC_SILVER'
    }

    # CLI ANSI controls
    CLI_RESET = '\033[0m'  # Toggle's for bold, italics and underline are not widely supported, so we have to use reset
    CLI_BOLD = "\033[1m"
    CLI_ITALICS = "\033[3m"  # Not widely supported
    CLI_UNDERLINE = "\033[4m"

    _nameToCLIContext = {
        'CLI_RESET': CLI_RESET,
        'CLI_BOLD': CLI_BOLD,
        'CLI_ITALICS': CLI_ITALICS,
        'CLI_UNDERLINE': CLI_UNDERLINE,
    }
    _CLIContextToName = {
        CLI_RESET: 'CLI_RESET',
        CLI_BOLD: 'CLI_BOLD',
        CLI_ITALICS: 'CLI_ITALICS',
        CLI_UNDERLINE: 'CLI_UNDERLINE',
    }

    # CLI ANSI color formatting codes
    CLI_DEFAULT = "\033[39m"
    CLI_WHITE = "\033[97m"
    CLI_BLACK = "\033[30m"
    CLI_BLUE = "\033[34m"
    CLI_GREEN = "\033[32m"
    CLI_RED = "\033[31m"
    CLI_BROWN = "\033[33m"
    CLI_PURPLE = "\033[35m"
    CLI_ORANGE = "\033[33m"  # Actually brown / yellow
    CLI_YELLOW = "\033[93m"
    CLI_LIME = "\033[92m"
    CLI_TEAL = "\033[36m"
    CLI_AQUA = "\033[96m"
    CLI_ROYAL = "\033[94m"
    CLI_PINK = "\033[95m"
    CLI_GREY = "\033[37m"
    CLI_SILVER = "\033[37m"
    
    _nameToCLIColor = {
        'CLI_WHITE': CLI_WHITE,
        'CLI_BLACK': CLI_BLACK,
        'CLI_BLUE': CLI_BLUE,
        'CLI_GREEN': CLI_GREEN,
        'CLI_RED': CLI_RED,
        'CLI_BROWN': CLI_BROWN,
        'CLI_PURPLE': CLI_PURPLE,
        'CLI_ORANGE': CLI_ORANGE,
        'CLI_YELLOW': CLI_YELLOW,
        'CLI_LIME': CLI_LIME,
        'CLI_TEAL': CLI_TEAL,
        'CLI_AQUA': CLI_AQUA,
        'CLI_ROYAL': CLI_ROYAL,
        'CLI_PINK': CLI_PINK,
        'CLI_GREY': CLI_GREY,
        'CLI_SILVER': CLI_SILVER
    }
    _CLIColorToName = {
        CLI_WHITE: 'CLI_WHITE',
        CLI_BLACK: 'CLI_BLACK',
        CLI_BLUE: 'CLI_BLUE',
        CLI_GREEN: 'CLI_GREEN',
        CLI_RED: 'CLI_RED',
        CLI_BROWN: 'CLI_BROWN',
        CLI_PURPLE: 'CLI_PURPLE',
        CLI_ORANGE: 'CLI_ORANGE',
        CLI_YELLOW: 'CLI_YELLOW',
        CLI_LIME: 'CLI_LIME',
        CLI_TEAL: 'CLI_TEAL',
        CLI_AQUA: 'CLI_AQUA',
        CLI_ROYAL: 'CLI_ROYAL',
        CLI_PINK: 'CLI_PINK',
        CLI_GREY: 'CLI_GREY',
        CLI_SILVER: 'CLI_SILVER'
    }
    
    # CLI ANSI background color formatting codes
    CLI_BG_DEFAULT = "\033[49m"
    CLI_BG_WHITE = "\033[107m"
    CLI_BG_BLACK = "\033[40m"
    CLI_BG_BLUE = "\033[44m"
    CLI_BG_GREEN = "\033[42m"
    CLI_BG_RED = "\033[41m"
    CLI_BG_BROWN = "\033[43m"
    CLI_BG_PURPLE = "\033[45m"
    CLI_BG_ORANGE = "\033[43m"  # Actually brown / yellow
    CLI_BG_YELLOW = "\033[103m"
    CLI_BG_LIME = "\033[102m"
    CLI_BG_TEAL = "\033[46m"
    CLI_BG_AQUA = "\033[106m"
    CLI_BG_ROYAL = "\033[104m"
    CLI_BG_PINK = "\033[105m"
    CLI_BG_GREY = "\033[47m"
    CLI_BG_SILVER = "\033[47m"
    
    _nameToCLIBackgroundColor = {
        'CLI_BG_DEFAULT': CLI_BG_DEFAULT,
        'CLI_BG_WHITE': CLI_BG_WHITE,
        'CLI_BG_BLACK': CLI_BG_BLACK,
        'CLI_BG_BLUE': CLI_BG_BLUE,
        'CLI_BG_GREEN': CLI_BG_GREEN,
        'CLI_BG_RED': CLI_BG_RED,
        'CLI_BG_BROWN': CLI_BG_BROWN,
        'CLI_BG_PURPLE': CLI_BG_PURPLE,
        'CLI_BG_ORANGE': CLI_BG_ORANGE,
        'CLI_BG_YELLOW': CLI_BG_YELLOW,
        'CLI_BG_LIME': CLI_BG_LIME,
        'CLI_BG_TEAL': CLI_BG_TEAL,
        'CLI_BG_AQUA': CLI_BG_AQUA,
        'CLI_BG_ROYAL': CLI_BG_ROYAL,
        'CLI_BG_PINK': CLI_BG_PINK,
        'CLI_BG_GREY': CLI_BG_GREY,
        'CLI_BG_SILVER': CLI_BG_SILVER
    }
    _CLIBackgroundColorToName = {
        CLI_BG_DEFAULT: 'CLI_BG_DEFAULT',
        CLI_BG_WHITE: 'CLI_BG_WHITE',
        CLI_BG_BLACK: 'CLI_BG_BLACK',
        CLI_BG_BLUE: 'CLI_BG_BLUE',
        CLI_BG_GREEN: 'CLI_BG_GREEN',
        CLI_BG_RED: 'CLI_BG_RED',
        CLI_BG_BROWN: 'CLI_BG_BROWN',
        CLI_BG_PURPLE: 'CLI_BG_PURPLE',
        CLI_BG_ORANGE: 'CLI_BG_ORANGE',
        CLI_BG_YELLOW: 'CLI_BG_YELLOW',
        CLI_BG_LIME: 'CLI_BG_LIME',
        CLI_BG_TEAL: 'CLI_BG_TEAL',
        CLI_BG_AQUA: 'CLI_BG_AQUA',
        CLI_BG_ROYAL: 'CLI_BG_ROYAL',
        CLI_BG_PINK: 'CLI_BG_PINK',
        CLI_BG_GREY: 'CLI_BG_GREY',
        CLI_BG_SILVER: 'CLI_BG_SILVER'
    }

    def __init__(self):
        """
        Initialize a new Message Parser instance
        """
        # Bold, Italics, Underline
        self.html_bold = re.compile("(<strong>|</strong>)", re.UNICODE)
        self.html_italics = re.compile("(<em>|</em>)", re.UNICODE)
        self.html_underline = re.compile("(<u>|</u>)", re.UNICODE)

        self.html_bold_start = re.compile("<strong>", re.UNICODE)
        self.html_italics_start = re.compile("<em>", re.UNICODE)
        self.html_underline_start = re.compile("<u>", re.UNICODE)

        self.html_bold_stop = re.compile("(</strong>)", re.UNICODE)
        self.html_italics_stop = re.compile("(</em>)", re.UNICODE)
        self.html_underline_stop = re.compile("(</u>)", re.UNICODE)

        # These aren't really useful at the moment, don't try and use them
        self.irc_bold = re.compile(re.escape(self.IRC_BOLD), re.UNICODE)
        self.irc_italics = re.compile(re.escape(self.IRC_ITALICS), re.UNICODE)
        self.irc_underline = re.compile(re.escape(self.IRC_UNDERLINE), re.UNICODE)

        self.cli_reset = re.compile(re.escape(self.CLI_RESET), re.UNICODE)
        self.cli_bold = re.compile(re.escape(self.CLI_BOLD), re.UNICODE)
        self.cli_italics = re.compile(re.escape(self.CLI_ITALICS), re.UNICODE)
        self.cli_underline = re.compile(re.escape(self.CLI_UNDERLINE), re.UNICODE)

        # Color formatting
        self.html_color = re.compile("(?P<opening_tag><p(\s)?\sclass=[\"']([a-zA-Z-_\s]+\s)?(fg-|bg-)([A-Za-z]+)"
                                     "(\s[a-zA-Z-_\s]+)?[\"'](\s)?>)(?P<message>[^<]+)(<\/p>)", re.UNICODE)
        self.html_fg_color = re.compile("(?P<opening_tag><p(\s.*)?\sclass=[\"'](.*\s)?fg-(?P<fg_color>[A-Za-z]+)(\s.*)?"
                                        "[\"'](\s.*)?>)", re.UNICODE)
        self.html_bg_color = re.compile("(?P<opening_tag><p(\s.*)?\sclass=[\"'](.*\s)?bg-(?P<bg_color>[A-Za-z]+)(\s.*)?"
                                        "[\"'](\s.*)?>)", re.UNICODE)

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

        # Color code replacement method
        def color_replace(match):
            fg_match = self.html_fg_color.match(match.group('opening_tag'))
            bg_match = self.html_bg_color.match(match.group('opening_tag'))

            # Set foreground / background colors
            fg_color = self.IRC_BLACK
            bg_color = None

            # Foreground
            if fg_match:
                fg_color_name = 'IRC_' + fg_match.group('fg_color').upper()
                if fg_color_name in self._nameToIRCColor:
                    fg_color = self._nameToIRCColor[fg_color_name]
            # Background
            if bg_match:
                bg_color_name = 'IRC_' + bg_match.group('bg_color').upper()
                if bg_color_name in self._nameToIRCColor:
                    bg_color = self._nameToIRCColor[bg_color_name]

            # Apply foreground / background colors
            if fg_match or bg_match:
                # Foreground and background or foreground only?
                if bg_color:
                    message_template = "{color_ctrl}{fg_code},{bg_code}{message}{color_ctrl}"
                else:
                    message_template = "{color_ctrl}{fg_code}{message}{color_ctrl}"

                # Format the message template
                formatted = message_template.format(color_ctrl=self.IRC_COLOR, fg_code=fg_color, bg_code=bg_color,
                                                    message=match.group('message'))
                return formatted

        # Substitute foreground / background color matches
        message = self.html_color.sub(color_replace, message)

        # Unescape HTML entities
        message = unescape(message)

        # Return the formatted message
        return message

    def html_to_cli(self, message):
        """
        Replaces HTML contextual formatting with CLI ANSI codes

        Args:
            message(str): The message to format

        Returns:
            str
        """
        # Bold, Italics, Underline
        message = self.html_bold_start.sub(self.CLI_BOLD, message)
        message = self.html_bold_stop.sub(self.CLI_RESET, message)

        message = self.html_italics_start.sub(self.CLI_ITALICS, message)
        message = self.html_italics_stop.sub(self.CLI_RESET, message)

        message = self.html_underline_start.sub(self.CLI_UNDERLINE, message)
        message = self.html_underline_stop.sub(self.CLI_RESET, message)

        # Color code replacement method
        def color_replace(match):
            fg_match = self.html_fg_color.match(match.group('opening_tag'))
            bg_match = self.html_bg_color.match(match.group('opening_tag'))

            # Set foreground / background colors
            fg_color = self.CLI_DEFAULT
            bg_color = None

            # Foreground
            if fg_match:
                fg_color_name = 'CLI_' + fg_match.group('fg_color').upper()
                if fg_color_name in self._nameToCLIColor:
                    fg_color = self._nameToCLIColor[fg_color_name]
            # Background
            if bg_match:
                bg_color_name = 'CLI_BG_' + bg_match.group('bg_color').upper()
                if bg_color_name in self._nameToCLIBackgroundColor:
                    bg_color = self._nameToCLIBackgroundColor[bg_color_name]

            # Apply foreground / background colors
            if fg_match or bg_match:
                # Foreground and background or foreground only?
                if bg_color:
                    message_template = "{fg_code}{bg_code}{message}{bg_default}{fg_default}"
                else:
                    message_template = "{fg_code}{message}{fg_default}"

                # Format the message template
                formatted = message_template.format(fg_code=fg_color, bg_code=bg_color, message=match.group('message'),
                                                    bg_default=self.CLI_BG_DEFAULT, fg_default=self.CLI_DEFAULT)
                return formatted

        # Substitute foreground / background color matches
        message = self.html_color.sub(color_replace, message)

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