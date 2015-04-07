import os
import importlib
import pkgutil
import logging
from configparser import ConfigParser


class PluginManager:
    """
    Universal plugin manager
    """
    def __init__(self, interfaces):
        """
        Initialize a new Plugin Manager instance

        Args:
            interfaces(dict): A dictionary of interfaces to load plugins for
        """
        self.log = logging.getLogger('nano.plugin_manager')
        self.interfaces = interfaces
        self.plugins = {}

        # Load our system plugins path
        self.sys_config = ConfigParser()
        self.sys_config.read('config/system.cfg')
        self.plugins_base_path = self.sys_config.get('Plugins', 'SystemPath')

    def load_all(self, including_disabled=False):
        """
        Load all available plugins

        Args:
            including_disabled(bool, optional): Loads disabled plugins when True. Defaults to False
        """
        # Load a list of available plugins
        self.log.info('Loading all {status} plugins'
                      .format(status='enabled' if not including_disabled else 'enabled and disabled'))
        plugin_list = [name for __, name, ispkg in pkgutil.iter_modules([self.plugins_base_path]) if ispkg]

        # Loop through our list and load our available plugins
        for plugin_name in plugin_list:
            # Set our plugin path and load the parent plugin
            plugin_path = os.path.join(self.plugins_base_path, plugin_name)
            self.load_plugin(plugin_name, plugin_path)

            # Load any subplugins
            subplugin_list = [name for __, name, ispkg in pkgutil.iter_modules([plugin_path]) if ispkg]
            for subplugin_name in subplugin_list:
                self.log.debug('Loading subplugin for: ' + plugin_name)
                subplugin_path = os.path.join(plugin_path, subplugin_name)
                self.load_plugin('.'.join([plugin_name, subplugin_name]), subplugin_path)

    def load_plugin(self, name, path):
        """
        Load a specified plugin

        Args:
            name(str): The name of the plugin to load
            path(str): The directory path of the plugin being loaded
        """
        # Load our plugin configuration
        plugin_enabled = True
        plugin_config = self.load_plugin_config(path)
        if isinstance(plugin_config, ConfigParser) and plugin_config.has_option('Plugin', 'Enabled'):
            plugin_enabled = plugin_config.getboolean('Plugin', 'Enabled')

        # Make sure the plugin is not disabled before trying to load it
        if not plugin_enabled:
            self.log.debug('Refusing to load a disabled plugin: ' + name)
            self.log.info('[SKIP] ' + name)
            return

        # Load the plugin and add it to our plugins dictionary
        self.log.info('[LOAD] ' + name)
        self.plugins[name.lower()] = Plugin(name, self.plugins_base_path, path, plugin_config, self.interfaces)

    def unload_plugin(self, name):
        """
        Unload a specified plugin

        Args:
            name(str): The name of the plugin to unload

        Returns:
            None or bool: Returns False if we attempt to unload a plugin that wasn't actually loaded
        """
        self.log.info('Unloading plugin: ' + name)
        if self.is_loaded(name):
            del self.plugins[name.lower()]
            return

        self.log.warn('Attempted to unload a plugin that was not actually loaded')
        return False

    @staticmethod
    def load_plugin_config(plugin_path):
        """
        Load and read a plugin configuration file (if one is available)

        Args:
            plugin_path(str): The filesystem path to the plugin

        Returns:
            configparser.ConfigParser or None
        """
        # Make sure a default configuration file for this plugin exists
        default_config_path = os.path.join(plugin_path, 'plugin.def.cfg')
        if not os.path.isfile(default_config_path):
            return

        config = ConfigParser()
        config.read_file(open(default_config_path))

        # Apply any custom configuration directives
        custom_config_path = os.path.join(plugin_path, 'plugin.cfg')
        if os.path.isfile(custom_config_path):
            config.read(custom_config_path)

        return config

    def is_loaded(self, name):
        """
        Returns True if the specified plugin is loaded, otherwise False

        Args:
            name(str): The name of the plugin to check

        Returns:
            bool
        """
        self.log.debug('Checking whether the plugin "{name}" is loaded or not'.format(name=name))
        return name.lower() in self.plugins

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
        self.log.info('Requesting the "{name}" plugin'.format(name=name))
        if name.lower() in self.plugins:
            return self.plugins[name.lower()]

        raise PluginNotLoadedError('The requested plugin, "{name}", has not been loaded'.format(name=name))

    def all(self):
        """
        Returns the plugins dictionary

        Returns:
            dict
        """
        self.log.info('Returning all loaded plugins')
        return self.plugins


