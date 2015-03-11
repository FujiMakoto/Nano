import os
import re
import importlib
from modules import Auth


class Commander:
    """
    Import and instantiate module command classes
    """
    def __init__(self):
        """
        Initialize a new Commander instance
        """
        # Initialize commander
        self.modules_dir = "modules"
        self.commands_file = "commands.py"
        self.commands = []
        self.auth = Auth()

        # Option patterns
        self.short_opt_pattern = re.compile("^\-([a-zA-Z])$")
        self.long_opt_pattern  = re.compile('^\-\-([a-zA-Z]*)="?(.+)"?$')

        # Loop through our modules directory
        for name in os.listdir(self.modules_dir):
            path = os.path.join(self.modules_dir, name)
            # Loop through our sub-directories that are not private (i.e. __pycache__)
            if os.path.isdir(path) and not name.startswith('_'):
                # Check and see if this module has a commands file
                if os.path.isfile(os.path.join(path, self.commands_file)):
                    self._load_module_commands(name)

    def _load_module_commands(self, name):
        """
        Attempt to load the commands class for the specified module

        Args:
            name(str): Name of the module to import
        """
        # Format the module path and command class name
        module_path = "%s.%s" % (self.modules_dir, name)
        class_name  = "%s%s" % (name.capitalize(), "Commands")

        # Import the parent module
        module = importlib.import_module(module_path)

        # Make sure we have a commands class, and import it into our commands list if so
        if hasattr(module, class_name):
            command_class = getattr(module, class_name)
            self.commands.append(command_class())

    def _parse_arguments(self, args):
        """
        Parse any options passed with our arguments

        Args:
            args(list): The command arguments

        Returns:
            list: [0: args, 1: opts]
        """
        parsed_args = []
        opts = {}

        # Make sure we actually have a list
        if isinstance(args, list):
            for arg in args:
                # Short option
                match = self.short_opt_pattern.match(arg)
                if match:
                    # Format option and remove it from our arguments list
                    arg = match.group(1)

                    # Add the option to our opts dictionary
                    opts[arg] = True
                    continue

                # Long option
                match = self.long_opt_pattern.match(arg)
                if match:
                    # Format option and remove it from our arguments list
                    arg = match.group(1)
                    argopt = match.group(2)

                    # Add the option to our opts dictionary
                    opts[arg] = argopt
                    continue

                parsed_args.append(arg)

        # Return our parsed arguments and options
        return [parsed_args, opts]

    def _execute(self, command, args, opts, irc, source, public):
        """
        Handle execution of the specified command

        Args:
            command(str): The command to execute
            args(list): The command arguments
            irc(NanoIRC): The active NanoIRC instance
            source(str): Hostmask of the requesting client
            public(bool): This command was executed from a public channel

        Returns:
            str or None: Returns a reply to send to the client, or None if nothing should be returned
        """
        for command_class in self.commands:
            if hasattr(command_class, command):
                command = getattr(command_class, command)
                return command(args, opts, irc, source, public)

        return None

    def execute(self, command, args, irc, source, public):
        """
        Attempt to execute the specified command

        Args:
            command(str): The command to execute
            args(list): The command arguments
            irc(NanoIRC): The active NanoIRC instance
            source(str): Hostmask of the requesting client
            public(bool): This command was executed from a public channel

        Returns:
            str or None: Returns a reply to send to the client, or None if nothing should be returned
        """
        # Command prefixes
        prefix       = "command_"
        admin_prefix = "admin_command_"
        user_prefix  = "user_command_"

        # Parse arguments
        args, opts = self._parse_arguments(args)

        # Are we authenticated?
        if self.auth.check(source, irc.network):
            user = self.auth.user(source, irc.network)

            # If we're an administrator, attempt to execute an admin command
            if user.is_admin:
                response = self._execute(admin_prefix + command, args, opts, irc, source, public)
                if response:
                    return response

            # Otherwise, attempt to execute an unprivileged user command
            response = self._execute(user_prefix + command, args, opts, irc, source, public)
            if response:
                return response

        # Attempt to execute a public command
        return self._execute(prefix + command, args, opts, irc, source, public)