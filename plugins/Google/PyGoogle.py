#!/usr/bin/python
"""
Google AJAX Search Module
http://code.google.com/apis/ajaxsearch/documentation/reference.html
Needs Python 3.4 or later
"""
import json
import sys
import urllib.parse
import urllib.request
import logging
import argparse
from math import ceil
from configparser import ConfigParser


__author__  = "Kiran Bandla, Makoto Fujikawa"
__version__ = "1.0"

# Web Search Specific Arguments
# http://code.google.com/apis/ajaxsearch/documentation/reference.html#_fonje_web
URL = 'http://ajax.googleapis.com/ajax/services/search/web?'

"""
SAFE
This optional argument supplies the search safety level which may be one of:
    * safe=active - enables the highest level of safe search filtering
    * safe=moderate - enables moderate safe search filtering (default)
    * safe=off - disables safe search filtering
"""
SAFE_ACTIVE     = "active"
SAFE_MODERATE   = "moderate"
SAFE_OFF        = "off"

"""
FILTER
This optional argument controls turning on or off the duplicate content filter:

    * filter=0 - Turns off the duplicate content filter
    * filter=1 - Turns on the duplicate content filter (default)

"""
FILTER_OFF  = 0
FILTER_ON   = 1

# Standard URL Arguments
# http://code.google.com/apis/ajaxsearch/documentation/reference.html#_fonje_args
"""
RSZ
This optional argument supplies the number of results that the application would like to receive.
A value of small indicates a small result set size or 4 results.
A value of large indicates a large result set or 8 results. If this argument is not supplied, a value of small is assumed.
"""
RSZ_SMALL = "small"
RSZ_LARGE = "large"

"""
HL
This optional argument supplies the host language of the application making the request.
If this argument is not present then the system will choose a value based on the value of the Accept-Language http header.
If this header is not present, a value of en is assumed.
"""


class PyGoogle:

    def __init__(self, query, config, pages=None, hl='en'):
        self.config = config
        self.pages  = pages or ceil(self.config.getint('Search', 'DefaultResults') / 8)
        self.query  = query
        self.filter = int(self.config.getboolean('Search', 'FilterDuplicates'))
        self.rsz    = RSZ_LARGE
        self.safe   = self.config['Search']['SafeSearch'].lower()
        self.hl     = hl
        self.__setup_logging(level=logging.INFO)

    def __setup_logging(self, level):
        logger = logging.getLogger('PyGoogle')
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(module)s %(levelname)s %(funcName)s| %(message)s'))
        logger.addHandler(handler)
        self.logger = logger

    def __search__(self, print_results=False):
        """
        Internal search query
        :param print_results: bool
        :return: list of results if successful or False otherwise
        """
        results = []
        for page in range(0, self.pages):
            rsz = 8
            if self.rsz == RSZ_SMALL:
                rsz = 4
            args = {'q': self.query,
                    'v': '1.0',
                    'start': page * rsz,
                    'rsz': self.rsz,
                    'safe': self.safe,
                    'filter': self.filter,
                    'hl': self.hl
                    }
            self.logger.debug('search: "%s" page# : %s' % (self.query, page))
            q = urllib.parse.urlencode(args)
            search_results = urllib.request.urlopen(URL + q)
            data = json.loads(search_results.read().decode('utf-8'))
            if 'responseStatus' not in data:
                self.logger.error('response does not have a responseStatus key')
                continue
            if data.get('responseStatus') != 200:
                self.logger.debug('responseStatus is not 200')
                self.logger.error('responseDetails : %s' % (data.get('responseDetails', None)))
                continue
            if print_results:
                if 'responseData' in data and 'results' in data['responseData']:
                    for result in data['responseData']['results']:
                        if result:
                            print('[%s]' % (urllib.parse.unquote(result['titleNoFormatting'])))
                            print(result['content'].strip("<b>...</b>").replace("<b>", '').replace("</b>", '').replace(
                                "&#39;", "'").strip())
                            print(urllib.parse.unquote(result['unescapedUrl']) + '\n')
                else:
                    # no responseData key was found in 'data'
                    self.logger.error('no responseData key found in response')
            results.append(data)
        return results

    def search(self):
        """
        Perform a Google search query and return the results as a dictionary
        :return: dict of Titles and URLs
        """
        results = []
        search_results = self.__search__()
        if not search_results:
            self.logger.info('No results returned')
            return results
        for data in search_results:
            if 'responseData' in data and 'results' in data['responseData']:
                for result in data['responseData']['results']:
                    if result and 'titleNoFormatting' in result:
                        title = urllib.parse.unquote(result['titleNoFormatting'])
                        results.append({title: urllib.parse.unquote(result['unescapedUrl'])})
            else:
                self.logger.error('no responseData key found in response')
                self.logger.error(data)
        return results

    def search_page_wise(self):
        """
        Get a dict of page-wise urls
        :return: dict
        """
        results = {}
        for page in range(0, self.pages):
            args = {'q': self.query,
                    'v': '1.0',
                    'start': page,
                    'rsz': RSZ_LARGE,
                    'safe': SAFE_OFF,
                    'filter': FILTER_ON,
                    }
            q = urllib.parse.urlencode(args)
            search_results = urllib.request.urlopen(URL+q)
            data = json.loads(search_results.read())
            urls = []
            if 'responseData' in data and 'results' in data['responseData']:
                for result in data['responseData']['results']:
                    if result and 'unescapedUrl' in result:
                        url = urllib.parse.unquote(result['unescapedUrl'])
                        urls.append(url)
            else:
                self.logger.error('no responseData key found in response')
            results[page] = urls
        return results

    def get_urls(self):
        """
        Get a list of result URLs
        :return: list
        """
        results = []
        search_results = self.__search__()
        if not search_results:
            self.logger.info('No results returned')
            return results
        for data in search_results:
            if data and 'responseData' in data and data['responseData']['results']:
                for result in data['responseData']['results']:
                    if result:
                        results.append(urllib.parse.unquote(result['unescapedUrl']))
        return results

    def get_result_count(self):
        """
        Get the number of results
        :return: int
        """
        temp = self.pages
        self.pages = 1
        result_count = 0
        search_results = self.__search__()
        if not search_results:
            return 0
        try:
            result_count = search_results[0]
            if not isinstance(result_count, dict):
                return 0
            result_count = result_count.get('responseData', None)
            if result_count:
                if 'cursor' in result_count and 'estimatedResultCount' in result_count['cursor']:
                    return result_count['cursor']['estimatedResultCount']
            return 0
        except Exception as e:
            self.logger.error(e)
        finally:
            self.pages = temp
        return result_count

    def display_results(self):
        """
        Prints results (for command line)
        """
        self.__search__(True)