class Plugin:
    """
    Plugin handler
    """
    def __init__(self, name, base_path, path, config, interfaces):
        """
        Initialize a new Plugin instance

        Args:
            name(str): The module name of the plugin to load
            base_path(str): The base directory for all system plugins
            path(str): The directory path of the plugin being loaded
            config(configparser.ConfigParser or None): The Plugin configuration
            interfaces(dict): A dictionary of active interfaces
        """
        # Set up the universal plugin logger
        self.log = logging.getLogger('nano.plugin')

        # Set our paths
        self.base_path = base_path
        self.path = path

        # Set the plugin name, configuration and class dictionaries
        self.name = name
        self.config = config
        self.command_classes = {}
        self.event_classes = {}

        # Import the plugin
        self.log.debug('Importing plugin: ' + name)
        self.interfaces = interfaces if isinstance(interfaces, dict) else {}
        self.module_imports = {}
        self._load_imports()

        # Finally, load and initialize the available Command and Event classes
        self._load_plugin()

    def _load_imports(self):
        """
        Load plugin imports on all available interfaces
        """
        for name, interface in self.interfaces.items():
            import_path = "{dir}.{name}.{interface}".format(dir=self.base_path, name=self.name, interface=name)
            try:
                self.module_imports[name] = importlib.import_module(import_path)
            except ImportError:
                continue

    def _load_plugin(self):
        """
        Attempt to load the Commands and Events classes for the specified plugin
        """
        self.log.debug('Loading plugin: ' + self.name)

        for name, module_import in self.module_imports.items():
            # See if we have a Commands class, and import it into our commands dictionary if so
            if hasattr(module_import, 'Commands'):
                self.log.debug('Loading {plugin_name} {interface_name} Commands'
                               .format(plugin_name=self.name, interface_name=name))
                command_class = getattr(module_import, 'Commands')
                self.command_classes[name] = command_class(self)

            # See if we have an Events class, and import it into our events dictionary if so
            if hasattr(module_import, 'Events'):
                self.log.debug('Loading {plugin_name} {interface_name} Events'
                               .format(plugin_name=self.name, interface_name=name))
                event_class = getattr(module_import, 'Events')
                self.event_classes[name] = event_class(self)

    def get_command(self, command_name, interface_name, command_prefix='command_'):
        """
        Retrieve a callable command method if it exists

        Args:
            command_name(str): The name of the command to retrieve
            interface_name(str): The name of the active interface
            command_prefix(str, optional): The prefix of the command method. Defaults to 'command_'

        Returns:
            bound method or None
        """
        self.log.debug('Requesting {prefix}{command_name} command method for {plugin_name}'
                       .format(prefix=command_prefix, command_name=command_name, plugin_name=self.name))

        # Make sure the requested interface has commands
        if interface_name not in self.command_classes:
            self.log.debug('Plugin {plugin_name} has no loaded commands for the {interface_name} interface'
                           .format(plugin_name=self.name, interface_name=interface_name))
            return

        # Return our command method if it exists
        if command_name and hasattr(self.command_classes[interface_name], command_prefix + command_name):
            self.log.debug('Returning {prefix}{command_name} command method for {plugin_name}'
                           .format(prefix=command_prefix, command_name=command_name, plugin_name=self.name))
            return getattr(self.command_classes[interface_name], command_prefix + command_name)

        # Otherwise return None
        self.log.debug('{prefix}{command_name} is not a registered command for {plugin_name}'
                       .format(prefix=command_prefix, command_name=command_name, plugin_name=self.name))
        return

    def get_event(self, event_name, interface_name):
        """
        Retrieve a callable IRC event method if it exists

        Args:
            event_name(str): The name of the event to retrieve
            interface_name(str): The name of the active interface

        Returns:
            bound method or None
        """
        self.log.debug('Requesting {event_name} event method for {plugin_name}'
                       .format(event_name=event_name, plugin_name=self.name))

        # Make sure the requested interface has events
        if interface_name not in self.event_classes:
            self.log.debug('Plugin {plugin_name} has no loaded events for the {interface_name} interface'
                           .format(plugin_name=self.name, interface_name=interface_name))
            return

        # Return our event method if it exists
        if hasattr(self.event_classes[interface_name], event_name):
            self.log.debug('Returning {event_name} event method for {plugin_name}'
                           .format(event_name=event_name, plugin_name=self.name))
            return getattr(self.event_classes[interface_name], event_name)

        # Otherwise return None
        self.log.debug('{event_name} is not a registered event for {plugin_name}'
                       .format(event_name=event_name, plugin_name=self.name))
        return

    def has_commands(self, interface_name):
        """
        Returns True if the module has an instantiated IRC Commands class

        Args:
            interface_name(str): The name of the active interface

        Returns:
            bool
        """
        self.log.debug('Checking if {plugin_name} has Commands'.format(plugin_name=self.name))
        return interface_name in self.command_classes

    def has_events(self, interface_name):
        """
        Returns True if the module has an instantiated IRC Events class

        Args:
            interface_name(str): The name of the active interface

        Returns:
            bool
        """
        self.log.debug('Checking if {plugin_name} has Events'.format(plugin_name=self.name))
        return interface_name in self.event_classes

    def __str__(self):
        """
        Returns the plugin's name when the plugin instance is called as a string
        """
        self.log.debug('Plugin "{name}" requested as a string, returning the name of the plugin'.format(name=self.name))
        return self.name


class PluginNotLoadedError(Exception):
    pass