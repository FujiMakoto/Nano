"""
language.py: Nano language and response processing library
"""
import re
from configparser import ConfigParser
from rivescript import RiveScript
from modules.exceptions import ModuleDisabledError

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Language:
    """
    Performs various language processing related tasks
    """
    def __init__(self):
        """
        Initialize a new Language instance
        """
        # Load our language processing configuration
        self.config = self.config()

        # Initialize RiveScript
        self.rs = RiveScript(self.config.getboolean('Language', 'Debug'))
        self.rs.load_directory("./lang")
        self.rs.sort_replies()

    def get_reply(self, source, message):
        """
        Get a response to the specified message

        Args:
            source(str):  The host this message is coming from
            message(str): The message to get a response to

        Returns:
            str or None
        """
        # Parse our message
        message = self.parse_message(source, message)

        try:
            # Get our response message from RiveScript
            reply = self.rs.reply(source, message)

            # Make sure we didn't get an error in our response
            error_pattern = re.compile("(^ERR:)|(\[ERR:.*\])")
            if error_pattern.match(reply):
                reply = None
        except (IndexError, ModuleDisabledError):
            # Either we matched a response but did not pass a variable check, or we requested a disabled module
            reply = None

        # Return our response
        return reply

    def parse_message(self, source, message, parse_directed=True, strip_control_chars=True):
        """
        Clean our message and ready it for language processing

        Args:
            source(str):               The host this message is coming from
            message(str):              The message to parse
            parse_directed(bool):      Parse whether or not the message was directed at us
            strip_control_chars(bool): Strip control characters

        Returns:
            str: The parsed message
        """
        # Strip control characters (color, bold, etc.) from our message
        if strip_control_chars:
            message = re.sub("\x03(?:\d{1,2}(?:,\d{1,2})?)?", "", message, 0, re.UNICODE)

        # Parse whether or not this message was directed at us
        if parse_directed:
            directed_pattern = re.compile("^nano(\W)?\s+", re.IGNORECASE)
            directed = bool(directed_pattern.match(message))
            self.set_directed(source, directed)

        # Return the parsed message
        return message

    def set_name(self, source, name):
        """
        Set the name for the specified host

        Args:
            source(str): The host this message is coming from
            name(str):   The name to set
        """
        self.rs.set_uservar(source, "name", name)

    def set_directed(self, source, directed=True):
        """
        Set the directed flag for sent messages

        Args:
            source(str):    The host this message is coming from
            directed(bool): Whether or not this message was directed at us
        """
        self.rs.set_uservar(source, "directed", directed)

    def rivescript(self):
        """
        Return our RiveScript instance

        Returns:
            RiveScript
        """
        return self.rs

    @staticmethod
    def config():
        """
        Static method that returns the logger configuration

        Returns:
            ConfigParser
        """
        config = ConfigParser()
        config.read("config/language.cfg")
        return config