"""
logger.py: Performs conversation / channel logging services
"""
import os
import time
from configparser import ConfigParser

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class _IRCLogger():
    def __init__(self, network, channel):
        """
        Initialize a new IRC Logger instance

        Args:
            network(str): The IRC network name
            channel(str): The channel being logged
        """
        # Load the logger configuration file
        self.config = self.config()
        self.config = self.config['IRC']

        # Set our network and channel
        self.network = network
        self.channel = channel

        # Set the default timestamp format
        self.timestamp_format = self.config['TimestampFormat']

        # A logfile should be defined in the extending classes
        self.logfile = None

    def log_message(self, nick, message):
        """
        Log a new channel message entry

        Args:
            nick(str):    IRC Nick of the message sender
            message(str): The message to be logged
        """
        log_entry = self.get_timestamp() + " <%s> %s" % (nick, message)
        self.logfile.write(log_entry + "\n")

    def log_action(self, nick, action):
        """
        Log a new channel action entry

        Args:
            nick(str):   IRC Nick of the message sender
            action(str): The action to be logged
        """
        log_entry = self.get_timestamp() + " * %s %s" % (nick, action)
        self.logfile.write(log_entry + "\n")

    def log_join(self, source):
        """
        Log a new channel join entry

        Args:
            source: Connection source
        """
        log_entry = self.get_timestamp() + "{nick} ({hostmask}) has joined".format(nick=source.nick, hostmask=source)
        self.logfile.write(log_entry + "\n")

    def log_part(self, nick, message=None):
        """
        Log a channel part entry

        Args:
            nick(str): IRC Nick of the parting user
            message(str or None): The users parting message
        """
        log_entry = self.get_timestamp() + "{nick} has left ({message})".format(nick=nick, message=message or "")
        self.logfile.write(log_entry + "\n")

    def log_quit(self, nick, message=None):
        """
        Log a channel part entry

        Args:
            nick(str): IRC Nick of the quitting user
            message(str or None): The users quit message
        """
        log_entry = self.get_timestamp() + "{nick} has quit ({message})".format(nick=nick, message=message or "")
        self.logfile.write(log_entry + "\n")

    def get_timestamp(self, timestamp_format=None):
        """
        Returns a formatted timestamp

        Args:
            timestamp_format(str): strftime format to use, defaults to format specified in config

        Returns:
            str
        """
        if timestamp_format:
            return time.strftime(timestamp_format, time.localtime(time.time()))

        return time.strftime(self.timestamp_format, time.localtime(time.time()))

    @staticmethod
    def config():
        """
        Static method that returns the logger configuration

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
    def __init__(self, network, channel):
        """
        Initialize a new IRC Channel Logger instance

        Args:
            network(str): The IRC network name
            channel(str): The channel being logged
        """
        super().__init__(network, channel)

        # Set our base path
        self.base_path    = str(self.config['LogPath']).rstrip("/") + "/%s/" % self.network.name
        self.logfile_name = self.channel.name + ".log"
        self.logfile_path = self.base_path + self.logfile_name

        # Make sure our logfile directory exists
        os.makedirs(self.base_path, 0o0750, True)

        # Open the logfile in append+read mode
        self.logfile = open(self.logfile_path, "a+")


class IRCQueryLogger(_IRCLogger):
    """
    Writes query messages and actions to the IRC query logfile
    """
    def __init__(self, network, nick):
        """
        Initialize a new IRC Query Logger instance

        Args:
            network(str): The IRC network name
            nick(str):    The IRC Nick of the user who is being query logged
        """
        super().__init__(network, nick)
        self.nick = nick

        # Set our base path
        self.base_path    = str(self.config['LogPath']).rstrip("/") + "/%s/queries/" % self.network.name
        self.logfile_name = self.nick + ".log"
        self.logfile_path = self.base_path + self.logfile_name

        # Make sure our logfile directory exists
        os.makedirs(self.base_path, 0o0750, True)

        # Open the logfile in append+read mode
        self.logfile = open(self.logfile_path, "a+")

    def log_message(self, message, nick=None):
        """
        Log a new query message entry

        Args:
            message(str): The message to be logged
            nick(str):    IRC Nick of the message sender
        """
        if nick:
            return super().log_message(nick, message)

        return super().log_message(self.nick, message)

    def log_action(self, action, nick=None):
        """
        Log a new channel action entry

        Args:
            action(str): The action to be logged
            nick(str):   The IRC Nick of the user who is being query logged
        """
        if nick:
            return super().log_action(nick, action)

        return super().log_message(self.nick, action)