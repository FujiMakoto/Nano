from src.cmd import NanoCmd
from .Network.cli import Commands as NetworkCommands


class Commands(NanoCmd):
    """
    Administration commands
    """
    prompt = '(admin) '

    def do_network(self, arg):
        """Create, delete and modify the IRC networks"""
        NetworkCommands().cmdloop()