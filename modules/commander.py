import os
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

    def _execute(self, command, args, irc, network, channel, source):
        """
        Handle execution of the specified command

        Args:
            command(str): The command to execute
            args(list): The command arguments
            irc(NanoIRC): The active NanoIRC instance
            network(database.models.Network): The active IRC network
            channel(database.models.Channel): The active IRC channel
            source(str): Hostmask of the requesting client

        Returns:
            str or None: Returns a reply to send to the client, or None if nothing should be returned
        """
        for command_class in self.commands:
            if hasattr(command_class, command):
                command = getattr(command_class, command)
                return command(args, irc=irc, network=network, channel=channel, source=source)

        return None

    def execute(self, command, args, irc, network, channel, source):
        """
        Attempt to execute the specified command

        Args:
            command(str): The command to execute
            args(list): The command arguments
            irc(NanoIRC): The active NanoIRC instance
            network(database.models.Network): The active IRC network
            channel(database.models.Channel): The active IRC channel
            source(str): Hostmask of the requesting client

        Returns:
            str or None: Returns a reply to send to the client, or None if nothing should be returned
        """
        # Command prefixes
        prefix       = "command_"
        admin_prefix = "admin_command_"
        user_prefix  = "user_command_"

        # Are we authenticated?
        if self.auth.check(source, network):
            user = self.auth.user(source, network)

            # If we're an administrator, attempt to execute an admin command
            if user.is_admin:
                response = self._execute(admin_prefix + command, args, irc, network, channel, source)
                if response:
                    return response

            # Otherwise, attempt to execute an unprivileged user command
            response = self._execute(user_prefix + command, args, irc, network, channel, source)
            if response:
                return response

        # Attempt to execute a public command
        return self._execute(prefix + command, args, irc, network, channel, source)