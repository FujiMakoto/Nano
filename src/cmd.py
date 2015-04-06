import sys
import inspect
import cmd
import logging


class NanoCmd(cmd.Cmd):
    """
    Nano Cmd class
    """
    intro = 'Welcome to the Nano shell.  Type \'start\' to initialize. Type \'help\' or \'?\' to list commands.\n'
    prompt = '(nano) '
    file = None

    def __init__(self, *args):
        """
        Initialize a new Nano Cmd instance
        """
        super().__init__()
        # Debug logger
        self.log = logging.getLogger('nano.cmd')

        # A bit of a crafty method of detecting whether or not we're initializing from another Cmd instance
        if len(args):
            # Enable the "back" command if we're in a sub-process (TODO: This is probably more accurately "home")
            setattr(self, 'do_back', self._do_back)
            self.cmdloop()

    def _do_back(self, arg):
        """Go back to the previous section"""
        return True

    def do_bye(self, arg):
        """Quit the shell session"""
        sys.exit()

    def precmd(self, line):
        """
        Command pre-processing

        Args:
            line(str): The line to pre-process
        """
        return line.lower()

    def get_names(self):
        """
        Custom method for pulling in base class attributes, including those programmatically created
        """
        return [name for name, method in inspect.getmembers(self) if name.startswith('do_')]