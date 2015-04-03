import logging
from src.plugins import PluginNotLoadedError
from src.commander import Commander

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class CLICommander(Commander):
    """
    CLI Command dispatcher
    """
    def __init__(self, cli):
        """
        Initialize a new CLI Commander instance

        Args:
            cli(src.cli.nano_cli.NanoCLI): The Nano CLI instance
        """
        super().__init__(cli)
        # Initialize commander
        self.log = logging.getLogger('nano.cli.commander')

    def execute(self, command_string, **kwargs):
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