"""
nano_cli.py: Establish a new CLI session
"""
import os
import logging
from src.utilities import MessageParser
from .postmaster import Postmaster
from .commander import CLICommander
from .shell import NanoShell

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


# noinspection PyMethodMayBeStatic
class NanoCLI():
    """
    Sets up a new CLI session
    """
    def __init__(self, nano):
        """
        Initialize a new Nano CLI instance

        Args:
            nano(Nano): The master Nano class instance
        """
        # Logging
        self.log = logging.getLogger('nano.cli')

        # Bind plugins
        if nano.plugins:
            self.log.debug('Binding plugins to CLI session ({id})'.format(id=id(nano.plugins)))
        else:
            self.log.debug('Not binding any plugins to CLI session')
        self.plugins = nano.plugins

        # Bind language
        if nano.language:
            self.log.debug('Binding language to CLI session ({id})'.format(id=id(nano.language)))
        else:
            self.log.debug('Not binding any language to CLI session')
        self.lang = nano.language

        # Set up our CLICommander, Postmaster and MessageParser instances
        self.commander = CLICommander(self)
        self.postmaster = Postmaster(self)
        self.message_parser = MessageParser()

        # Set up shell
        os.system('clear')
        NanoShell(nano, self).cmdloop()

    def _handle_replies(self, replies):
        """
        Deliver replies

        Args:
            replies(list, tuple, str or None): The event replies to process
        """
        if replies:
            self.log.debug('Delivering response messages')
            self.postmaster.deliver(replies)
        else:
            print("\n")
            self.log.debug('No response received')

    def get_replies(self, message):
        """
        Query available sources for a reply to a message

        Args:
            message(str): The message to parse

        Returns:
            list, tuple, str or None
        """
        # Are we trying to call a command directly?
        if self.commander.trigger_pattern.match(message):
            self.log.info('Acknowledging command request')
            self._handle_replies(self.commander.execute(message))
            return

        self.log.debug('Querying language engine for a response')
        replies = self.lang.get_reply('!cli', message)

        # Handle / deliver the replies
        self._handle_replies(replies)
        return