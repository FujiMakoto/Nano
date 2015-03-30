import logging
from .plugin import Google


class Commands:
    """
    IRC Commands for the Google plugin
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
        self.log = logging.getLogger('nano.plugins.google')

    def command_search(self, command):
        """
        Perform a search query and returns the top results

        Args:
            command(src.Command): The IRC command instance
        """
        # How many results are we retrieving?
        results = 4
        if 'results' in command.opts:
            results = abs(int(command.opts['results']))

        return self.google.search(' '.join(command.args), results)

    def command_lucky(self, command):
        """
        Perform a search query and return the first result

        Args:
            command(src.Command): The IRC command instance
        """
        return self.google.lucky(' '.join(command.args))
