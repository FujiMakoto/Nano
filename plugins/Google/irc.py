import logging
from .module import Google


class Commands:
    """
    IRC Commands for the Google module
    """
    commands_help = {
        'main': [
            'Performs Google search queries.',
            'Available commands: <strong>search, lucky</strong>'
        ],

        'search': [
            'Perform a search query and returns the top results.',
            'Syntax: search <strong><query></strong>'
        ],

        'lucky': [
            'Perform a search query and return the first result.',
            'Syntax: lucky <strong><query></strong>'
        ],
    }

    def __init__(self):
        """
        Initialize a new auth Commands instance
        """
        self.google = Google()
        self.log = logging.getLogger('nano.modules.google')

    def command_search(self, args, opts, irc, source, public, **kwargs):
        """
        Perform a search query and returns the top results
        """
        # How many results are we retrieving?
        results = 4
        if 'results' in opts:
            results = abs(int(opts['results']))

        return self.google.search(' '.join(args), results)

    def command_lucky(self, args, opts, irc, source, public, **kwargs):
        """
        Perform a search query and return the first result
        """
        return self.google.lucky(' '.join(args))
