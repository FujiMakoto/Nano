# !/usr/bin/env python3
"""
net_irc.py: Establish a new IRC connection
"""
import re
from html.parser import unescape
from configparser import ConfigParser
import irc.bot
import irc.strings
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
        :param channel: str: The channel to join
        :param nickname: str: The nick to use
        :param server: str: The server to connect to
        :param port: int: The server port number
        """
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.lang    = Language()

    def on_nicknameinuse(self, c, e):
        """
        If our nick is in use on connect, append an underscore to it and try again
        :param c:
        :param e:
        """
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        """
        Join our specified channel once we get a welcome to the server
        :param c:
        :param e:
        """
        c.join(self.channel)

    def on_privmsg(self, c, e):
        """
        Handle private messages / queries
        :param c:
        :param e:
        """
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.lang.set_name(source[1], e.source.nick)

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
        :param c:
        :param e:
        """
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.lang.set_name(source[1], e.source.nick)

        # Get our reply
        reply = self.lang.get_reply(source[1], e.arguments[0])

        if reply:
            # Apply some formatting and parsing
            reply = self.html_to_control_codes(reply)

            # Send our response to the channel
            c.privmsg(self.channel, reply)

    @staticmethod
    def html_to_control_codes(message):
        """
        Replace accepted HTML formatting with control codes and strip any excess HTML that remains
        :param message: The message to parse
        :return: str: The IRC formatted string
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
        :rtype: ConfigParser
        """
        config = ConfigParser()
        config.read('config/irc.cfg')

        if network:
            return config[network]

        return config