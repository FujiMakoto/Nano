import logging
from .network import Network
from .nano_irc import NanoIRC
from plugins import Channel


class Interface:
    """
    IRC Interface
    """
    def __init__(self, nano):
        """
        Start a new IRC Interface instance

        Args:
            nano(Nano): The master Nano class
        """
        self.log = logging.getLogger('nano.irc.interface')
        self.nano = nano

        # Fetch our autojoin networks
        self.network_list = Network()
        self.networks = self.network_list.all()

        # Fetch our autojoin channels
        self.channel_list = Channel()

    def start(self):
        """
        Start the IRC Interface
        """
        for network in self.networks:
            self.log.info('Connecting to Network: ' + network.name)
            # Fetch our autojoin channels
            channels = self.channel_list.all(network)
            # TODO: Add proper multi-channel support
            for channel in channels:
                NanoIRC(network, channel, self.nano.plugins, self.nano.language).start()