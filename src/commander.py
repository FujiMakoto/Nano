import re
import shlex
import logging
from .plugins import PluginNotLoadedError
from .auth import Auth

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Commander:
    """
    IRC Command and Event dispatcher
    """
    EVENT_JOIN = "on_join"
    EVENT_PART = "on_part"
    EVENT_QUIT = "on_quit"
    EVENT_KICK = "on_kick"
    EVENT_PUBMSG = "on_public_message"
    EVENT_PRIVMSG = "on_private_message"
    EVENT_PUBACTION = "on_public_action"
    EVENT_PRIVACTION = "on_private_action"
    EVENT_PUBNOTICE = "on_public_notice"
    EVENT_PRIVNOTICE = "on_private_notice"

    _methodToName = {
        EVENT_JOIN: 'EVENT_JOIN',
        EVENT_PART: 'EVENT_PART',
        EVENT_QUIT: 'EVENT_QUIT',
        EVENT_KICK: 'EVENT_KICK',
        EVENT_PUBMSG: 'EVENT_PUBMSG',
        EVENT_PRIVMSG: 'EVENT_PRIVMSG',
        EVENT_PUBACTION: 'EVENT_PUBACTION',
        EVENT_PRIVACTION: 'EVENT_PRIVACTION',
        EVENT_PUBNOTICE: 'EVENT_PUBNOTICE',
        EVENT_PRIVNOTICE: 'EVENT_PRIVNOTICE',
    }
    _nameToMethod = {
        'EVENT_JOIN': EVENT_JOIN,
        'EVENT_PART': EVENT_PART,
        'EVENT_QUIT': EVENT_QUIT,
        'EVENT_KICK': EVENT_KICK,
        'EVENT_PUBMSG': EVENT_PUBMSG,
        'EVENT_PRIVMSG': EVENT_PRIVMSG,
        'EVENT_PUBACTION': EVENT_PUBACTION,
        'EVENT_PRIVACTION': EVENT_PRIVACTION,
        'EVENT_PUBNOTICE': EVENT_PUBNOTICE,
        'EVENT_PRIVNOTICE': EVENT_PRIVNOTICE,
    }

    def __init__(self, irc):
        """
        Initialize a new Commander instance
        """
        # Initialize commander
        self.irc = irc
        self.log = logging.getLogger('nano.irc.commander')
        self.auth = Auth()

        # Command trigger pattern
        self.trigger_pattern = re.compile("^>>>( )?[a-zA-Z]+")

        # Option patterns
        self.short_opt_pattern = re.compile("^\-([a-zA-Z])$")
        self.long_opt_pattern  = re.compile('^\-\-([a-zA-Z]*)="?(.+)"?$')

    def _execute(self, command, plugin, args, opts, source, public, command_prefix='command_'):
        """
        Handle execution of the specified command

        Args:
            command(str): Name of the command to execute
            plugin(str): Name of the plugin
            args(list): The command arguments
            opts(dict): The command options
            source(str): Hostmask of the requesting client
            public(bool): This command was executed from a public channel
            command_prefix(str, optional): The prefix of the command method. Defaults to 'command_'

        Returns:
            list, tuple, str or None: Returns replies to send to the client, or None if nothing should be returned
        """
        # Get our commands class name for the requested plugin
        try:
            command = self.irc.plugins.get(plugin).get_irc_command(command, command_prefix)
            if callable(command):
                return command(Command(self.irc, args, opts, source, public))
        except PluginNotLoadedError:
            self.log.info('Attempted to execute a command from a plugin that is not loaded or does not exist')
            return

    def _help_execute(self, plugin, command=None):
        """
        Return the help entry for the specified plugin or plugin command

        Args:
            plugin(str): Name of the requested plugin
            command(str): Name of the requested command

        Returns:
            str, dict, list or None: The help entry, or None if no help entry exists
        """
        # Get our commands class name for the requested plugin
        commands_help = None

        if self.irc.plugins.is_loaded(plugin):
            # Load the commands class and check if a help dictionary exists in it
            commands_class = self.irc.plugins.get(plugin).commands_class
            if hasattr(commands_class, 'commands_help'):
                commands_help = commands_class.commands_help

        # Attempt to retrieve the requested help entry
        if commands_help:
            if not command and 'main' in commands_help:
                return commands_help['main']

            if command and command in commands_help:
                return commands_help[command]
        else:
            return "Either no help entries for <strong>{plugin}</strong> are available or the plugin does not exist"\
                .format(plugin=plugin)

        # Return a default message if we didn't get anything
        return "Either no help entry is available for <strong>{command}</strong> or the command does not exist"\
            .format(command=command)

    def _parse_command_string(self, command_string):
        """
        Parses a command string into arguments and options

        Args:
            command_args(list): The command arguments

        Returns:
            list: [0: args, 1: opts]
        """
        # Strip the trigger and split the command string
        command_string = command_string.lstrip(">>>").strip()
        command_args = shlex.split(command_string)

        # Set our defaults
        parsed_args = []
        opts = {}

        # Make sure we actually have a list
        if isinstance(command_args, list):
            # Loop through and parse our remaining arguments
            for arg in command_args:
                # Short option
                match = self.short_opt_pattern.match(arg)
                if match:
                    # Format option and remove it from our arguments list
                    opt = match.group(1).lower()

                    # Add the option to our opts dictionary
                    self.log.debug('Toggle option set: ' + arg)
                    opts[opt] = True
                    continue

                # Long option
                match = self.long_opt_pattern.match(arg)
                if match:
                    # Format option and remove it from our arguments list
                    opt = match.group(1).lower()
                    value = match.group(2).lower()

                    # Add the option to our opts dictionary
                    self.log.debug('Value option set: {opt} ({value})'.format(opt=opt, value=value))
                    opts[opt] = value
                    continue

                parsed_args.append(arg)

        # Return our parsed values
        return [parsed_args, opts]

    def _parse_command_arguments(self, args):
        """
        Parses command arguments and returns the requested plugin, command, remaining arguments and help request status

        Args:
            args(list): A list of arguments to parse

        Returns:
            tuple: (0: plugin, 1: command, 2: args, 3: help_command)

        Raises:
            PluginNotLoadedError: No active plugin could be found to handle this command request
        """
        # Set some default arguments
        plugin = None
        command = None
        help_command = False
        args_len = len(args)
        args_lower = [arg.lower() for arg in args]

        # Help command? (TODO: This is still a bit kludgy)
        if args_len and args_lower[0] == 'help':
            self.log.debug('Registering command string as a Help request')
            del args_lower[0]
            del args[0]
            args_len -= 1
            help_command = True

        # Do we have a valid plugin or subplugin for this request?
        if args_len and self.irc.plugins.is_loaded(args_lower[0]):
            self.log.debug('Plugin matched: ' + args_lower[0])
            plugin = args_lower[0]
            del args[0]
        if args_len >= 2:
            subplugin = '.'.join([args_lower[0], args_lower[1]])
            if self.irc.plugins.is_loaded(subplugin):
                self.log.debug('Subplugin matched: ' + subplugin)
                plugin = subplugin
                del args[0]

        if not plugin:
            self.log.debug('Requested plugin is not loaded or does not exist')
            raise PluginNotLoadedError('The requested plugin is not loaded or does not exist')

        if len(args):
            command = args.pop(0)
            self.log.debug('Command registered: ' + command)

        return plugin, command, args, help_command

    def execute(self, command_string, source, public):
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
        # Command prefixes
        admin_prefix = "admin_command_"
        user_prefix  = "user_command_"

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
        if self.auth.check(source.host, self.irc.network):
            user = self.auth.user(source.host, self.irc.network)

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
        for plugin_name, plugin in self.irc.plugins.all().items():
            if plugin.has_irc_events():
                event_method = plugin.get_irc_event(event_name)
                if callable(event_method):
                    event_replies = event_method(event, self.irc)
                    if event_replies:
                        replies.append(event_replies)

        self.log.debug('Returning event replies: ' + str(replies))
        return replies

    def filter_command_string(self, command_string):
        """
        Returns a filtered command string (for safe logging, stripping potentially sensitive data such as passwords)

        Args:
            command_string(str): The command string to filter

        Returns:
            tuple: (0: command_string, 1: filtered)
        """
        # Strip our command trigger
        command_string = command_string.lstrip('>>>').strip()

        # Parse our command string into names, arguments and options
        try:
            # Attempt to retrieve our actual plugin and command values
            args, opts = self._parse_command_string(command_string)
            plugin, command, args, help_command = self._parse_command_arguments(args)
            self.log.info('Filtering a valid command string')

            # If this was a help request, we don't need to filter anything
            if help_command:
                return '>>> ' + command_string, False

            # Set the filtered command string
            command_string = '>>> {plugin} {command}'.format(plugin=plugin, command=command)

            # If we don't have any arguments, don't consider the string filtered (options are intentionally ignored)
            filtered = bool(len(args))
            return command_string, filtered
        except PluginNotLoadedError:
            # Even though this was an invalid command request, we should still filter primarily in case of typos
            # Just shlex split the string and set the first two arguments as the plugin and command respectively
            self.log.info('Attempting to filter an invalid command string')
            args = shlex.split(command_string)

            # "Plugin"
            if len(args):
                plugin = args.pop(0)
            else:
                plugin = ''

            # "Command"
            if len(args):
                command = args.pop(0)
            else:
                command = ''

            command_string = '>>> {plugin} {command}'.format(plugin=plugin, command=command)

            # If we still have excess arguments, this command string should be considered filtered
            filtered = bool(len(args))

            return command_string, filtered


