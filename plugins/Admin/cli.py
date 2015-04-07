from src.cmd import NanoCmd
from .Network.cli import Commands as NetworkCommands
from .Channel.cli import Commands as ChannelCommands


# noinspection PyMethodMayBeStatic
class Commands(NanoCmd):
    """
    Administration commands
    """
    prompt = '(admin) '

    def __init__(self, plugin):
        """
        Initialize a new Admin Commands instance

        Args:
            plugin(src.plugins.Plugin): The plugin instance
        """
        super().__init__()
        self.plugin = plugin

    def do_network(self, arg):
        """Create, delete and modify the IRC networks"""
        NetworkCommands().cmdloop()

    def do_channel(self, arg):
        """Create, delete and modify the IRC channels"""
        ChannelCommands().cmdloop()