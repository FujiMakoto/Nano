# !/usr/bin/env python3
"""
net_irc.py: Establish a new IRC connection
"""
import re
import shlex
from html.parser import unescape
from configparser import ConfigParser
import irc.bot
import irc.strings
from commands import IRCCommands
from language import Language

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class NanoIRC(irc.bot.SingleServerIRCBot):
    """
    Establishes a new connection to the configured IRC server
    """
    def __init__(self, channel, nickname, server, port=6667):
        """
        Initialize a new Nano IRC instance

        Args:
            channel(str):  The channel to join
            nickname(str): The nick to use
            server(str):   The server to connect to
            port(int):     The server port number
        """
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.lang    = Language()

        # Load our IRC Commands
        self.commands = IRCCommands(self.connection)
        self.command_pattern = re.compile("^>>>( )?[a-zA-Z]+")

    def on_nicknameinuse(self, c, e):
        """
        If our nick is in use on connect, append an underscore to it and try again
        """
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        """
        Join our specified channel once we get a welcome to the server
        """
        c.join(self.channel)

    def on_privmsg(self, c, e):
        """
        Handle private messages / queries
        """
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.lang.set_name(source[1], e.source.nick)

        return self.execute_command(e.arguments[0], c, e)

        # Get our reply
        reply = self.lang.get_reply(source[1], e.arguments[0])

        if reply:
            # Apply some formatting and parsing
            reply = self.html_to_control_codes(reply)

            # Send our response to the querying user
            c.privmsg(e.source.nick, reply)

    def on_pubmsg(self, c, e):
        """
        Handle channel messages
        """
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.lang.set_name(source[1], e.source.nick)

        # Are we trying to call a command directly?
        if self.command_pattern.match(e.arguments[0]):
            reply = self.execute_command(e.arguments[0], c, e)

            # If we received a response, send it to the channel
            if reply:
                c.privmsg(self.channel, reply)

            return

        # Get our reply
        reply = self.lang.get_reply(source[1], e.arguments[0])

        if reply:
            # Apply some formatting and parsing
            reply = self.html_to_control_codes(reply)

            # Send our response to the channel
            c.privmsg(self.channel, reply)

    def execute_command(self, command_string, c, e):
        """
        Execute an IRC command
        """
        # Strip the trigger and split the command string
        command_string = command_string.lstrip(">>>").strip()
        command_string = shlex.split(command_string)

        # Make sure the method exists
        try:
            command = getattr(self.commands, "command_" + command_string[0])
        except AttributeError:
            print('Function not found "%s" (%s)' % (command_string[0], " ".join(command_string[1:])))
            return

        # Make sure this is actually a function, not a variable
        if not callable(command):
            print("Attempted to call a variable")
            return

        # Attempt to execute the command
        try:
            command(*command_string[1:])
        except Exception:
            return

    @staticmethod
    def html_to_control_codes(message):
        """
        Replace accepted HTML formatting with control codes and strip any excess HTML that remains

        Args:
            message(str): The message to parse

        Returns:
            str: The IRC formatted string
        """
        # Parse bold text
        message = re.sub("(<strong>|<\/strong>)", "\x02", message, 0, re.UNICODE)

        # Strip any HTML formatting IRC protocol does not support
        message = re.sub('<[^<]+?>', '', message)

        # Unescape any HTML entities
        message = unescape(message)

        return message

    @staticmethod
    def load_config(network=None):
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