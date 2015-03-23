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


# noinspection PyTypeChecker
class _IRCLogger():
    """
    Base IRC logger class
    """
    def __init__(self, irc, source, enabled=True):
        """
        Initialize a new IRC Logger instance

        Args:
            network(database.models.Network): The IRC network name
            source(logger.IRCLoggerSource): The channel or IRC nick being logged
            enabled(bool): Enable / disable logging. Defaults to True
        """
        # Load the logger configuration file
        self.config  = self.config()
        self.enabled = enabled

        # Set up our debug logger
        self.debug_log = logging.getLogger('nano.irc.logger')

        # Set our irc and source reference
        self.irc = irc
        self.source = source

        # Set the default timestamp format
        self.timestamp_format = self.config['IRC']['TimestampFormat']

        # A logfile and path should be defined in the extending classes
        self.logfile_path = None
        self.logfile = None

    def enable(self):
        """
        Enable the logger
        """
        self.debug_log.info('Setting up logging for ' + self.source.name)

        # Open our logfile
        if not self.logfile and self.logfile_path:
            self.debug_log.debug('Opening logfile: ' + self.logfile_path)
            self.logfile = open(self.logfile_path, "a+")

        self.enabled = True

    def disable(self):
        """
        Disable the logger
        """
        self.debug_log.info('Disabling logging for ' + self.source.name)

        # Close our logfile
        if self.logfile:
            self.debug_log.debug('Closing logfile: ' + self.logfile_path)
            self.logfile.close()
            self.logfile = None

        self.enabled = False

    def flush(self):
        """
        Flush the logfile to disk
        """
        if self.enabled and self.logfile:
            self.debug_log.debug('Flushing log for ' + self.source.name)
            self.logfile.flush()

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

    def __init__(self, irc, source, enabled=True):
        """
        Initialize a new IRC Channel Logger instance

        Args:
            network(database.models.Network): The IRC network name
            source(logger.IRCLoggerSource): The channel being logged
            enabled(bool): Enable / disable logging
        """
        super().__init__(irc, source, enabled)

        # Set our base path
        self.base_path    = str(self.config['IRC']['LogPath']).rstrip("/") + "/%s/" % self.irc.network.name
        self.logfile_name = self.source.name + ".log"
        self.logfile_path = self.base_path + self.logfile_name

        # Make sure our logfile directory exists
        os.makedirs(self.base_path, 0o0750, True)

        # Open the logfile if enabled
        if self.enabled:
            self.enable()
        else:
            self.logfile = None

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
                                      channel=self.source.name)
        self.logfile.write(self.get_timestamp() + log_entry + "\n")


class IRCQueryLogger(_IRCLogger):
    """
    Writes query messages and actions to the IRC query logfile
    """
    MESSAGE = " <{nick}> {message}"
    ACTION = " * {nick} {message}"
    NOTICE = " -{nick}- {message}"
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

    serviceNicks = [
        'NickServ',
        'ChanServ',
        'MemoServ',
        'BotServ',
        'OperServ',
        'HostServ',
        'Global',
        'HelpServ'
    ]

    def __init__(self, irc, source, enabled=True):
        """
        Initialize a new IRC Query Logger instance

        Args:
            network(database.models.Network): The IRC network name
            source(logger.IRCLoggerSource): The IRC nick being logged
            enabled(bool): Enable / disable logging. Defaults to True
        """
        super().__init__(irc, source, enabled)

        # Set come configuration variables
        self.redact_command_args = self.config.getboolean('IRC', 'RedactQueryCommandArguments')
        self.log_services = self.config.getboolean('IRC', 'LogServiceMessages')

        # Set our base path
        self.base_path    = str(self.config['IRC']['LogPath']).rstrip("/") + "/%s/queries/" % self.irc.network.name
        self.logfile_name = self.source.name + ".log"
        self.logfile_path = self.base_path + self.logfile_name

        # Make sure our logfile directory exists
        os.makedirs(self.base_path, 0o0750, True)

        # If we're not logging service messages, disable the logger on match
        if not self.log_services:
            if source.name in self.serviceNicks and self.irc.network.has_services:
                # TODO: Consider performing further verification to make sure someone isn't impersonating services
                self.debug_log.debug('Refusing to set up logger for service ' + source.name)
                self.enabled = False

        # Open the logfile if enabled
        if self.enabled:
            self.enable()
            self.log(self.JOIN, source)
        else:
            self.logfile = None

    def log(self, log_format, source=None, message=None):
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
            # Has the hostmask changed since our last session?
            if source.host != self.source.host:
                self.log(self.JOIN, source, message)
                self.source = IRCLoggerSource(source.name, source.host)

            # Set the clients nick and hostmask
            nick = source.name
            hostmask = source.host
        else:
            # Set our nick and hostmask
            nick = self.irc.connection.get_nickname()
            hostmask = "localhost"

        # Do we have a command string we need to filter?
        if self.redact_command_args and message and self.irc.command.trigger_pattern.match(message):
            # Parse our command string and re-format it into a filtered message
            module, command, args, opts = self.irc.command.parse_command_string(message)
            if module and command:
                message = ">>> {module} {command}".format(module=module, command=command)
                if len(args) or len(opts):
                    message += " [** Command arguments redacted **]"

        # Yo dawg
        self.debug_log.debug('Logging PRIV_{type} from {nick}'
                             .format(type=self._formatToName[log_format], nick=nick))

        # Format and write the log entry
        log_entry = log_format.format(nick=nick, hostmask=hostmask or "", message=message or "")
        self.logfile.write(self.get_timestamp() + log_entry + "\n")


class IRCLoggerSource:
    """
    IRC Logging source
    """
    def __init__(self, name, host=None):
        """
        Initialize a new IRC Logger Source class

        Args:
            name(str): The IRC nick or channel name
            host(str): The clients hostmask
        """
        self.name = name
        self.host = host