class Command:
    """
    An IRC command
    """
    def __init__(self, irc, args, opts, source, public):
        """
        Initialize a Command

        Args:
            args(list): Any command arguments
            opts(list): Any command arguments
            source(irc.client.NickMask): The client calling the command
            public(bool): Whether or not the command was called from a public channel
        """
        self.log = logging.getLogger('nano.command')
        self.log.info('Setting up a new Command instance')

        # Set the NanoIRC instance
        self.irc = irc

        # Set the command arguments and options
        self.args = args if args is not None else []
        self.opts = opts if opts is not None else []

        # Set the client source
        self.source = source
        self.public = public

        # TODO Set our current application version
        self.version = None

        # Event holders
        self._whois = []

    def deliver_response(self, response):
        """
        Deliver a response message (intended to be utilized primarily for events)

        Args:
            response(list, tuple or str): The response message(s) to deliver
        """
        self.irc.postmaster.deliver(response, self.source, self.irc.channel, self.public)

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
            self.irc.connection.remove_global_handler('whoisuser', whois_start)
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
            self.irc.connection.remove_global_handler('endofwhois', whois_end)
            self.log.debug('End of WHOIS response')

            # Fire our callback method and reset the event holder
            if not callable(callback):
                self.log.error('The callback supplied was not a valid callable method! Please review the documentation')

            callback(self, self._whois)
            self._whois = []

        # Bind and execute the events
        self.log.debug('Binding WHOIS events')
        self.irc.connection.add_global_handler('whoisuser', whois_start)
        self.irc.connection.add_global_handler('endofwhois', whois_end)

        self.log.debug('Executing WHOIS command')
        self.irc.connection.whois(targets)