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
        self.commands = {}
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
        module_path = "{modules_dir}.{module_name}".format(modules_dir=self.modules_dir, module_name=name)
        class_name  = self._get_commands_class_name(name)

        # Import the parent module
        module = importlib.import_module(module_path)

        # Make sure we have a commands class, and import it into our commands list if so
        if hasattr(module, class_name):
            command_class = getattr(module, class_name)
            self.commands[class_name] = command_class()

    def _parse_command_arguments(self, command_args):
        """
        Parse any options passed with our arguments

        Args:
            command_args(list): The command arguments

        Returns:
            list: [0: module, 1: command, 2: args, 3: opts]
        """
        # Set our defaults
        module = None
        command = None
        parsed_args = []
        opts = {}

        # Make sure we actually have a list
        if isinstance(command_args, list):
            # Set our module and command
            module = command_args.pop(0)
            command = command_args.pop(0)

            # Loop through and parse our remaining arguments
            for arg in command_args:
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

        # Return our parsed values
        return [module, command, parsed_args, opts]

    def _get_commands_class_name(self, module_name):
        """
        Return the formatted commands class name for the specified module

        Args:
            module_name(str): The name of the module
        """
        return "{module_name}Commands".format(module_name=module_name.capitalize())

    def _execute(self, command, module, args, opts, irc, source, public):
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
        # Get our commands class name for the requested module
        commands_class_name = self._get_commands_class_name(module)
        if commands_class_name in self.commands:
            # Load the commands class and check if our requested command exists in it
            commands_class = self.commands[commands_class_name]
            if hasattr(commands_class, command):
                # Load the command and return the response
                command = getattr(commands_class, command)
                return command(args, opts, irc, source, public)

        return None

    def execute(self, command_args, irc, source, public):
        """
        Attempt to execute the specified command

        Args:
            command_args(str): The command to execute
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

        # Make sure we have at least two arguments (the module and the command)
        if len(command_args) < 2:
            return None

        # Parse arguments
        module, command, args, opts = self._parse_command_arguments(command_args)

        # Are we authenticated?
        if self.auth.check(source, irc.network):
            user = self.auth.user(source, irc.network)

            # If we're an administrator, attempt to execute an admin command
            if user.is_admin:
                response = self._execute(admin_prefix + command, module, args, opts, irc, source, public)
                if response:
                    return response

            # Attempt to execute an unprivileged user command
            response = self._execute(user_prefix + command, module, args, opts, irc, source, public)
            if response:
                return response

        # Attempt to execute a public command
        return self._execute(prefix + command, module, args, opts, irc, source, public)