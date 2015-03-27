import os
import importlib
import pkgutil
import logging
from configparser import ConfigParser

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


class PluginManager:
    """
    Universal plugin manager
    """
    def __init__(self):
        """
        Initialize a new Plugin Manager instance
        """
        self.plugins = {}

        # Load our system plugins path
        self.sys_config = ConfigParser()
        self.sys_config.read('config/system.cfg')
        self.plugins_base_path = self.sys_config.get('Paths', 'Plugins')

    def load_all(self, including_disabled=False):
        """
        Load all available plugins

        Args:
            including_disabled(bool, optional): Loads disabled plugins when True. Defaults to False
        """
        # Load a list of available plugins
        plugin_list = [name for __, name, ispkg in pkgutil.iter_modules([self.plugins_base_path]) if ispkg]

        # Loop through our list and load our available plugins
        for plugin_name in plugin_list:
            # Set our plugin path and load the parent plugin
            plugin_path = os.path.join(self.plugins_base_path, plugin_name)
            self.load_plugin(plugin_name, plugin_path)

            # Load any subplugins
            subplugin_list = [name for __, name, ispkg in pkgutil.iter_modules([plugin_path]) if ispkg]
            for subplugin_name in subplugin_list:
                subplugin_path = os.path.join(plugin_path, subplugin_name)
                self.load_plugin('.'.join([plugin_name, subplugin_name]), subplugin_path)

    def load_plugin(self, name, path):
        """
        Load a specified plugin

        Args:
            name(str): The name of the plugin to load
            path(str): The directory path of the plugin being loaded
        """
        self.plugins[name] = Plugin(name, self.plugins_base_path, path)

    def unload_plugin(self, name):
        """
        Unload a specified plugin

        Args:
            name(str): The name of the plugin to unload

        Returns:
            None or bool: Returns False if we attempt to unload a plugin that wasn't actually loaded
        """
        if name in self.plugins:
            del self.plugins[name]
            return

        return False

    def get(self, name):
        """
        Return an instance of the specified plugin

        Args:
            name(str): The name of the plugin to retrieve

        Returns:
            method

        Raises:
            PluginNotLoadedError: Raised when attempting to get a plugin that does not exist or hasn't been loaded
        """
        if name in self.plugins:
            return self.plugins[name]

        raise PluginNotLoadedError('The requested plugin, "{name}", has not been loaded'.format(name=name))

    def all(self):
        """
        Returns the plugins dictionary

        Returns:
            dict
        """
        return self.plugins


class Plugin:
    """
    Plugin handler
    """
    def __init__(self, name, plugins_base_path, plugin_path):
        """
        Initialize a new Plugin instance

        Args:
            name(str): The module name of the plugin to load
            plugins_base_path(str): The base directory for all system plugins
            plugin_path(str): The directory path of the plugin being loaded
        """
        # Set up the universal plugin logger
        self.log = logging.getLogger('nano.plugin')

        # Set our paths
        self.plugins_base_path = plugins_base_path
        self.plugin_path = plugin_path

        # Set the plugin name and class placeholders
        self.name = name
        self.commands_class = None
        self.events_class = None

        # Import the plugin
        self.log.debug('Importing plugin: ' + name)
        self.import_path = "{plugins_dir}.{plugin_name}".format(plugins_dir=self.plugins_base_path, plugin_name=name)
        self.module_import = importlib.import_module(self.import_path)

        # Finally, load and initialize everything
        self._load_plugin()

    def _load_plugin(self):
        """
        Attempt to load the Commands and Events classes for the specified plugin

        Args:
            name(str): Name of the module to import
        """
        self.log.debug('Loading module: ' + self.name)
        # See if we have a Commands class, and import it into our commands list if so
        if hasattr(self.module_import, 'Commands'):
            self.log.debug('Loading {module} Commands'.format(module=self.name))
            command_class = getattr(self.module_import, 'Commands')
            self.commands_class = command_class()

        # See if we have an Events class, and import it into our events list if so
        if hasattr(self.module_import, 'Events'):
            self.log.debug('Loading {module} Events'.format(module=self.name))
            event_class = getattr(self.module_import, 'Events')
            self.events_class = event_class()

    def get_irc_event(self, event_name):
        """
        Retrieve a callable IRC event method if it exists

        Args:
            event_name(str): The name of the event to retrieve

        Returns:
            method or None
        """
        self.log.debug('Requesting {event_name} event method for {module_name}'
                       .format(event_name=event_name, module_name=self.name))

        # Return our event method if it exists
        if hasattr(self.events_class, event_name):
            self.log.debug('Returning {event_name} event method for {module_name}'
                           .format(event_name=event_name, module_name=self.name))
            return getattr(self.events_class, event_name)

        # Otherwise return None
        self.log.debug('{event_name} is not a registered event for {module_name}'
                       .format(event_name=event_name, module_name=self.name))
        return

    def get_irc_command(self, command_name, command_prefix='command_'):
        """
        Retrieve a callable IRC command method if it exists

        Args:
            command_name(str): The name of the command to retrieve

        Returns:
            method or None
        """
        self.log.debug('Requesting {prefix}{command_name} command method for {module_name}'
                       .format(prefix=command_prefix, command_name=command_name, module_name=self.name))

        # Return our command method if it exists
        if hasattr(self.commands_class, command_prefix + command_name):
            self.log.debug('Returning {prefix}{command_name} command method for {module_name}'
                           .format(prefix=command_prefix, command_name=command_name, module_name=self.name))
            return getattr(self.commands_class, command_prefix + command_name)

        # Otherwise return None
        self.log.debug('{prefix}{command_name} if not a registered command for {module_name}'
                       .format(prefix=command_prefix, command_name=command_name, module_name=self.name))
        return

    def has_irc_commands(self):
        """
        Returns True if the module has an instantiated IRC Commands class

        Returns:
            bool
        """
        self.log.debug('Checking if {module_name} has Commands'.format(module_name=self.name))
        return self.commands_class is not None

    def has_irc_events(self):
        """
        Returns True if the module has an instantiated IRC Events class

        Returns:
            bool
        """
        self.log.debug('Checking if {module_name} has Events'.format(module_name=self.name))
        return self.events_class is not None

    def __str__(self):
        """
        Returns the plugin's name when the plugin instance is called as a string
        """
        return self.name


class PluginNotLoadedError(Exception):
    pass