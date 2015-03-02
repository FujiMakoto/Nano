from configparser import ConfigParser
from .PyGoogle import PyGoogle


class Google():
    def __init__(self):
        # Get the module configuration
        self.config  = ConfigParser()
        self.config.read('modules/Google/module.cfg')
        self.enabled = self.config.getboolean('Module', 'Enabled')

    @staticmethod
    def lucky(query):
        """
        Perform a Google search on the specified query and return the first result only
        :param query: str: The search term
        :return:
        """
        pg = PyGoogle(query, 1)
        results = pg.search()

        # @TODO: Our response is a DICT, so it's NOT technically the first result. This is being improved later
        for title, url in results.items():
            title = title
            url = url
            break

        return "<strong>" + title + "</strong>: " + url