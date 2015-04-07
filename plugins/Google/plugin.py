import logging
from math import ceil
from .PyGoogle import PyGoogle


class Google:
    """
    Perform Google search queries
    """
    def __init__(self, plugin):
        """
        Initialize a new Google instance
        """
        # Get the plugin configuration
        self.log = logging.getLogger('nano.plugins.google')
        self.plugin = plugin
        self.enabled = self.plugin.config.getboolean('Plugin', 'Enabled')
        self.result_limit = self.plugin.config.getint('Search', 'MaxResults')

    def _search(self, query, max_results):
        """
        Execute a search query

        Args:
            query(str): The search query to execute
            max_results(int): The number of search results to return

        Returns:
            list, dict or None
        """
        # Set up PyGoogle and fetch our results
        max_results = min(max_results, self.result_limit)
        self.log.info('Retrieving {max} results for the search query: {query}'.format(max=max_results, query=query))
        pages = ceil(max_results / 8)
        google = PyGoogle(query, self.plugin.config, pages)
        results = google.search()

        # Did we not get any results?
        if not results:
            return None

        # Do we only want the first result?
        if max_results == 1:
            return results.pop(0)

        # Return our requested results
        return results[:max_results]

    def _format_result(self, result):
        """
        Format a search query result

        Args:
            result(dict): The title/url dict search result

        Returns:
            str
        """
        self.log.debug('Formatting search result: ' + str(result))
        for title, url in result.items():
            return "<strong>" + title + "</strong>: " + url

    def search(self, query, max_results=4):
        """
        Perform a Google search on the specified query and returns the top 4 results

        Args:
            query(str): The search query to execute

        Returns:
            str
        """
        self.log.info('Executing Google search query')
        # Are we actually requesting a lucky search?
        if max_results == 1:
            return self.lucky(query)

        # Execute the search query
        results = self._search(query, max_results)

        # Did we not get any results?
        if not results:
            return "Sorry, your search query did not return anything."

        # Format our results
        formatted_results = []
        for result in results:
            formatted_results.append(self._format_result(result))

        # Return our joined results
        return ' | '.join(formatted_results)

    def lucky(self, query):
        self.log.info('Executing Google lucky query')
        """
        Perform a Google search on the specified query and return the first result only

        Args:
            query(str): The search query to execute

        Returns:
            str
        """
        # Execute the search query
        result = self._search(query, 1)

        # Did we not get a result?
        if not result:
            return "Sorry, your search query did not return anything."

        # Return the formatted result
        return self._format_result(result)