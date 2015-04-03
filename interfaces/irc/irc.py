import logging
import irc.client

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


# noinspection PyMethodMayBeStatic
class IRC:
    """
    Establishes a new connection to an IRC server
    """
    def __init__(self, network, channel):
        """
        Initialize a new IRC instance

        Args:
            network(database.models.Network): The IRC Network to connect to
            channel(database.models.channel): The channel to join
        """
        self.log = logging.getLogger('nano.irc')

        # Set up the client Reactor
        self.log.debug('Setting up the IRC Reactor')
        self.reactor = irc.client.Reactor()

        try:
            self.connection = self.reactor.server().connect(network.host, network.port, network.nick)
        except irc.client.ServerConnectionError as e:
            print(e)
            exit()

        # Assign handlers
        self.log.debug('Assigning connection event handlers')
        self.connection.add_global_handler('nicknameinuse', self.on_nick_in_use)
        self.connection.add_global_handler('erroneusnickname', self.on_erroneous_nick)
        self.connection.add_global_handler('serviceinfo', self.on_service_info)
        self.connection.add_global_handler('featurelist', self.on_welcome)
        self.connection.add_global_handler('cannotsendtochan', self.on_cannot_send_to_channel)
        self.connection.add_global_handler('toomanychannels', self.on_too_many_channels)
        self.connection.add_global_handler('unavailresource', self.on_unavailable_resource)
        self.connection.add_global_handler('channelisfull', self.on_channel_is_full)
        self.connection.add_global_handler('keyset', self.on_key_set)
        self.connection.add_global_handler('badchannelkey', self.on_bad_channel_key)
        self.connection.add_global_handler('inviteonlychan', self.on_invite_only_channel)
        self.connection.add_global_handler('bannedfromchan', self.on_banned_from_channel)
        self.connection.add_global_handler('banlistfull', self.on_ban_list_full)
        self.connection.add_global_handler('chanoprivsneeded', self.on_chanop_privs_needed)
        self.connection.add_global_handler('pubmsg', self.on_public_message)
        self.connection.add_global_handler('pubnotice', self.on_public_notice)
        self.connection.add_global_handler('privmsg', self.on_private_message)
        self.connection.add_global_handler('privnotice', self.on_private_notice)
        self.connection.add_global_handler('action', self.on_action)
        self.connection.add_global_handler('join', self.on_join)
        self.connection.add_global_handler('part', self.on_part)
        self.connection.add_global_handler('quit', self.on_quit)
        self.connection.add_global_handler('kick', self.on_kick)

    def start(self):
        """
        Initialize and start processing the IRC connection
        """
        self.log.info('Initializing a new IRC connection')
        self.reactor.process_forever()

    def on_nick_in_use(self, connection, event):
        """
        433: nicknameinuse

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_erroneous_nick(self, connection, event):
        """
        432: erroneusnickname

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_service_info(self, connection, event):
        """
        231: serviceinfo

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_welcome(self, connection, event):
        """
        001: welcome

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_feature_list(self, connection, event):
        """
        005: featurelist

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_cannot_send_to_channel(self, connection, event):
        """
        404: cannotsendtochan

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_too_many_channels(self, connection, event):
        """
        405: toomanychannels

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_unavailable_resource(self, connection, event):
        """
        437: unavailresource

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_channel_is_full(self, connection, event):
        """
        471: channelisfull

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_key_set(self, connection, event):
        """
        467: keyset

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_bad_channel_key(self, connection, event):
        """
        475: badchannelkey

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_invite_only_channel(self, connection, event):
        """
        473: inviteonlychan

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_banned_from_channel(self, connection, event):
        """
        474: bannedfromchan

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_ban_list_full(self, connection, event):
        """
        478: banlistfull

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_chanop_privs_needed(self, connection, event):
        """
        482: chanoprivsneeded

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_public_message(self, connection, event):
        """
        pubmsg

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_public_notice(self, connection, event):
        """
        pubnotice

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_private_message(self, connection, event):
        """
        privmsg

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_private_notice(self, connection, event):
        """
        privnotice

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_action(self, connection, event):
        """
        action

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_join(self, connection, event):
        """
        join

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_part(self, connection, event):
        """
        part

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_quit(self, connection, event):
        """
        quit

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass

    def on_kick(self, connection, event):
        """
        kick

        Args:
            connection(irc.client.connection): The active IRC connection
            event(irc.client,Event): The event response data
        """
        pass