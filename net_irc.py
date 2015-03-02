#! /usr/bin/env python
#
# Example program using irc.bot.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
irc.bot.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

    stats -- Prints some channel information.

    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.

    die -- Let the bot cease to exist.

    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr, log
import re
import html.parser
import nano


class NanoIRC(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.handler = nano.Handler(None)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.handler.set_name(source[1], e.source.nick)

        # Get our reply
        reply = self.handler.send(source[1], e.arguments[0], True)

        # Apply some formatting and parsing
        # Replace HTML <strong> tags with IRC bold codes
        reply = re.sub("(<strong>|<\/strong>)", "\x02", reply, 0, re.UNICODE)

        # Replace HTML entities
        hp = html.parser.HTMLParser()
        reply = hp.unescape(reply)

        c.privmsg(e.source.nick, reply)

    def on_pubmsg(self, c, e):
        # Get our hostmask to use as our name
        source = str(e.source).split("@", 1)
        self.handler.set_name(source[1], e.source.nick)

        # Get our reply
        reply = self.handler.send(source[1], e.arguments[0])

        # Apply some formatting and parsing
        # Replace HTML <strong> tags with IRC bold codes
        reply = re.sub("(<strong>|<\/strong>)", "\x02", reply, 0, re.UNICODE)

        # Replace HTML entities
        hp = html.parser.HTMLParser()
        reply = hp.unescape(reply)

        c.privmsg(self.channel, reply)

    def on_dccmsg(self, c, e):
        c.privmsg("You said: " + e.arguments[0])

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        import sys
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.privmsg(sys.argv[2], "--- Channel statistics ---")
                c.privmsg(sys.argv[2], "Channel: " + chname)
                users = list(chobj.users())
                users.sort()
                c.privmsg(sys.argv[2], "Users: " + ", ".join(users))
                opers = list(chobj.opers())
                opers.sort()
                c.privmsg(sys.argv[2], "Opers: " + ", ".join(opers))
                voiced = list(chobj.voiced())
                voiced.sort()
                c.privmsg(sys.argv[2], "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        else:
            c.notice(nick, "Not understood: " + cmd)


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