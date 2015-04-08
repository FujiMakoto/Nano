"""
nano_cli.py: Establish a new CLI session
"""
import os
import logging
from interfaces.cli.shell import NanoShell


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
        self.nano = nano
        # Logging
        self.log = logging.getLogger('nano.cli')

        # Bind plugins
        if self.nano.plugins:
            self.log.debug('Binding plugins to CLI session ({id})'.format(id=id(self.nano.plugins)))
        else:
            self.log.debug('Not binding any plugins to CLI session')
        self.plugins = self.nano.plugins

        # Bind language
        if self.nano.language:
            self.log.debug('Binding language to CLI session ({id})'.format(id=id(self.nano.language)))
        else:
            self.log.debug('Not binding any language to CLI session')
        self.lang = self.nano.language

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
            self.log.debug('No response received')

    def start(self, command=None):
        """
        Starts the shell interpreter

        Args:
            command(None or str): Executes the single command provided. Defaults to None (regular shell mode)
        """
        # Are we executing a single command?
        if command:
            NanoShell(self.nano, self).onecmd(command)

        # Otherwise, drop into the shell interpreter in a command loop
        os.system('clear')
        while True:
            NanoShell(self.nano, self).cmdloop()

    def get_replies(self, message):
        """
        Query available sources for a reply to a message

        Args:
            message(str): The message to parse

        Returns:
            list, tuple, str or None
        """
        self.log.debug('Querying language engine for a response')
        replies = self.lang.get_reply('!cli', message)

        # Handle / deliver the replies
        self._handle_replies(replies)
        return