"""
logger.py: Performs conversation / channel logging services
"""
import os
import time
import logging
from configparser import ConfigParser

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class _IRCLogger():
    """
    Base IRC logger class
    """
    def __init__(self, network, channel, enabled=True):
        """
        Initialize a new IRC Logger instance

        Args:
            network(database.models.Network): The IRC network name
            channel(database.models.Channel): The channel being logged
            enabled(bool): Enable / disable logging. Defaults to True
        """
        # Load the logger configuration file
        self.config  = self.config()
        self.config  = self.config['IRC']
        self.enabled = enabled

        # Set up our debug logger
        self.debug_log = logging.getLogger('nano.irc.logger')

        # Set our network and channel
        self.network = network
        self.channel = channel

        # Set the default timestamp format
        self.timestamp_format = self.config['TimestampFormat']

        # A logfile should be defined in the extending classes
        self.logfile = None

    def enable(self):
        """
        Enable the logger
        """
        self.debug_log.info('Setting up channel logging for ' + self.channel.name)
        self.enabled = True

    def disable(self):
        """
        Disable the logger
        """
        self.debug_log.info('Disabling channel logging for ' + self.channel.name)
        self.enabled = False

    def get_timestamp(self, timestamp_format=None):
        """
        Returns a formatted timestamp

        Args:
            timestamp_format(str or None): strftime format to use. Defaults to format specified in config

        Returns:
            str
        """
        if timestamp_format:
            return time.strftime(timestamp_format, time.localtime(time.time()))

        return time.strftime(self.timestamp_format, time.localtime(time.time()))

    @staticmethod
    def config():
        """
        Return the logger configuration

        Returns:
            ConfigParser
        """
        config = ConfigParser()
        config.read("config/logger.cfg")

        return config


class IRCChannelLogger(_IRCLogger):
    """
    Writes channel messages and actions to the IRC channels logfile
    """
    MESSAGE = " <{nick}> {message}"
    ACTION = " * {nick} {message}"
    NOTICE = " -{nick}/{channel}- {message}"
    JOIN = " {nick} ({hostmask}) has joined"
    PART = " {nick} has left ({message})"
    QUIT = " {nick} has quit ({message})"

    _formatToName = {
        MESSAGE: 'MESSAGE',
        ACTION: 'ACTION',
        NOTICE: 'NOTICE',
        JOIN: 'JOIN',
        PART: 'PART',
        QUIT: 'QUIT',
    }
    _nameToFormat = {
        'MESSAGE': MESSAGE,
        'ACTION': ACTION,
        'NOTICE': NOTICE,
        'JOIN': JOIN,
        'PART': PART,
        'QUIT': QUIT,
    }

    def __init__(self, network, channel, enabled=True):
        """
        Initialize a new IRC Channel Logger instance

        Args:
            network(database.models.Network): The IRC network name
            channel(database.models.Channel): The channel being logged
            enabled(bool): Enable / disable logging
        """
        super().__init__(network, channel, enabled)

        # Set our base path
        self.base_path    = str(self.config['LogPath']).rstrip("/") + "/%s/" % self.network.name
        self.logfile_name = self.channel.name + ".log"
        self.logfile_path = self.base_path + self.logfile_name

        # Make sure our logfile directory exists
        os.makedirs(self.base_path, 0o0750, True)

        # Open the logfile in append+read mode
        self.logfile = open(self.logfile_path, "a+")

    def log(self, log_format, nick, hostmask=None, message=None):
        """
        Write a new channel log entry

        Args:
            log_format(str): The string format to use for the log entry
            nick(str): The IRC nick of the client
            hostmask(str or None): The IRC hostmask of the client
            message(str or None): The message to be logged
        """
        # Make sure logging is enabled
        if not self.enabled:
            return False

        # Yo dawg
        self.debug_log.debug('Logging {type} from {nick}'.format(type=self._formatToName[log_format], nick=nick))

        # Format and write the log entry
        log_entry = log_format.format(nick=nick, hostmask=hostmask or "", message=message or "",
                                      channel=self.channel.name)
        self.logfile.write(self.get_timestamp() + log_entry + "\n")


class IRCQueryLogger(_IRCLogger):
    """
    Writes query messages and actions to the IRC query logfile
    """
    MESSAGE = " <{nick}> {message}"
    ACTION = " * {nick} {message}"
    NOTICE = " -{nick}/{channel}- {message}"
    JOIN = " {nick} ({hostmask}) has initiated a new query session"
    PART = " {nick} has left ({message})"
    QUIT = " {nick} has quit ({message})"

    _formatToName = {
        MESSAGE: 'MESSAGE',
        ACTION: 'ACTION',
        NOTICE: 'NOTICE',
        JOIN: 'JOIN',
        PART: 'PART',
        QUIT: 'QUIT',
    }
    _nameToFormat = {
        'MESSAGE': MESSAGE,
        'ACTION': ACTION,
        'NOTICE': NOTICE,
        'JOIN': JOIN,
        'PART': PART,
        'QUIT': QUIT,
    }

    def __init__(self, network, source, enabled=True):
        """
        Initialize a new IRC Query Logger instance

        Args:
            network(database.models.Network): The IRC network name
            source(irc.client.NickMask): NickMask of the client
            enabled(bool): Enable / disable logging. Defaults to True
        """
        super().__init__(network, source, enabled)
        self.source = source

        # Set our base path
        self.base_path    = str(self.config['LogPath']).rstrip("/") + "/%s/queries/" % self.network.name
        self.logfile_name = self.source.nick + ".log"
        self.logfile_path = self.base_path + self.logfile_name

        # Make sure our logfile directory exists
        os.makedirs(self.base_path, 0o0750, True)

        # Open the logfile in append+read mode
        self.logfile = open(self.logfile_path, "a+")

    def log(self, log_format, connection, source=None, message=None):
        """
        Write a new query log entry

        Args:
            log_format(str): The string format to use for the log entry
            connection(irc.client.ServerConnection): The IRC server connection we are logging from.
            source(irc.client.NickMask or None): NickMask of the client (or none if we're logging our own messages)
            message(str or None): The message to be logged
        """
        # Make sure logging is enabled
        if not self.enabled:
            return False

        # Are we logging a message from the client or ourselves?
        if source:
            self.nick = source.nick
            self.hostmask = source.host
        else:
            self.nick = connection.get_nickname()
            self.hostmask = "localhost"

        # Yo dawg
        self.debug_log.debug('Logging PRIV_{type} from {nick}'
                             .format(type=self._formatToName[log_format], nick=self.nick))

        # Format and write the log entry
        log_entry = log_format.format(nick=self.nick, hostmask=self.hostmask or "", message=message or "",
                                      channel=self.channel.name)
        self.logfile.write(self.get_timestamp() + log_entry + "\n")