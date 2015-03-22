import logging
from . import Datetime


class Commands:
    """
    IRC Commands for the Datetime module
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
        self.log = logging.getLogger('nano.modules.datetime.irc.commands')

    def command_date(self, args, opts, irc, source, public, **kwargs):
        """
        Return the current formatted date
        """
        return self.datetime.date()

    def command_time(self, args, opts, irc, source, public, **kwargs):
        """
        Return the current formatted time
        """
        return self.datetime.time()