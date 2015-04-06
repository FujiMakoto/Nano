from src.cmd import NanoCmd
from interfaces.irc.network import Network


class Commands(NanoCmd):
    """
    Network administration commands
    """
    prompt = '(network) '

    def __init__(self):
        """
        Initialize a new Admin Network Commands instance
        """
        super().__init__()
        self.network_list = Network()

    def _get_network_by_id(self, db_id):
        """
        Retrieve a network by its database ID

        Args:
            db_id(int): The database ID
            command(src.Command): The IRC command instance
            destination(str): The message destination

        Returns:
            database.models.Network

        Raises:
            InvalidSyntaxError: Raised if the supplied ID is not a valid integer
        """
        # Retrieve the network
        try:
            db_id = int(db_id)
        except ValueError:
            return False

        return self.network_list.get(db_id)

    def do_list(self, arg):
        """
        Lists all saved networks
        """
        networks = self.network_list.all()

        # No networks found
        if not networks:
            print('No networks found')

        # Loop through the networks and print them out
        for network in networks:
            # Color the network name by its autojoin status
            autojoin = bool(network.autojoin)
            color = 'green' if autojoin else 'red'

            # Set and return the formatted response string
            message = '<strong>{id}:</strong> <p class="fg-{color}">{name}</p> ({host}:{port})'
            message = message.format(id=network.id, color=color, name=network.name, host=network.host,
                                     port=network.port)
            self.printf(message)

    def do_show(self, line):
        """
        Display detailed information about the specified network
        Syntax: show <id>
        """
        # Format our args / opts and make sure we have enough args
        args, opts = self.commander.parse_line(line)
        if not len(args):
            return print('Please specify a valid network ID')

        # Attempt to fetch the requested network
        network = self._get_network_by_id(args[0])

        if network is False:
            return print('Please specify a valid network ID')
        if network is None:
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
        args, opts = self.commander.parse_line(line)
        if not len(args):
            return print('Please specify a valid network ID')

        # Attempt to fetch the requested network
        network = self._get_network_by_id(args[0])

        if network is False:
            return print('Please specify a valid network ID')
        if network is None:
            return print('No network with the specified ID exists')

        # Enable autojoin
        network.autojoin = True
        self.network_list.dbs.commit()

        self.printf("Network <strong>{name}</strong> successfully enabled".format(name=network.name))

    def do_disable(self, line):
        """
        Disables a networks autojoin flag
        Syntax: disable <id>
        """
        # Format our args / opts and make sure we have enough args
        args, opts = self.commander.parse_line(line)
        if not len(args):
            return print('Please specify a valid network ID')

        # Attempt to fetch the requested network
        network = self._get_network_by_id(args[0])

        if network is False:
            return print('Please specify a valid network ID')
        if network is None:
            return print('No network with the specified ID exists')

        # Disable autojoin
        network.autojoin = False
        self.network_list.dbs.commit()

        self.printf("Network <strong>{name}</strong> successfully disabled".format(name=network.name))

    def do_edit(self, line):
        """
        Modify a network attribute
        Syntax: edit <id> <attribute> <value>
        """
        # Format our args / opts and make sure we have enough args
        args, opts = self.commander.parse_line(line)
        if len(args) < 3:
            return self.printf('Not enough arguments provided. Syntax: <strong>edit <id> <attribute> <value></strong>')

        # Attempt to fetch the requested network
        network = self._get_network_by_id(args[0])

        if network is False:
            return print('Please specify a valid network ID')
        if network is None:
            return print('No network with the specified ID exists')

        # Make sure we have a valid attribute
        attribute = str(args[1]).lower()
        value = args[2]
        if attribute not in self.network_list.validAttributes:
            return self.printf("Invalid attribute, valid attributes include: <strong>{attrs}</strong>"
                               .format(attrs=', '.join(self.network_list.validAttributes)))

        # Update the attribute
        name = network.name  # Just in case we update the name attribute
        setattr(network, attribute, value)
        self.network_list.dbs.commit()

        return self.printf("Attribute <strong>{attr}</strong> successfully updated to <strong>{value}</strong> for "
                           "network <strong>{name}</strong>".format(attr=attribute, value=value, name=name))

    def do_create(self, line):
        """
        Create a new network
        Syntax: create <name> <host> <port>
        """
        # Format our args / opts and make sure we have enough args
        args, opts = self.commander.parse_line(line)
        if len(args) < 3:
            return self.printf('Not enough arguments provided. Syntax: <strong>create <name> <host> <port></strong>')

        # Set the attributes
        name = str(args[0])
        host = str(args[1])
        try:
            port = int(args[2])
        except ValueError:
            return print('Please specify a valid port number')

        # Create the network entry
        self.network_list.create(name, host, port)

        return self.printf("Network <strong>{name}</strong> successfully created (<strong>{host}:{port}</strong>)"
                           .format(name=name, host=host, port=port))

    def do_remove(self, line):
        """
        Delete an existing network
        Syntax: delete <id>
        """
        # Format our args / opts and make sure we have enough args
        args, opts = self.commander.parse_line(line)
        if not len(args):
            return self.printf('Please specify a valid network ID')

        # Attempt to fetch the requested network
        network = self._get_network_by_id(args[0])

        if network is False:
            return print('Please specify a valid network ID')
        if network is None:
            return print('No network with the specified ID exists')

        # Delete the network
        name = network.name
        self.network_list.remove(network)

        return self.printf("Network <strong>{name}</strong> successfully removed".format(name=name))