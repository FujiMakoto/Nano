import logging
from src.commander import Commander


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
        pass

    def parse_line(self, line):
        """
        Parse a Cmd line into arguments and options

        Args:
            line(str): The Cmd arguments
        """
        return self._parse_command_string(line)


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