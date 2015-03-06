"""
commands.py
"""
import re

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class IRCCommands:
    def __init__(self, connection):
        self.connection = connection
        """:type : irc.client.ServerConnection"""

    def command_kick(self, channel, nick, reason=None):
        self.connection.kick(channel, nick, reason)

    def command_test(self, message):
        print("Success! %s" % message)