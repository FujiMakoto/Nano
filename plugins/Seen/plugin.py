import re
import logging
import datetime as _datetime
import dateutil.parser
import time
from humanize import naturaltime
from boltons.jsonutils import reverse_iter_lines


class Seen:
    """
    User first / last seen commands
    """
    _DEFAULT_PATTERNS = [
        re.compile('^\[(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] <(?P<name>\S+?)> (?P<message>.+)$'),
        re.compile('^\[(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \* (?P<name>\S+?) (?P<message>.+)$')
    ]

    def __init__(self, message_patterns=_DEFAULT_PATTERNS):
        """
        Initialize a new Seen instance

        Args:
            message_patterns(list): A list of regex message patterns to attempt to match
        """
        self.log = logging.getLogger('nano.plugins.seen')
        self.message_patterns = message_patterns

    def _iterate_lines(self, name, logfile):
        """
        Args:
            name(str): The name to search for
            logfile(_io.TextIOWrapper): The opened logfile

        Returns:
            SeenMessage
        """
        for line in logfile:
            # Loop through our message patterns and attempt to find a match
            for pattern in self.message_patterns:
                match = pattern.match(line)
                if match:
                    break
            else:
                continue

            # If we have a match, get the attributes from it
            line_datetime = match.group('datetime')
            line_name     = match.group('name')
            line_message  = match.group('message')

            # Does our name match?
            if line_name.lower() == name.lower():
                self.log.info('Match found for {name}'.format(name=name))
                break
            continue
        else:
            raise NotSeenError

        return line_datetime, line_name, line_message

    def first(self, name, logfile):
        """
        When a specified user was first seen

        Args:
            name(str): The name to search for
            logfile(str): Path to the logfile to open and scan

        Returns:
            SeenMessage
        """
        self.log.info('Attempting to find the first logged message by {name}'.format(name=name))
        with open(logfile, 'rU') as logfile:
            return SeenMessage(*self._iterate_lines(name, logfile))

    def last(self, name, logfile):
        """
        When a specified user was first seen

        Args:
            name(str): The name to search for
            logfile(str): Path to the logfile to open and scan

        Returns:
            tuple of str
        """
        self.log.info('Attempting to find the last logged message by {name}'.format(name=name))
        with open(logfile, 'rU') as logfile:
            return SeenMessage(*self._iterate_lines(name, reverse_iter_lines(logfile)))


class SeenMessage:
    """
    Seen message metadata object
    """
    def __init__(self, datetime, name, message):
        """
        Initialize a new Seen Message metadata instance

        Args:
            datetime(str or datetime.datetime): Either a raw datetime string, or a pre-parsed datetime instance
            name(str): The name of the person being searched for
            message(str): The message that was matched
        """
        self.datetime = dateutil.parser.parse(datetime) if not isinstance(datetime, _datetime.datetime) else datetime
        now = _datetime.datetime.fromtimestamp(time.mktime(time.localtime(time.time())))
        self.timedelta = naturaltime(now - self.datetime)
        self.name = name
        self.message = message


class NotSeenError(Exception):
    pass