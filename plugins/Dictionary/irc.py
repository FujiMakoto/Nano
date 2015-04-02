import logging
from configparser import ConfigParser
from plugins.exceptions import NotEnoughArgumentsError
from .plugin import Dictionary

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Commands:
    """
    IRC Commands for the Dictionary plugin
    """
    commands_help = {
        'main': [
            'Returns dictionary definitions.',
            'Available commands: <strong>define</strong>'
        ],

        'define': [
            'Looks up the definition of a word using the Merriam Webster dictionary.',
            'Syntax: define <strong><word></strong>'
        ],
    }

    def __init__(self):
        """
        Initialize a new Dictionary Commands instance
        """
        self.log = logging.getLogger('nano.plugins.dictionary.irc.commands')
        self.config = ConfigParser()
        self.config.read('plugins/Dictionary/plugin.cfg')
        self.dictionary = Dictionary(self.config['MerriamWebster']['ApiKey'])
        self.max_limit = self.config.getint('Dictionary', 'MaxDefinitions')
        self.max_default = self.config.getint('Dictionary', 'DefaultMaxDefinitions')

    def command_define(self, command):
        """
        Looks up the definition of a word using the Merriam Webster dictionary
        Syntax: dictionary define <word>

        Args:
            command(src.Command): The IRC command instance
        """
        if not len(command.args):
            raise NotEnoughArgumentsError(command, 1)

        # Do we have a definition limit option?
        max_definitions = self.max_default
        if 'max' in command.opts:
            max_definitions = min(abs(int(command.opts['max'])), self.max_limit)

        # Fetch our definitions
        word = ' '.join(command.args)
        self.log.info('Fetching up to {max} definitions for the word {word}'
                      .format(max=max_definitions, word=word))
        definitions = self.dictionary.define(word, max_definitions)

        if not definitions:
            return "Sorry, I couldn't find a definition for <strong>{word}</strong>".format(word=command.args[0])

        # Format our definitions
        formatted_definitions = []
        for index, definition in enumerate(definitions):
            if not formatted_definitions:
                formatted_definitions.append("<strong>{word}</strong> (<em>{pos}</em>) <strong>1:</strong> {definition}"
                                             .format(word=word, pos=definition[1], definition=definition[2]))
            else:
                formatted_definitions.append("<strong>{key}:</strong> {definition}"
                                             .format(key=index + 1, definition=definition[2]))

        self.log.debug('Returning formatted definitions: ' + str(formatted_definitions))
        return ' '.join(formatted_definitions)