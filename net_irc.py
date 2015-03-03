# !/usr/bin/env python3
"""
net_irc.py: Establish an IRC connection
"""
import re
import html.parser
import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr, log
import nano

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
        self.handler = nano.Handler(None)

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
        self.handler.set_name(source[1], e.source.nick)

        # Get our reply
        reply = self.handler.send(source[1], e.arguments[0], True)

        # Apply some formatting and parsing
        # Replace HTML <strong> tags with IRC bold codes
        if reply:
            reply = re.sub("(<strong>|<\/strong>)", "\x02", reply, 0, re.UNICODE)

            # Replace HTML entities
            hp = html.parser.HTMLParser()
            reply = hp.unescape(reply)

        c.privmsg(e.source.nick, reply)

    def on_pubmsg(self, c, e):
        """
        Handle channel messages
        :param c:
        :param e:
        """
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.handler.set_name(source[1], e.source.nick)

        # Get our reply
        reply = self.handler.send(source[1], e.arguments[0])

        # Apply some formatting and parsing
        # Replace HTML <strong> tags with IRC bold codes
        if reply:
            reply = re.sub("(<strong>|<\/strong>)", "\x02", reply, 0, re.UNICODE)

            # Replace HTML entities
            hp = html.parser.HTMLParser()
            reply = hp.unescape(reply)

        if reply == "ERR: No Reply Matched":
            reply = None

        if reply:
            c.privmsg(self.channel, reply)


def main():
    import configparser
    import logging

    # Logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
    log.addHandler(ch)

    # Load our configuration
    config = configparser.ConfigParser()
    config.read('config/irc.cfg')

    # Set our server information
    server   = config['Network']['Server']
    port     = int(config['Network']['Port'])
    channel  = config['Network']['Channel']
    nickname = 'Nano'

    bot = NanoIRC(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()