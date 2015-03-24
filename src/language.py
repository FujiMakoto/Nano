"""
language.py: Nano language and response processing library
"""
import os
import re
import logging
from ast import literal_eval
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
        self.log = logging.getLogger('nano.language')
        # Load our language processing configuration
        self.config = self.config()

        # Initialize RiveScript
        self.log.info('Initializing language engine')
        self.rs = RiveScript(self.config.getboolean('Language', 'Debug'))
        self._load_language_files()
        self.error_pattern = re.compile("(^ERR:)|(\[ERR:.*\])")
        self.eval_pattern = re.compile("(^\(.+\)$|^\[.+\]$)")

    def _load_language_files(self):
        self.log.info('Loading language files')
        # Load the base language files
        self.log.info('Loading base language files')
        self.rs.load_directory("./lang")

        # Loop through our modules directory
        modules_dir = "modules"
        lang_dir = "lang"
        config_file = "module.cfg"
        for name in os.listdir(modules_dir):
            path = os.path.join(modules_dir, name)
            # Loop through our sub-directories that are not private (i.e. __pycache__)
            if os.path.isdir(path) and not name.startswith('_'):
                # Check and see if this module has a commands file
                module_lang_path = os.path.join(path, lang_dir)
                if os.path.isdir(module_lang_path):
                    # Check our module configuration file if it exists and make sure the module is enabled
                    module_enabled = True
                    config_path = os.path.join(path, config_file)
                    if os.path.isfile(config_path):
                        self.log.debug('Reading {module} configuration: {path}'.format(module=name, path=config_path))
                        config = ConfigParser()
                        config.read(os.path.join(path, config_file))
                        if config.has_option('Module', 'Enabled'):
                            module_enabled = config.getboolean('Module', 'Enabled')

                    if module_enabled:
                        self.log.info('Loading {module} language files'.format(module=name))
                        self.rs.load_directory(module_lang_path)
                    else:
                        self.log.debug('Not loading {module} language files because the module is disabled'
                                       .format(module=name))

        self.log.info('Sorting language replies')
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
        self.log.info('Thinking of a reply to send to ' + source)
        message = self.parse_message(source, message)

        # Request a reply to our message
        try:
            # Get our response message from RiveScript
            reply = self.rs.reply(source, message)

            # Make sure we didn't get an error in our response
            if self.error_pattern.match(reply):
                self.log.debug('Received an ERROR response: ' + reply)
                reply = None
        except (IndexError, ModuleDisabledError):
            # Either we matched a response but did not pass a variable check, or we requested a disabled module
            self.log.info('A response was matched, but we failed to pass a conditional check to retrieve it')
            reply = None

        # Evaluate our response into list/tuple form
        if reply and self.eval_pattern.match(reply):
            self.log.debug('Evaluating our response as a list or tuple')
            try:
                reply = literal_eval(reply)
            except (SyntaxError, ValueError) as exception:
                self.log.warn('Exception thrown when attempting to evaluate response: ' + str(exception))

        # Return our response
        if reply:
            self.log.info('Reply matched: ' + str(reply))
        else:
            self.log.info('Could not find a response to send')

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