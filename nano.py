#!/usr/bin/env python3.4
"""
Nano Launcher
"""
import logging
from configparser import ConfigParser
from src.interfaces import InterfaceManager
from src.plugins import PluginManager
from src.language import Language


class Nano:
    """
    Nano master class
    """
    def __init__(self):
        """
        Initialize a new Nano instance
        """
        # Load our configuration
        self.config = ConfigParser()
        self.config.read('config/system.cfg')
        self.interfaces = None
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

        # Load interfaces
        self.interfaces = InterfaceManager()
        self.interfaces.load_all()

        # Loud plugins
        if self.config.getboolean('Plugins', 'Enabled'):
            self.plugins = PluginManager(self.interfaces.all())
            self.plugins.load_all()

        # Load the language engine
        if self.config.getboolean('Language', 'Enabled'):
            self.language = Language(self.plugins)

    def start(self):
        """
        Start Nano by establishing connections on all enabled protocols and networks
        """
        # Fetch all our available interfaces minus the CLI interface
        interfaces = self.interfaces.all()
        interfaces.pop('cli')

        # TODO: Multiple interfaces are not actually supported yet. So, all we are really doing is calling IRC directly
        interfaces['irc'].start(self)

    def cli(self):
        """
        Launch the Nano administration shell
        """
        # TODO: If an argument is passed to the script (e.g. ./nano.py start), just execute that single command instead
        self.interfaces.get('cli').start(self)

# Launch the administration shell on script execution
if __name__ == "__main__":
    Nano().cli()