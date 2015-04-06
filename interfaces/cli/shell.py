import logging
from src.cmd import NanoCmd


class NanoShell(NanoCmd):
    """
    Nano shell interpreter
    """
    def __init__(self, nano, cli):
        """
        Initialize a new Nano Shell instance

        Args:
            nano(Nano): The master Nano class instance
            cli(src.cli.nano_cli.NanoCLI): The Nano CLI instance
        """
        self.log = logging.getLogger('nano.cmd')
        # Set our Nano and CLI instances and ready a list of plugins for iteration
        self.nano = nano
        self.cli = cli
        self.plugins = self.nano.plugins.all().items() if self.nano else None

        # Load our available plugins
        self._load_plugins()
        super().__init__()

    def _load_plugins(self):
        """
        Load and programmatically create all available plugin CLI command methods
        """
        for name, plugin in self.plugins:
            # Do not attempt to create methods for sub-plugins
            if '.' not in name and plugin.has_commands('cli'):
                self.log.debug('Loading CLI commands for ' + name)
                # Load the CLI commands class and retrieve a list of all module methods
                commands = plugin.command_classes['cli']
                setattr(self, 'do_' + name, type(commands))

    def do_start(self, arg):
        """Establish connections on all enabled protocols"""
        self.nano.start()

    def do_chat(self, arg):
        """Initialize a chat session with Nano"""
        ChatShell(self.cli).start()


class ChatShell():
    """
    Nano conversation shell
    """
    def __init__(self, cli):
        """
        Initialize a new Chat Shell instance

        Args:
            cli(src.cli.nano_cli.NanoCLI): The Nano CLI instance
        """
        self.cli = cli

    def start(self):
        """
        Start the chat session
        """
        while True:
            message = input('You> ')
            if message == '/quit':
                break

            print('Nano> ', end='')
            self.cli.get_replies(message)
            print()