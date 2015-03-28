import logging
from .webster import CollegiateDictionary, WordNotFoundException, InvalidAPIKeyException

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Dictionary:
    """
    If you don't know what a dictionary is, look it up in the dictionary
    """
    def __init__(self, api_key=None):
        """
        Initialize a new Dictionary Plugin instance
        """
        self.log = logging.getLogger('nano.plugins.dictionary')
        self.dictionary = CollegiateDictionary(api_key)

    def define(self, word, max_definitions=3):
        """
        Fetch definitions for the specified word

        Args:
            word(str): The word to define
            max_definitions(int): The maximum number of definitions to retrieve. Defaults to 3

        Returns:
            list
        """
        self.log.info('Looking up the definition of: ' + word)
        # Attempt to fetch the words definition
        try:
            definitions = []
            for entry in self.dictionary.lookup(word):
                for definition, examples in entry.senses:
                    definitions.append((entry.word, entry.function, definition))
        except WordNotFoundException:
            self.log.info('No definition for {word} found'.format(word=word))
            definitions = []
        except InvalidAPIKeyException:
            self.log.error('Invalid API key defined in Dictionary configuration')
            definitions = []

        return definitions[:max_definitions]