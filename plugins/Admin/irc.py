import os
import logging


class Commands:
    """
    IRC Commands for the Admin plugin
    """
    commands_help = {
        'main': [
            'Administrative commands',
            'Available commands: <strong>channel, network, ignore, restart'
        ],
    }

    def __init__(self, plugin):
        """
        Initialize a new Admin Commands instance

        Args:
            plugin(src.plugins.Plugin): The plugin instance
        """
        self.log = logging.getLogger('nano.plugins.admin.irc.commands')
        self.plugin = plugin

    def admin_command_restart(self, command):
        """
        Restart Nano

        Args:
            command(src.Command): The IRC command instance
        """
        self.log.info('Restarting!')
        script = os.path.join(os.getcwd(), 'nano.py')
        os.execl(script, script, 'start')