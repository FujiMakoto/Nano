import logging
from plugins.exceptions import NotEnoughArgumentsError, InvalidSyntaxError
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

    def __init__(self, plugin):
        """
        Initialize a new auth Commands instance

        Args:
            plugin(src.plugins.Plugin): The plugin instance
        """
        self.plugin = plugin
        self.google = Google(self.plugin)
        self.log = logging.getLogger('nano.plugins.google')

    def command_search(self, command):
        """
        Perform a search query and returns the top results
        Syntax: google search <query>

        Args:
            command(src.Command): The IRC command instance
        """
        if not len(command.args):
            raise NotEnoughArgumentsError(command, 1)

        # How many results are we retrieving?
        results = 4
        if 'results' in command.opts:
            try:
                results = abs(int(command.opts['results']))
            except ValueError:
                raise InvalidSyntaxError(command, 'Invalid results number specified. Syntax: <strong>{syntax}</strong>')

        return self.google.search(' '.join(command.args), results)

    def command_lucky(self, command):
        """
        Perform a search query and return the first result
        Syntax: google lucky <query>

        Args:
            command(src.Command): The IRC command instance
        """
        if not len(command.args):
            raise NotEnoughArgumentsError(command, 1)

        return self.google.lucky(' '.join(command.args))
