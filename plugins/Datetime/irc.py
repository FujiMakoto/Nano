import logging
from . import Datetime


class Commands:
    """
    IRC Commands for the Datetime plugin
    """
    commands_help = {
        'main': [
            'Provides various date and time services.',
            'Available commands: <strong>date, time</strong>'
        ],

        'date': [
            'Returns the current date.',
        ],

        'time': [
            'Returns the current time.',
        ],
    }

    def __init__(self):
        """
        Initialize a new Datetime Commands instance
        """
        self.datetime = Datetime()
        self.log = logging.getLogger('nano.plugins.datetime.irc.commands')

    def command_date(self, command):
        """
        Return the current formatted date

        Args:
            command(src.Command): The IRC command instance
        """
        return self.datetime.date()

    def command_time(self, command):
        """
        Return the current formatted time

        Args:
            command(src.Command): The IRC command instance
        """
        return self.datetime.time()