import logging
from src.plugins import PluginNotLoadedError
from src.commander import Commander, Command

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class IRCCommander(Commander):
    """
    IRC Command and Event dispatcher
    """
    def __init__(self, connection):
        """
        Initialize a new IRC Commander instance
        """
        super().__init__(connection)
        # Initialize commander
        self.log = logging.getLogger('nano.irc.commander')
        self.command = IRCCommand

    def execute(self, command_string, **kwargs):
        """
        Attempt to execute the specified command

        Args:
            command_args(str): The command to execute
            irc(src.NanoIRC): The active NanoIRC instance
            source(str): Hostmask of the requesting client
            public(bool): This command was executed from a public channel

        Returns:
            list, tuple, str or None: Returns replies to send to the client, or None if nothing should be returned
        """
        print(__name__)
        # Command prefixes
        admin_prefix = "admin_command_"
        user_prefix  = "user_command_"

        # Source / public
        source = kwargs['source']
        public = kwargs['public']

        # Parse our command string into names, arguments and options
        try:
            args, opts = self._parse_command_string(command_string)
            plugin, command, args, help_command = self._parse_command_arguments(args)
        except PluginNotLoadedError:
            return None

        # Are we executing a help command?
        if help_command:
            return self._help_execute(plugin, command)

        # Are we authenticated?
        if self.auth.check(source.host, self.connection.network):
            user = self.auth.user(source.host, self.connection.network)

            # If we're an administrator, attempt to execute an admin command
            if user.is_admin:
                response = self._execute(command, plugin, args, opts, source, public, admin_prefix)
                if response:
                    return response

            # Attempt to execute an unprivileged user command
            response = self._execute(command, plugin, args, opts, source, public, user_prefix)
            if response:
                return response

        # Attempt to execute a public command
        return self._execute(command, plugin, args, opts, source, public)

    def event(self, event_name, event):
        """
        Fire IRC events for loaded plugins

        Args:
            event_name(str): The name of the event being fired
            event(irc.client.Event): The IRC event instance

        Returns:
            list
        """
        # Make sure we're not executing a command
        if self.trigger_pattern.match(event.arguments[0]):
            self.log.debug('Not firing events for command requests')
            return

        self.log.debug('Firing ' + self._methodToName[event_name])

        # Loop through and execute our events
        replies = []
        for plugin_name, plugin in self.connection.plugins.all().items():
            if plugin.has_irc_events():
                event_method = plugin.get_irc_event(event_name)
                if callable(event_method):
                    event_replies = event_method(event, self.connection)
                    if event_replies:
                        replies.append(event_replies)

        self.log.debug('Returning event replies: ' + str(replies))
        return replies


class IRCCommand(Command):
    """
    An IRC command
    """
    def __init__(self, irc, args, opts, **kwargs):
        """
        Initialize a Command

        Args:
            args(list): Any command arguments
            opts(list): Any command options
            source(irc.client.NickMask): The client calling the command
            public(bool): Whether or not the command was called from a public channel
        """
        super().__init__(irc, args, opts, **kwargs)
        self.log = logging.getLogger('nano.irc.command')
        self.log.info('Setting up a new IRC Command instance')

        # Set the client source
        try:
            self.source = kwargs['source']
            self.public = kwargs['public']
        except NameError:
            raise SyntaxError('The IRCCommand instance requires the source and public arguments to be set')

        # Event holders
        self._whois = []

    def deliver_response(self, response):
        """
        Deliver a response message (intended to be utilized primarily for events)

        Args:
            response(list, tuple or str): The response message(s) to deliver
        """
        self.connection.postmaster.deliver(response, self.source, self.connection.channel, self.public)

    def bind_whois_event(self, targets, callback):
        """
        Fire an IRC WHOIS command and call the callback once a response is received

        Args:
            targets(str): The target(s) to WHOIS
            callback: The method to fire on WHOIS response
        """
        # Event methods
        def whois_start(connection, event):
            """
            Handles a single WHOIS response event

            Args:
                connection(irc.client.ServerConnection): The active IRC server connection
                event(irc.client.Event): The event response data
            """
            # Unbind our event listener
            self.connection.connection.remove_global_handler('whoisuser', whois_start)
            self.log.debug('WHOIS response: ' + str(event.arguments))

            # Append our whois data
            if len(event.arguments):
                self._whois.append(event.arguments)

        def whois_end(connection, event):
            """
            Handles the end of a WHOIS event

            Args:
                connection(irc.client.ServerConnection): The active IRC server connection
                event(irc.client.Event): The event response data
            """
            # Unbind our event listener
            self.connection.connection.remove_global_handler('endofwhois', whois_end)
            self.log.debug('End of WHOIS response')

            # Fire our callback method and reset the event holder
            if not callable(callback):
                self.log.error('The callback supplied was not a valid callable method! Please review the documentation')

            callback(self, self._whois)
            self._whois = []

        # Bind and execute the events
        self.log.debug('Binding WHOIS events')
        self.connection.connection.add_global_handler('whoisuser', whois_start)
        self.connection.connection.add_global_handler('endofwhois', whois_end)

        self.log.debug('Executing WHOIS command')
        self.connection.connection.whois(targets)