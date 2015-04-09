import shlex

from interfaces.cli.cmd import NanoCmd
from interfaces.irc.network import Network, NetworkNotFoundError



# noinspection PyTypeChecker
class Commands(NanoCmd):
    """
    Network administration commands
    """
    prompt = '(network) '

    def __init__(self, plugin):
        """
        Initialize a new Admin Network Commands instance

        Args:
            plugin(src.plugins.Plugin): The plugin instance
        """
        super().__init__()
        self.plugin = plugin
        self.network_list = Network()
        self.validator = self.network_list.validate.editing

    def do_list(self, line):
        """
        Lists all saved networks
        """
        networks = self.network_list.all()

        # No networks found
        if not networks:
            return print('No networks found')

        # Loop through the networks and print them out
        for network in networks:
            # Color the network name by its autojoin status
            autojoin = bool(network.autojoin)
            color = 'green' if autojoin else 'red'

            # Set and print the formatted response string
            message = '<strong>{id}:</strong> <p class="fg-{color}">{name}</p> ({host}:{port})'
            message = message.format(id=network.id, color=color, name=network.name, host=network.host,
                                     port=network.port)
            self.printf(message)

    def do_show(self, line):
        """
        Display detailed information about a specified network
        Syntax: show <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return print('Please specify a valid network ID')

        # Attempt to fetch the requested network
        try:
            network = self.network_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except NetworkNotFoundError:
            return print('No network with the specified ID exists')

        # Set the autojoin and service statuses
        status = '<p class="fg-green">active</p>' if network.autojoin else '<p class="fg-red">disabled</p>'
        has_services = 'Yes' if network.has_services else 'No'

        # Format the response strings
        response_list = ['<strong>Name:</strong> {name}'.format(name=network.name),
                         '<strong>Status:</strong> {status}'.format(status=status),
                         '<strong>Host:</strong> {host}'.format(host=network.host),
                         '<strong>Port:</strong> {port}'.format(port=network.port),
                         '<strong>Has services:</strong> {service_status}'.format(service_status=has_services),
                         '<strong>Auth method:</strong> {auth_method}'.format(auth_method=network.auth_method)]

        if network.nick:
            response_list.append('<strong>Nick:</strong> {nick}'.format(nick=network.nick))

        # Return our response strings
        for response in response_list:
            self.printf(response)

    def do_enable(self, line):
        """
        Enables a networks autojoin flag
        Syntax: enable <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return print('Please specify a valid network ID')

        # Attempt to fetch the requested network
        try:
            network = self.network_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except NetworkNotFoundError:
            return print('No network with the specified ID exists')

        # Enable autojoin
        network.autojoin = True
        self.network_list.dbs.commit()

        self.printf('Network <strong>{name}</strong> successfully enabled'.format(name=network.name))

    def do_disable(self, line):
        """
        Disables a networks autojoin flag
        Syntax: disable <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return print('Please specify a valid network ID')

        # Attempt to fetch the requested network
        try:
            network = self.network_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except NetworkNotFoundError:
            return print('No network with the specified ID exists')

        # Disable autojoin
        network.autojoin = False
        self.network_list.dbs.commit()

        self.printf('Network <strong>{name}</strong> successfully disabled'.format(name=network.name))

    def do_edit(self, line):
        """
        Modify a network attribute
        Syntax: edit <id> <attribute> <value>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if len(args) < 3:
            return self.printf('Not enough arguments provided. Syntax: <strong>edit <id> <attribute> <value></strong>')

        # Attempt to fetch the requested network
        try:
            network = self.network_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except NetworkNotFoundError:
            return print('No network with the specified ID exists')

        # Make sure we have a valid attribute
        attribute = str(args[1]).lower()
        value = args[2]
        if attribute not in self.network_list.validAttributes:
            return self.printf('Invalid attribute, valid attributes include: <strong>{attrs}</strong>'
                               .format(attrs=', '.join(self.network_list.validAttributes)))

        # Update the attribute
        name = network.name  # Just in case we update the name attribute
        setattr(network, attribute, value)
        self.network_list.dbs.commit()

        return self.printf('Attribute <strong>{attr}</strong> successfully updated to <strong>{value}</strong> for '
                           'network <strong>{name}</strong>'.format(attr=attribute, value=value, name=name))

    def do_create(self, line):
        """
        Create a new network
        Syntax: create
        """
        # Request / set the input attributes
        inputs = {'name': self.validated_input('name', self.validator),
                  'host': self.validated_input('host', self.validator),
                  'port': self.validated_input('port', self.validator, required=False, default=6667, cast=int),
                  'nick': self.validated_input('nick', self.validator, required=False, default='Nano'),
                  'autojoin': self.validated_input('autojoin', self.validator, required=False, default=True,
                                                   yes_or_no=True),
                  'has_services': self.validated_input('has_services', self.validator, required=False, default=True,
                                                       yes_or_no=True),
                  'auth_method': self.validated_input('auth_method', self.validator, required=False),
                  'user_password': self.validated_input('user_password', self.validator, required=False),
                  'server_password': self.validated_input('server_password', self.validator, required=False)}

        # Create the network entry
        self.network_list.create(**inputs)

        return self.printf('Network <strong>{name}</strong> successfully created (<strong>{host}:{port}</strong>)'
                           .format(name=inputs['name'], host=inputs['host'], port=inputs['port']))

    def do_remove(self, line):
        """
        Delete an existing network
        Syntax: remove <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return self.printf('Please specify a valid network ID')

        # Attempt to fetch the requested network
        try:
            network = self.network_list.get(int(args[0]))
        except ValueError:
            return print('Please specify a valid network ID')
        except NetworkNotFoundError:
            return print('No network with the specified ID exists')

        # Delete the network
        name = network.name
        self.network_list.remove(network)

        return self.printf('Network <strong>{name}</strong> successfully removed'.format(name=name))