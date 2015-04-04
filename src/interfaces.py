import os
import pkgutil
import importlib
import logging
from configparser import ConfigParser


class InterfaceManager:
    """
    Universal interface manager
    """
    def __init__(self):
        """
        Initialize a new Interface Manager instance
        """
        self.log = logging.getLogger('nano.interface_manager')
        self.interfaces = {}

        # Load our system interfaces path
        self.sys_config = ConfigParser()
        self.sys_config.read('config/system.cfg')
        self.interfaces_base_path = self.sys_config.get('Interfaces', 'SystemPath')

    def load_all(self, including_disabled=False):
        """
        Load all available interfaces

        Args:
            including_disabled(bool, optional): Loads disabled interfaces when True. Defaults to False
        """
        self.log.info('Loading all {status} interfaces'
                      .format(status='enabled' if not including_disabled else 'enabled and disabled'))
        interface_list = [name for __, name, ispkg in pkgutil.iter_modules([self.interfaces_base_path]) if ispkg]

        # Loop through our list and load our available interfaces
        for interface_name in interface_list:
            # Set the interface path and load
            interface_path = os.path.join(self.interfaces_base_path, interface_name)
            self.load_interface(interface_name, interface_path)

    def load_interface(self, name, path):
        """
        Load a specified interface

        Args:
            name(str): The name of the interface to load
            path(str): The directory path of the interface being loaded
        """
        # Load our interface configuration
        interface_enabled = True
        interface_config = self.load_interface_config(path)
        if isinstance(interface_config, ConfigParser) and interface_config.has_option('Interface', 'Enabled'):
            interface_enabled = interface_config.getboolean('Interface', 'Enabled')

        # Make sure the interface is not disabled before trying to load it
        if not interface_enabled:
            self.log.debug('Refusing to load a disabled interface: ' + name)
            self.log.info('[SKIP] ' + name)
            return

        # Load the interface and add it to our interfaces dictionary
        self.log.info('[LOAD] ' + name)
        self.interfaces[name.lower()] = Interface(name, self.interfaces_base_path, path, interface_config)

    def unload_plugin(self, name):
        """
        Unload a specified interface

        Args:
            name(str): The name of the interface to unload

        Returns:
            None or bool: Returns False if we attempted to unload an interface that wasn't actually loaded
        """
        self.log.info('Unloading interface: ' + name)
        if self.is_loaded(name):
            del self.interfaces[name.lower()]
            return

        self.log.warn('Attempted to unload an interface that was not actually loaded')
        return False

    @staticmethod
    def load_interface_config(interface_path):
        """
        Load and read a interface configuration file (if one is available)

        Args:
            interface_path(str): The filesytsem path to the interface

        Returns:
            configparser.ConfigParser or None
        """
        # Make sure a configuration file for this interface exists
        config_path = os.path.join(interface_path, 'interface.cfg')
        if not os.path.isfile(config_path):
            return

        # Load and return a ConfigParser instance
        config = ConfigParser()
        config.read(config_path)
        return config

    def is_loaded(self, name):
        """
        Returns True if the specified interface is loaded, otherwise False

        Args:
            name(str): The name of the interface to check

        Returns:
            bool
        """
        self.log.debug('Checking whether the interface "{name}" is loaded or not'.format(name=name))
        return name.lower() in self.interfaces

    def get(self, name):
        """
        Return an instance of the specified interface

        Args:
            name(str): The name of the interface to retrieve

        Returns:
            method

        Raises:
            InterfaceNotLoadedError: Raised when attempting to get an interface that does not exist or is not loaded
        """
        self.log.info('Requesting the "{name}" interface'.format(name=name))
        if name.lower() in self.interfaces:
            return self.interfaces[name.lower()]

        raise InterfaceNotLoadedError('The requested interface, "{name}", has not been loaded'.format(name=name))

    def all(self):
        """
        Returns the interfaces dictionary

        Returns:
            dict
        """
        self.log.info('Returning all loaded interfaces')
        return self.interfaces


class Interface:
    """
    Interface handler
    """
    def __init__(self, name, base_path, path, config):
        """
        Initialize a new Interface instance

        Args:
            name(str): The package name of the interface to load
            base_path(str): The base directory for all system interfaces
            path(str): The directory path to the interface being loaded
            config(configparser.ConfigParser or None): The interface configuration
        """
        # Set up the universal interface logger
        self.log = logging.getLogger('nano.interface')

        # Set our paths
        self.interface_base_path = base_path
        self.interface_path = path

        # Set the interface class placeholder
        self.log.debug('Importing interface: ' + name)
        self.import_path = "{interface_dir}.{name}".format(interface_dir=self.interface_base_path, name=name)
        self.module_import = importlib.import_module(self.import_path)
        self.interface_class = None

        # Set the interface name and configuration
        self.name = name
        self.config = config

        # Finally, load and initialize everything
        self._load_interface()

    def _load_interface(self):
        self.log.debug('Loading interface: ' + self.name)
        # Make sure we have an Interface class before trying to import
        if hasattr(self.module_import, 'Interface'):
            self.log.debug('Loading {name} Interface'.format(name=self.name))
            self.interface_class = getattr(self.module_import, 'Interface')

    def start(self, nano):
        if callable(self.interface_class):
            interface = self.interface_class
            interface(nano).start()


class InterfaceNotLoadedError(Exception):
    pass