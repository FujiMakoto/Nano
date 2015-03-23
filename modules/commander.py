import os
import re
import shlex
import logging
import importlib
from configparser import ConfigParser
from modules import Auth

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class Commander:

    EVENT_JOIN = "on_join"
    EVENT_PART = "on_part"
    EVENT_QUIT = "on_quit"
    EVENT_KICK = "on_kick"
    EVENT_PUBMSG = "on_public_message"
    EVENT_PRIVMSG = "on_private_message"
    EVENT_PUBACTION = "on_public_action"
    EVENT_PRIVACTION = "on_private_action"
    EVENT_PUBNOTICE = "on_public_notice"
    EVENT_PRIVNOTICE = "on_private_notice"

    _methodToName = {
        EVENT_JOIN: 'EVENT_JOIN',
        EVENT_PART: 'EVENT_PART',
        EVENT_QUIT: 'EVENT_QUIT',
        EVENT_KICK: 'EVENT_KICK',
        EVENT_PUBMSG: 'EVENT_PUBMSG',
        EVENT_PRIVMSG: 'EVENT_PRIVMSG',
        EVENT_PUBACTION: 'EVENT_PUBACTION',
        EVENT_PRIVACTION: 'EVENT_PRIVACTION',
        EVENT_PUBNOTICE: 'EVENT_PUBNOTICE',
        EVENT_PRIVNOTICE: 'EVENT_PRIVNOTICE',
    }
    _nameToMethod = {
        'EVENT_JOIN': EVENT_JOIN,
        'EVENT_PART': EVENT_PART,
        'EVENT_QUIT': EVENT_QUIT,
        'EVENT_KICK': EVENT_KICK,
        'EVENT_PUBMSG': EVENT_PUBMSG,
        'EVENT_PRIVMSG': EVENT_PRIVMSG,
        'EVENT_PUBACTION': EVENT_PUBACTION,
        'EVENT_PRIVACTION': EVENT_PRIVACTION,
        'EVENT_PUBNOTICE': EVENT_PUBNOTICE,
        'EVENT_PRIVNOTICE': EVENT_PRIVNOTICE,
    }

    """
    Import and instantiate module command classes
    """
    def __init__(self, irc):
        """
        Initialize a new Commander instance
        """
        # Initialize commander
        self.irc = irc
        self.log = logging.getLogger('nano.modules.commander')
        self.modules_dir = "modules"
        self.irc_file = "irc.py"
        self.config_file = "module.cfg"
        self.commands = {}
        self.events = {}
        self.auth = Auth()

        # Command trigger pattern
        self.trigger_pattern = re.compile("^>>>( )?[a-zA-Z]+")

        # Option patterns
        self.short_opt_pattern = re.compile("^\-([a-zA-Z])$")
        self.long_opt_pattern  = re.compile('^\-\-([a-zA-Z]*)="?(.+)"?$')

        # Loop through our modules directory
        for name in os.listdir(self.modules_dir):
            path = os.path.join(self.modules_dir, name)
            # Loop through our sub-directories that are not private (i.e. __pycache__)
            if os.path.isdir(path) and not name.startswith('_'):
                # Check and see if this module has a commands file
                if os.path.isfile(os.path.join(path, self.irc_file)):
                    # Check our module configuration file if it exists and make sure the module is enabled
                    module_enabled = True
                    config_path = os.path.join(path, self.config_file)
                    if os.path.isfile(config_path):
                        self.log.debug('Reading {module} configuration: {path}'.format(module=name, path=config_path))
                        config = ConfigParser()
                        config.read(os.path.join(path, self.config_file))
                        if config.has_option('Module', 'Enabled'):
                            module_enabled = config.getboolean('Module', 'Enabled')

                    # Load the module
                    if module_enabled:
                        self.log.info('[LOAD] ' + name)
                        self._load_module(name)
                    else:
                        self.log.info('[SKIP] {module} - Module disabled in configuration'.format(module=name))

    def _load_module(self, name):
        """
        Attempt to load the Commands and Events classes for the specified module

        Args:
            name(str): Name of the module to import
        """
        self.log.debug('Loading module: ' + name)
        # Import the IRC module
        module = self._import_module(name)

        # See if we have a Commands class, and import it into our commands list if so
        if hasattr(module, 'Commands'):
            self.log.debug('Loading {module} Commands'.format(module=name))
            command_class = getattr(module, 'Commands')
            self.commands[name.lower()] = command_class()

        # See if we have an Events class, and import it into our events list if so
        if hasattr(module, 'Events'):
            self.log.debug('Loading {module} Events'.format(module=name))
            event_class = getattr(module, 'Events')
            self.events[name.lower()] = event_class()

    def _import_module(self, name):
        """
        Return an imported module by its name

        Args:
            module_name(str): The name of the module
        """
        self.log.debug('Importing module: ' + name)
        module_path = "{modules_dir}.{module_name}".format(modules_dir=self.modules_dir, module_name=name)
        return importlib.import_module(module_path)

    def _execute(self, command, module, args, opts, source, public):
        """
        Handle execution of the specified command

        Args:
            command(str): Name of the command to execute
            module(str): Name of the module
            args(list): The command arguments
            opts(dict): The command options
            irc(NanoIRC): The active NanoIRC instance
            source(str): Hostmask of the requesting client
            public(bool): This command was executed from a public channel

        Returns:
            str or None: Returns a reply to send to the client, or None if nothing should be returned
        """
        # Get our commands class name for the requested module
        module = module.lower()
        if module in self.commands:
            # Load the commands class and check if our requested command exists in it
            commands_class = self.commands[module]
            if hasattr(commands_class, command):
                # Load the command and return the response
                command = getattr(commands_class, command)
                return command(args, opts, self.irc, source, public)

        return None

    def _help_execute(self, module, command=None):
        """
        Return the help entry for the specified module or command

        Args:
            module(str): Name of the requested module
            command(str): Name of the requested command

        Returns:
            str, dict, list or None: The help entry, or None if no help entry exists
        """
        # Get our commands class name for the requested module
        module = module.lower()
        commands_help = None

        if module in self.commands:
            # Load the commands class and check if a help dictionary exists in it
            commands_class = self.commands[module]
            if hasattr(commands_class, 'commands_help'):
                commands_help = commands_class.commands_help

        # Attempt to retrieve the requested help entry
        if commands_help:
            if not command and 'main' in commands_help:
                return commands_help['main']

            if command and command in commands_help:
                return commands_help[command]
        else:
            return "Either no help entries for <strong>{module}</strong> are available or the module does not exist"\
                .format(module=module)

        # Return a default message if we didn't get anything
        return "Either no help entry is available for <strong>{command}</strong> or the command does not exist"\
            .format(command=command)

    def execute(self, command_string, source, public):
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

        # Parse our command string into names, arguments and options
        module, command, args, opts = self.parse_command_string(command_string)

        # Make sure we have at least two arguments (the module and the command)
        if not module or not command:
            return None

        # Are we executing a help command? (TODO: This is a bit kludgy)
        if module == 'help':
            module = command
            command = args[0] if len(args) else None
            return self._help_execute(module, command)

        if command == 'help':
            command = args[0] if len(args) else None
            return self._help_execute(module, command)

        # Are we authenticated?
        if self.auth.check(source, self.irc.network):
            user = self.auth.user(source, self.irc.network)

            # If we're an administrator, attempt to execute an admin command
            if user.is_admin:
                response = self._execute(admin_prefix + command, module, args, opts, source, public)
                if response:
                    return response

            # Attempt to execute an unprivileged user command
            response = self._execute(user_prefix + command, module, args, opts, source, public)
            if response:
                return response

        # Attempt to execute a public command
        return self._execute(prefix + command, module, args, opts, source, public)

    def parse_command_string(self, command_string):
        """
        Parse any options passed with our arguments

        Args:
            command_args(list): The command arguments

        Returns:
            list: [0: module, 1: command, 2: args, 3: opts]
        """
        # Strip the trigger and split the command string
        command_string = command_string.lstrip(">>>").strip()
        command_args = shlex.split(command_string)

        # Set our defaults
        module = None
        command = None
        parsed_args = []
        opts = {}

        # Make sure we actually have a list
        if isinstance(command_args, list):
            # Loop through and parse our remaining arguments
            for arg in command_args:
                # Short option
                match = self.short_opt_pattern.match(arg)
                if match:
                    # Format option and remove it from our arguments list
                    arg = match.group(1).lower()

                    # Add the option to our opts dictionary
                    opts[arg] = True
                    continue

                # Long option
                match = self.long_opt_pattern.match(arg)
                if match:
                    # Format option and remove it from our arguments list
                    arg = match.group(1).lower()
                    argopt = match.group(2).lower()

                    # Add the option to our opts dictionary
                    opts[arg] = argopt
                    continue

                parsed_args.append(arg)

            # Set our module and command
            if len(parsed_args):
                module = parsed_args.pop(0)
            if len(parsed_args):
                command = parsed_args.pop(0)

        # Return our parsed values
        return [module, command, parsed_args, opts]

    def event(self, event_name, event):
        """
        Fire IRC events for loaded modules

        Args:
            event_name(str): The name of the event being fired
            event(irc.client.Event): The IRC event instance

        Returns:
            list
        """
        # Make sure we're not executing a command
        if self.trigger_pattern.match(event.arguments[0]):
            self.log.debug('Not firing events for command request')
            return

        self.log.debug('Firing ' + self._methodToName[event_name])
        replies = []

        # Loop through and execute our events
        for module, events_class in self.events.items():
            if hasattr(events_class, event_name):
                event_method = getattr(events_class, event_name)
                event_reply = event_method(event, self.irc)

                if event_reply:
                    self.log.info('Queuing {event} reply from {module}'
                                  .format(event=self._methodToName[event_name], module=module.upper()))
                    # TODO: Queue limit
                    replies.append(event_reply)

        self.log.debug('Returning event replies: ' + str(replies))
        return replies