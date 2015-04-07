import logging
from configparser import ConfigParser
from .plugin import URL


class Commands:
    """
    IRC Commands for the URL plugin
    """
    commands_help = {
        'main': [
            'Parses titles and other attributes of URL\'s.',
            'Available commands: <strong>title</strong>'
        ],

        'title': [
            'Returns the title of the specified web page.',
            'Syntax: title <strong><url></strong>'
        ],
    }

    def __init__(self, plugin):
        """
        Initialize a new URL Commands instance
        """
        self.plugin = plugin
        self.url = URL()
        self.log = logging.getLogger('nano.plugins.url.irc.commands')

    def command_title(self, command):
        """
        Returns the title of a web page
        Syntax: url title <url>

        Args:
            command(src.Command): The IRC command instance
        """
        # Format the URL title?
        formatted = True
        if 'formatted' in command.opts:
            if command.opts['formatted'].lower() == "false":
                formatted = False

        # Retrieve and return the title
        title = self.url.get_title_from_url(command.args[0], formatted)

        if title:
            return title

        return "Sorry, I couldn't retrieve a valid web page title for the URL you gave me."


class Events:
    """
    IRC Events for the URL plugin
    """
    def __init__(self, plugin):
        """
        Initialize a new URL Events instance
        """
        self.plugin = plugin
        self.url = URL()
        self.log = logging.getLogger('nano.plugins.url.irc.events')
        self.parse_messages = self.plugin.config.getboolean('URL', 'AutoParseTitles')

    def on_public_message(self, event, irc):
        """
        Parse a public message for a URL and return its title if found

        Args:
            event(irc.client.Event): The IRC event instance
            irc(src.NanoIRC): The IRC connection instance
        """
        if not self.parse_messages:
            self.log.debug('[PUBMSG] Message parsing disabled, skipping')
            return

        self.log.debug('[PUBMSG] Searching message for URL\'s to parse')
        title = self.url.get_title_from_message(event.arguments[0])

        return title