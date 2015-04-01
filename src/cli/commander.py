import re
import shlex
import logging
from src.plugins import PluginNotLoadedError

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class CLICommander:
    """
    CLI Command dispatcher
    """
    def __init__(self, cli):
        """
        Initialize a new CLI Commander instance

        Args:
            cli(src.cli.nano_cli.NanoCLI): The Nano CLI instance
        """
        # Initialize commander
        self.cli = cli
        self.log = logging.getLogger('nano.cli.commander')

        # Command trigger pattern
        self.trigger_pattern = re.compile("^>>>( )?[a-zA-Z]+")

        # Option patterns
        self.short_opt_pattern = re.compile("^\-([a-zA-Z])$")
        self.long_opt_pattern  = re.compile('^\-\-([a-zA-Z]*)="?(.+)"?$')

    def _execute(self, command, plugin, args, opts):
        """
        Handle execution of the specified command

        Args:
            command(str): Name of the command to execute
            plugin(str): Name of the plugin
            args(list): The command arguments
            opts(dict): The command options

        Returns:
            list, tuple, str or None: Returns replies to print, or None if nothing should be returned
        """
        # Get our commands class name for the requested plugin
        try:
            command = self.cli.plugins.get(plugin).get_cli_command(command)
            if callable(command):
                return command(CLICommand(self.cli, args, opts))
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

        if self.cli.plugins.is_loaded(plugin):
            # Load the commands class and check if a help dictionary exists in it
            commands_class = self.cli.plugins.get(plugin).commands_class
            if hasattr(commands_class, 'cli_commands_help'):
                commands_help = commands_class.cli_commands_help

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
        if args_len and self.cli.plugins.is_loaded(args_lower[0]):
            self.log.debug('Plugin matched: ' + args_lower[0])
            plugin = args_lower[0]
            del args[0]
        if args_len >= 2:
            subplugin = '.'.join([args_lower[0], args_lower[1]])
            if self.cli.plugins.is_loaded(subplugin):
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

    def execute(self, command_string):
        """
        Attempt to execute the specified command

        Args:
            command_args(str): The command to execute

        Returns:
            list, tuple, str or None: Returns replies to send to the client, or None if nothing should be returned
        """
        # Parse our command string into names, arguments and options
        try:
            args, opts = self._parse_command_string(command_string)
            plugin, command, args, help_command = self._parse_command_arguments(args)
        except PluginNotLoadedError:
            return None

        # Are we executing a help command?
        if help_command:
            return self._help_execute(plugin, command)

        # Attempt to execute a public command
        return self._execute(command, plugin, args, opts)


class CLICommand:
    """
    A CLI command
    """
    def __init__(self, cli, args, opts):
        """
        Initialize a CLI Command

        Args:
            cli(src.cli.nano_cli.NanoCLI): The Nano CLI instance
            args(list): Any command arguments
            opts(list): Any command options
        """
        self.log = logging.getLogger('nano.cli_command')
        self.log.info('Setting up a new CLI Command instance')

        # Set the NanoCLI instance
        self.cli = cli

        # Set the command arguments and options
        self.args = args if args is not None else []
        self.opts = opts if opts is not None else []

        # TODO Set our current application version
        self.version = None