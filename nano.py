#!/usr/bin/env python3.4
"""
net_irc.py: Establish an IRC connection
"""
import logging
from configparser import ConfigParser
from net_irc import NanoIRC
from modules import Network, Channel
# from database import DbSession
# from database.models import Network, Channel

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Nano:
    def __init__(self):
        # Load our configuration
        self.config = ConfigParser()
        self.config.read('config/nano.cfg')

        # Define our parent logging namespace and get our log level / format
        self.log = logging.getLogger('nano')
        self.log_formatter = logging.Formatter("[%(asctime)s] %(levelname)s.%(name)s: %(message)s",
                                               self.config['System']['LogFormat'])

        self.log_level = getattr(logging, str(self.config['System']['LogLevel']).upper(), None)
        if not isinstance(self.log_level, int):
            self.log_level = logging.NOTSET

        self.log.setLevel(self.log_level)

        # Set up our console logger
        console_logger = logging.StreamHandler()
        console_logger.setLevel(self.log_level)
        console_logger.setFormatter(self.log_formatter)
        self.log.addHandler(console_logger)

        # Set up our file logger
        if self.config.getboolean('System', 'LogToFile'):
            log_path = self.config['System']['LogPath']
            file_logger = logging.FileHandler(log_path)
            file_logger.setLevel(self.log_level)
            file_logger.setFormatter(self.log_formatter)
            self.log.addHandler(file_logger)

    def irc(self):
        # Fetch our autojoin networks
        net = Network()
        networks = net.all()

        for network in networks:
            self.log.info('Connecting to Network: ' + network.name)
            # Fetch our autojoin channels
            chan = Channel()
            channels = chan.all(network)

            # @TODO: Add proper multi-channel support
            for channel in channels:
                nano_irc = NanoIRC(network, channel)
                nano_irc.start()


def main():
    nano = Nano()
    nano.irc()


if __name__ == "__main__":
    main()