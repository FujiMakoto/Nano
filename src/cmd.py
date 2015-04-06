import sys
import inspect
import cmd
import logging
from src.utilities import MessageParser
from interfaces.cli.commander import CLICommander
from interfaces.cli.postmaster import Postmaster


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

        # Set up our CLICommander, Postmaster and MessageParser instances
        self.commander = CLICommander(self)
        self.postmaster = Postmaster(self)
        self.message_parser = MessageParser()

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

    def get_names(self):
        """
        Custom method for pulling in base class attributes, including those programmatically created
        """
        return [name for name, method in inspect.getmembers(self) if name.startswith('do_')]

    def do_help(self, arg):
        'List available commands with "help" or detailed help with "help cmd".'
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc=inspect.getdoc(getattr(self, 'do_' + arg))
                    if doc:
                        self.stdout.write("%s\n"%str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n"%str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  list(help.keys()),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)

    def printf(self, message):
        """
        Format a message response before printing

        Args:
            message(str): The message to format
        """
        if message:
            formatted_message = self.message_parser.html_to_cli(message)
            print(formatted_message)