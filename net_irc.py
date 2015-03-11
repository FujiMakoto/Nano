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
import irc.events
from modules import Commander
from language import Language

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
        self.network = network
        self.channel = channel
        self.lang    = Language()
        self.command = Commander()

        # Channel command pattern
        self.command_pattern = re.compile("^>>>( )?[a-zA-Z]+")

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

    def deliver_messages(self, messages, nick, channel, private=False):
        # Make sure we have a list of messages to iterate through
        if not isinstance(messages, list):
            messages = [messages]

        # Are we returning to a public channel or query by default?
        if private:
            default_destination = nick
        else:
            default_destination = channel.name

        # Iterate through our messages
        for message in messages:
            if isinstance(message, dict):
                # Split our destination and parse our message
                destination, message = message.popitem()
                message = self.html_to_control_codes(message)

                # Where are we sending the message?
                if destination == "private":
                    self.connection.privmsg(nick, message)
                elif destination == "private_notice":
                    self.connection.notice(nick, message)
                elif destination == "public_notice":
                    self.connection.notice(channel.name, message)
                elif destination == "public":
                    self.connection.privmsg(channel.name, message)
                else:
                    self.connection.privmsg(default_destination, message)
            else:
                message = self.html_to_control_codes(message)
                self.connection.privmsg(default_destination, message)

    def on_nicknameinuse(self, c, e):
        """
        If our nick is in use on connect, append an underscore to it and try again
        """
        # TODO: Ghost using nickserv if possible
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        """
        Join our specified channel once we get a welcome to the server
        """
        # TODO: Multi-channel support
        c.join(self.channel.name)

    def on_privmsg(self, c, e):
        """
        Handle private messages / queries
        """
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.lang.set_name(source[1], e.source.nick)

        # Are we trying to call a command directly?
        if self.command_pattern.match(e.arguments[0]):
            reply = self.execute_command(e.arguments[0], e.source, False)
        else:
            reply = self.lang.get_reply(source[1], e.arguments[0])

        if reply:
            # Deliver our messages
            self.deliver_messages(reply, e.source.nick, self.channel, True)

    def on_pubmsg(self, c, e):
        """
        Handle channel messages
        """
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.lang.set_name(source[1], e.source.nick)

        # Are we trying to call a command directly?
        if self.command_pattern.match(e.arguments[0]):
            reply = self.execute_command(e.arguments[0], e.source, True)
        else:
            reply = self.lang.get_reply(source[1], e.arguments[0])

        if reply:
            # Deliver our messages
            self.deliver_messages(reply, e.source.nick, self.channel)

    def on_quit(self, c, e):
        # TODO: Clear login sessions
        print(e.source.nick + " has quit!")

    def execute_command(self, command_string, source, public=True):
        """
        Execute an IRC command
        """
        # Strip the trigger and split the command string
        command_string = command_string.lstrip(">>>").strip()
        command_string = shlex.split(command_string)

        # Attempt to execute the command
        #return self.command.execute(command_string[0], command_string[1:], self, self.network, self.channel, source)
        try:
            reply = self.command.execute(command_string[0], command_string[1:], self, source, public)
            return reply
        except Exception as e:
            print(str(e))
            return
