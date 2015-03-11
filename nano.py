#!/usr/bin/env python3.4
"""
net_irc.py: Establish an IRC connection
"""
from net_irc import NanoIRC
from modules import Network, Channel
# from database import DbSession
# from database.models import Network, Channel

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Nano:

    @staticmethod
    def irc():
        # Fetch our autojoin networks
        net = Network()
        networks = net.all()

        for network in networks:
            # Fetch our autojoin channels
            chan = Channel()
            channels = chan.all(network)

            # @TODO: Add proper multi-channel support
            for channel in channels:
                nano_irc = NanoIRC(network, channel)
                nano_irc.start()


def main():
    Nano.irc()


if __name__ == "__main__":
    main()