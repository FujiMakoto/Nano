import re
import shlex
import inspect
import logging
from abc import ABCMeta, abstractmethod
from src.plugins import PluginNotLoadedError
from src.validator import ValidationError
from plugins.exceptions import CommandError, NotEnoughArgumentsError
from src.auth import Auth

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Commander:
    """
    Command dispatcher abstract class
    """
    __metaclass__ = ABCMeta

    # TODO: Move these events to the IRC commander
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

    def __init__(self, connection):
        """
        Initialize a new Commander instance
        """
        # Initialize commander
        self.connection = connection
        self.log = logging.getLogger('nano.commander')
        self.auth = Auth()

        # Command trigger pattern
        self.trigger_pattern = re.compile('^>>>( )?[a-zA-Z]+')

        # Docstring syntax pattern
        self.docstring_syntax = re.compile('^Syntax: (.+)$')
        self.syntax_optional_arg = re.compile('\[<([^>]+)>\]')
        self.syntax_required_arg = re.compile('<([^>]+)>')

        # Option patterns
        self.short_opt_pattern = re.compile('^\-([a-zA-Z])$')
        self.long_opt_pattern  = re.compile('^\-\-([a-zA-Z]*)="?(.+)"?$')

        # Command instance
        self.command = Command

    def _execute(self, command_name, plugin, args, opts, source, public, command_prefix='command_'):
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
            command_method = self.connection.plugins.get(plugin).get_irc_command(command_name, command_prefix)
            if callable(command_method):
                syntax, min_args = self._parse_command_syntax(command_method)
                command = self.command(self.connection, args, opts, source=source, public=public, syntax=syntax)
                if len(args) < min_args:
                    self.log.info('Not enough arguments supplied to execute this command')
                    raise NotEnoughArgumentsError(command, min_args)
                return command_method(command)
        # Plugin not found
        except PluginNotLoadedError:
            self.log.info('Attempted to execute a command from a plugin that is not loaded or does not exist')
            return
        # Command exceptions
        except CommandError as e:
            self.log.info('Command raised an exception: ' + e.error_message)
            return e.destination, e.error_message
        # Validation exceptions
        except ValidationError as e:
            self.log.info('Validation exception raised: ' + e.error_message)
            return e.error_message
        # Uncaught exceptions (actual errors)
        except Exception as e:
            self.log.error('Uncaught exception raised when executing a plugin command (Args: {args}, Opts: {opts})'
                           .format(args=args, opts=opts), exc_info=e)
            return "An unknown error occurred while trying to process your request"

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

        if self.connection.plugins.is_loaded(plugin):
            # Load the commands class and check if a help dictionary exists in it
            commands_class = self.connection.plugins.get(plugin).commands_class
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

    def _parse_command_syntax(self, command):
        """
        Attempts to retrieve the command syntax from the commands docstring

        Args:
            command(method): The command method to inspect

        Returns:
            tuple (0: str or None, 1: int)
        """
        syntax = None
        args_required = 0

        if not callable(command):
            return syntax, args_required

        self.log.debug('Fetching command docstring')
        try:
            docstrings = inspect.getdoc(command).split('\n')
        except AttributeError:
            return syntax, args_required

        self.log.debug('Inspecting docstring for command syntax')
        for docstring in docstrings:
            syntax_match = self.docstring_syntax.match(docstring)
            if syntax_match:
                # Set our syntax
                syntax = syntax_match.group(1)
                self.log.debug('Syntax matched: ' + syntax)

                # Get the number of required arguments
                required_args = self.syntax_optional_arg.sub('', syntax)
                args_required = len(self.syntax_required_arg.findall(required_args))
                self.log.debug('{num} required arguments registered'.format(num=args_required))
                break

        return syntax, args_required

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
        if args_len and self.connection.plugins.is_loaded(args_lower[0]):
            self.log.debug('Plugin matched: ' + args_lower[0])
            plugin = args_lower[0]
            del args[0]
        if args_len >= 2:
            subplugin = '.'.join([args_lower[0], args_lower[1]])
            if self.connection.plugins.is_loaded(subplugin):
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

    @abstractmethod
    def execute(self, command_string, **kwargs):
        pass

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
    def __init__(self, connection, args, opts, **kwargs):
        """
        Initialize a Command

        Args:
            args(list): Any command arguments
            opts(list): Any command options
            source(irc.client.NickMask): The client calling the command
            public(bool): Whether or not the command was called from a public channel
        """
        self.log = logging.getLogger('nano.command')

        # Set the connection instance
        self.connection = connection

        # Set the command arguments and options
        self.args = args if args is not None else []
        self.opts = opts if opts is not None else []

        # Set the command syntax
        self.syntax = kwargs['syntax'] if 'syntax' in kwargs else None

        # TODO Set our current application version
        self.version = None