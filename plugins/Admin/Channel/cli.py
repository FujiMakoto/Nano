import shlex

from interfaces.cli.cmd import NanoCmd
from interfaces.irc.channel import Channel, ChannelNotFoundException
from interfaces.irc.network import Network, NetworkNotFoundError
from plugins.Admin.Network.cli import Commands as NetworkCommands



# noinspection PyUnboundLocalVariable
class Commands(NanoCmd):
    """
    Channel administration commands
    """
    prompt = '(channel) '

    def __init__(self, plugin):
        """
        Initialize a new Admin Channel Commands instance

        Args:
            plugin(src.plugins.Plugin): The plugin instance
        """
        super().__init__()
        self.plugin = plugin
        self.channel_list = Channel()
        self.network_list = Network()
        self.validator = self.channel_list.validate.single
        self.network = None
        self.network_commands = NetworkCommands(None)

    def _get_network(self, allow_none=False):
        """
        Prompt the client to select a network, optionally allowing no selection

        Args:
            allow_none(bool, optional): Allow no selection to be made (by selecting "all networks"). Defaults to False

        Returns:
            database.models.Network or None
        """
        # Get the network to lookup on
        while True:
            # Prompt for the network ID
            try:
                db_id = abs(int(input('[ID] ')))
            except ValueError:
                if allow_none:
                    print('Please specify a valid network ID, or 0 to list all channels on all networks')
                else:
                    print('Please specify a valid network ID')
                continue

            # Retrieve the network
            network = None
            if db_id is not 0:
                try:
                    network = self.network_list.get(db_id)
                except NetworkNotFoundError:
                    print('No network with the specified ID exists, please select a valid network from the above list')
                    continue
            elif not allow_none:
                print('Please specify a valid network ID, or 0 to list all channels on all networks')
                continue
            break

        return network

    def do_list(self, line):
        """
        Lists all saved channels
        Syntax: list
        """
        # Prompt for the Network to list channels on
        self.network_commands.do_list(line)
        print('-' * 12)
        self.printf('<strong>0:</strong> All Networks\n')
        print('Which network do you want to list channels on?')

        # Get the network to lookup on
        network = self._get_network(True)

        # Retrieve a list of channels
        channels = self.channel_list.all(network, False)

        if not channels:
            if network is None:
                return print('No channels have been created yet')
            else:
                return print('No channels for the specified network have been created yet')

        # Loop through the channels and print them our
        for channel in channels:
            # Color the channel name by its autojoin status
            autojoin = bool(channel.autojoin)
            color = 'green' if autojoin else 'red'

            # Set and print the formatted response string
            message = '<strong>{id}:</strong> <p class="fg-{color}">{name}</p>'
            message = message.format(id=channel.id, color=color, name=channel.name)
            self.printf(message)

    def do_show(self, line):
        """
        Display detailed information about a specified channel
        Syntax: show <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return print('Please specify a valid channel ID')

        # Attempt to fetch the requested channel
        try:
            channel = self.channel_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except ChannelNotFoundException:
            return print('No channel with the specified ID exists')

        # Set the autojoin, manage topic, and log statuses
        status = '<p class="fg-green">active</p>' if channel.autojoin else '<p class="fg-red">disabled</p>'
        manage_topic = 'Yes' if channel.manage_topic else 'No'
        log = 'Yes' if channel.log else 'No'

        # Format the response strings
        response_list = ['<strong>Name:</strong> {name}'.format(name=channel.name),
                         '<strong>Status:</strong> {status}'.format(status=status),
                         '<strong>Log:</strong> {log}'.format(log=log),
                         '<strong>Channel Password:</strong> {password}'.format(password=channel.channel_password),
                         '<strong>XOP Level:</strong> {xop}'.format(xop=channel.xop_level),
                         '<strong>Manage Topic:</strong> {manage_topic}'.format(manage_topic=manage_topic),
                         '<strong>Topic Max:</strong> {max}'.format(max=channel.topic_max),
                         '<strong>Topic Mode:</strong> {mode}'.format(mode=channel.topic_mode),
                         '<strong>Topic Separator:</strong> {separator}'.format(separator=channel.topic_separator)]

        # Return our response strings
        for response in response_list:
            self.printf(response)

    def do_enable(self, line):
        """
        Enables a channels autojoin flag
        Syntax: enable <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return print('Please specify a valid channel ID')

        # Attempt to fetch the requested channel
        try:
            channel = self.channel_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except ChannelNotFoundException:
            return print('No channel with the specified ID exists')

        # Enable autojoin
        channel.autojoin = True
        self.channel_list.dbs.commit()

        self.printf('Channel <strong>{name}</strong> successfully enabled'.format(name=channel.name))

    def do_disable(self, line):
        """
        Disables a channels autojoin flag
        Syntax: disable <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return print('Please specify a valid channel ID')

        # Attempt to fetch the requested channel
        try:
            channel = self.channel_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except ChannelNotFoundException:
            return print('No channel with the specified ID exists')

        # Enable autojoin
        channel.autojoin = False
        self.channel_list.dbs.commit()

        self.printf('Channel <strong>{name}</strong> successfully disabled'.format(name=channel.name))

    def do_edit(self, line):
        """
        Modify a channel attribute
        Syntax: edit <id> <attribute> <value>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if len(args) < 3:
            return self.printf('Not enough arguments provided. Syntax: <strong>edit <id> <attribute> <value></strong>')

        # Attempt to fetch the requested channel
        try:
            channel = self.channel_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except ChannelNotFoundException:
            return print('No channel with the specified ID exists')

        # Make sure we have a valid attribute
        attribute = str(args[1]).lower()
        value = args[2]
        if attribute not in self.channel_list.validAttributes:
            return self.printf('Invalid attribute, valid attributes include: <strong>{attrs}</srong>'
                               .format(attrs=', '.join(self.channel_list.validAttributes)))

        # Update the attribute
        name = channel.name  # Just in case we update the name attribute
        setattr(channel, attribute, value)
        self.channel_list.dbs.commit()

        return self.printf('Attribute <strong>{attr}</strong> successfully updated to <strong>{value}</strong> for '
                           'channel <strong>{name}</strong>'.format(attr=attribute, value=value, name=name))

    # noinspection PyUnboundLocalVariable
    def do_create(self, line):
        """
        Create a new channel
        Syntax: create
        """
        # Prompt for the Network to list channels on
        self.network_commands.do_list(line)
        print('\nWhich network do you want to create a channel on?')

        # Get the network to lookup on
        network = self._get_network()
        print()

        # Request / set the input attributes
        inputs = {'name': self.validated_input('name', self.validator),
                  'channel_password': self.validated_input('channel_password', self.validator, required=False),
                  'autojoin': self.validated_input('autojoin', self.validator, required=False, default=True,
                                                   yes_or_no=True),
                  'log': self.validated_input('log', self.validator, required=False, default=True, yes_or_no=True),
                  'xop_level': self.validated_input('xop_level', self.validator, required=False, default=0, cast=int),
                  'manage_topic': self.validated_input('manage_topic', self.validator, required=False, default=True,
                                                       yes_or_no=True),
                  'topic_mode': self.validated_input('topic_mode', self.validator, required=False, default='STATIC'),
                  'topic_max': self.validated_input('topic_max', self.validator, required=False, default=3, cast=int)}

        # Create the channel entry
        self.channel_list.create(network=network, **inputs)

        return self.printf('Channel <strong>{name}</strong> successfully created'.format(name=inputs['name']))

    def do_remove(self, line):
        """
        Delete an existing channel
        Syntax: remove <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return self.printf('Please specify a valid channel ID')

        # Attempt to fetch the requested channel
        try:
            channel = self.channel_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except NetworkNotFoundError:
            return print('No network with the specified ID exists')

        # Delete the channel
        name = channel.name
        self.channel_list.remove(channel)

        return self.printf('Channel <strong>{name}</strong> successfully created'.format(name=name))