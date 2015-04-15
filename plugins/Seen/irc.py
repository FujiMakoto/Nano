import logging
import random
from .plugin import Seen, NotSeenError
from plugins.exceptions import NotEnoughArgumentsError


class Commands:
    """
    IRC Commands for the Seen plugin
    """
    NOT_SEEN_RESPONSES = [
        "Hmm.. I don't think I've ever seen {name}.",
        "I have never seen {name} before.",
        "{name}? Who is that?",
        "{name}? What a funny name! I've never seen them before.",
        "{name}? That name's not familiar to me, sorry!"
    ]

    FIRST_SEEN_RESPONSES = [
        "I met {name} for the first time {timedelta}!",
        "I first met {name} around {timedelta}."
    ]

    LAST_SEEN_RESPONSES = [
        "I last saw {name} {timedelta}.",
        "I saw {name} {timedelta}.",
        "{name}? I saw them about {timedelta}",
        "I guess it was around {timedelta}."
    ]

    def __init__(self, plugin):
        """
        Initialize a new Seen Commands instance
        """
        self.log = logging.getLogger('nano.plugins.seen.irc.commands')
        self.plugin = plugin
        self.seen = Seen()

    def command_first(self, command):
        """
        Returns the first time a user was seen in a channel
        Syntax: seen first <nick>

        Args:
            command(src.commander.Command): The IRC command instance
        """
        if not command.public:
            return 'If you want to know when I first saw them, ask me in a public channel!'

        # Set name / logfile
        logfile = command.connection.channel_logger.logfile_path
        try:
            name = command.args[0].capitalize()
        except IndexError:
            raise NotEnoughArgumentsError

        # Are we asking when did we first see ourselves?
        if name.lower() == command.connection.network.nick.lower():
            return "Why are you asking me when I first met myself? You're a weird person!"

        # Have we seen this person?
        try:
            seen = self.seen.first(name, logfile)
        except NotSeenError:
            return random.choice(self.NOT_SEEN_RESPONSES).format(name=name)

        # Return a random first seen response
        return random.choice(self.FIRST_SEEN_RESPONSES).format(name=seen.name, timedelta=seen.timedelta)

    def command_last(self, command):
        """
        Returns the first time a user was seen in a channel
        Syntax: seen first <nick>

        Args:
            command(src.commander.Command): The IRC command instance
        """
        if not command.public:
            return 'If you want to know when I last saw them, ask me in a public channel!'

        # Set name / logfile
        logfile = command.connection.channel_logger.logfile_path
        try:
            name = command.args[0].capitalize()
        except IndexError:
            raise NotEnoughArgumentsError

        # Are we asking when did we last saw ourselves?
        if name.lower() == command.connection.network.nick.lower():
            return "Why are you asking me when I last saw myself? You're a weird person!"

        # Have we seen this person?
        try:
            seen = self.seen.last(name, logfile)
        except NotSeenError:
            return random.choice(self.NOT_SEEN_RESPONSES).format(name=name)

        # Return a random first seen response
        return random.choice(self.LAST_SEEN_RESPONSES).format(name=seen.name, timedelta=seen.timedelta)