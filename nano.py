#!/usr/bin/env python3.4
"""
net_irc.py: Establish an IRC connection
"""
import logging
from configparser import ConfigParser
from src.plugins import PluginManager
from src.language import Language
from src.nano_irc import NanoIRC
from src.network import Network
from src.cli.nano_cli import NanoCLI
from plugins import Channel

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
        self.config.read('config/system.cfg')
        self.plugins = None
        self.language = None

        # Define our parent logging namespace and get our log level / format
        self.log = logging.getLogger('nano')
        self.log_formatter = logging.Formatter("[%(asctime)s] %(levelname)s.%(name)s: %(message)s",
                                               self.config['ErrorLogging']['LogFormat'])

        # Console log level
        self.console_log_level = getattr(logging, str(self.config['ErrorLogging']['ConsoleLevel']).upper(), None)
        if not isinstance(self.console_log_level, int):
            self.console_log_level = logging.NOTSET

        self.log.setLevel(self.console_log_level)

        # Set up our console logger
        console_logger = logging.StreamHandler()
        console_logger.setLevel(self.console_log_level)
        console_logger.setFormatter(self.log_formatter)
        self.log.addHandler(console_logger)

        # File log level
        self.file_log_level = getattr(logging, str(self.config['ErrorLogging']['LogfileLevel']).upper(), None)
        if not isinstance(self.file_log_level, int):
            self.file_log_level = logging.NOTSET

        # Set up our file logger
        if self.config.getboolean('ErrorLogging', 'LogToFile'):
            log_path = self.config['ErrorLogging']['LogfilePath']
            file_logger = logging.FileHandler(log_path)
            file_logger.setLevel(self.file_log_level)
            file_logger.setFormatter(self.log_formatter)
            self.log.addHandler(file_logger)

        # Loud our plugins
        if self.config.getboolean('Plugins', 'Enabled'):
            self.plugins = PluginManager()
            self.plugins.load_all()

        # Load the language engine
        if self.config.getboolean('Language', 'Enabled'):
            self.language = Language(self.plugins)

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
                nano_irc = NanoIRC(network, channel, self.plugins, self.language)
                nano_irc.start()

    def cli(self):
        NanoCLI(self)


def main():
    nano = Nano()
    nano.cli()


if __name__ == "__main__":
    main()