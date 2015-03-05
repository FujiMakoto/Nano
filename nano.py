#!/usr/bin/env python3
"""
net_irc.py: Establish an IRC connection
"""
from net_irc import NanoIRC

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Nano:

    @staticmethod
    def irc():
        irc_config = NanoIRC.load_config()

        for network in irc_config.sections():
            # Get our configuration for this network
            config = irc_config[network]
            """:type : configparser.ConfigParser"""

            # If it's active and we should automatically connect to it..
            if config.getboolean(network, "Active") and config.getboolean(network, "AutoConnect"):
                nano_irc = NanoIRC(config["Channels"], config["Nick"], config["Server"], int(config["Port"]))
                nano_irc.start()


def main():
    Nano.irc()


if __name__ == "__main__":
    main()