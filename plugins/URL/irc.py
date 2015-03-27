import logging
from configparser import ConfigParser
from .module import URL

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Commands:
    """
    IRC Commands for the URL module
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

    def __init__(self):
        """
        Initialize a new auth Commands instance
        """
        self.url = URL()
        self.log = logging.getLogger('nano.modules.url.irc.commands')

    def command_title(self, args, opts, irc, source, public, **kwargs):
        """
        Returns the title of a web page
        """
        # Format the URL title?
        formatted = True
        if 'formatted' in opts:
            if 'false' in opts['formatted'].lower():
                formatted = False

        # Retrieve and return the title
        title = self.url.get_title_from_url(args[0], formatted)

        if title:
            return title

        return "Sorry, I couldn't retrieve a valid web page title for the URL you gave me."


class Events:
    """
    IRC Events for the URL module
    """
    def __init__(self):
        """
        Initialize a new URL Events instance
        """
        self.url = URL()
        self.log = logging.getLogger('nano.modules.url.irc.events')
        self.config = ConfigParser()
        self.config.read('plugins/URL/module.cfg')
        self.parse_messages = self.config.getboolean('URL', 'AutoParseTitles')

    def on_public_message(self, event, irc):
        """
        Parse a public message for a URL and return its title if found

        Args:
            event(irc.client.Event): The IRC event instance
            irc(NanoIRC): The IRC connection instance
        """
        if not self.parse_messages:
            self.log.debug('[PUBMSG] Message parsing disabled, skipping')
            return

        self.log.debug('[PUBMSG] Searching message for URL\'s to parse')
        title = self.url.get_title_from_message(event.arguments[0])

        return title