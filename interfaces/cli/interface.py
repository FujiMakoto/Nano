import sys
import logging
from interfaces.cli.nano_cli import NanoCLI


class Interface:
    """
    CLI Interface
    """
    def __init__(self, nano):
        """
        Initialize a new CLI Interface instance

        Args:
            nano(Nano): The master Nano class
        """
        self.log = logging.getLogger('nano.cli.interface')
        self.nano = nano

    def start(self):
        """
        Start the CLI Interface
        """
        command = sys.argv[1] if len(sys.argv) > 1 else None
        NanoCLI(self.nano).start(command)