import logging

from interfaces.irc.network import Network
from plugins.exceptions import NotEnoughArgumentsError, InvalidSyntaxError


# noinspection PyMethodMayBeStatic
class Commands:
    """
    IRC Commands for the Admin Network plugin
    """
    commands_help = {
        'main': [
            'Manages the IRC network list',
            'Available commands: <strong>list, show, enable, disable, edit, create, remove</strong>'
        ],

        'list': [
            'Lists all saved networks',
            'Syntax: admin network list'
        ],

        'show': [
            'Displays detailed information about the specified network.',
            'Syntax: admin network show <strong><id></strong>'
        ],

        'enable': [
            'Enables the networks <strong>autojoin</strong> flag',
            'Syntax: admin network enable <strong><id></strong>'
        ],

        'disable': [
            'Disables the networks <strong>autojoin</strong> flag',
            'Syntax: admin network disable <strong><id></strong>'
        ],

        'edit': [
            'Modifies an attribute for a saved network',
            'Syntax: admin network edit <strong><id> <attribute> <value></strong>'
        ],

        'create': [
            'Creates a new network',
            'Syntax: admin network create <strong><name> <host> <port></strong>'
        ],

        'remove': [
            'Removes a saved network',
            'Syntax: admin network remove <strong><id></strong>'
        ],
    }

    def __init__(self):
        """
        Initialize a new Admin Network Commands instance
        """
        self.log = logging.getLogger('nano.plugins.admin.network.irc.commands')
        self.network_list = Network()

    def _get_destination(self, public):
        """
        Get the message destination

        Args:
            public(bool): Whether or not the command was executed in a public channel
        """
        return 'private_notice' if public else 'private_message'

    def _get_network_by_id(self, db_id, command, destination):
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
            raise InvalidSyntaxError(command, message='Please specify a valid network ID', destination=destination)

        return self.network_list.get(db_id)

    def admin_command_list(self, command):
        """
        Lists all saved networks
        Syntax: admin network list

        Args:
            command(src.Command): The IRC command instance
        """
        self.log.info('Returning a list of networks to ' + command.source.nick)
        destination = self._get_destination(command.public)
        networks = self.network_list.all()

        # It's possible to have no networks returned if we deleted the last network while still connected
        if not networks:
            return destination, "No networks found, did you delete the last one while connected?"

        # Loop through the networks and format them into a string response
        response_list = []
        for network in networks:
            autojoin = bool(network.autojoin)
            color = 'green' if autojoin else 'red'
            # Append the formatted response string to our response list
            response_list.append('<strong>{id}:</strong> <p class="fg-{color}">{name}</p> ({host}:{port})'
                                 .format(id=network.id, color=color, name=network.name, host=network.host,
                                         port=network.port))

        return destination, ' '.join(response_list)

    def admin_command_show(self, command):
        """
        Display detailed information about the specified network
        Syntax: admin network show <id>

        Args:
            command(src.Command): The IRC command instance

        Raises:
            NotEnoughArgumentsError: Command requires 1 argument
            InvalidSyntaxError: Argument 1 must be a valid integer
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            raise NotEnoughArgumentsError(command, error_message='Please specify a valid network ID',
                                          destination=destination)

        # Make sure we have a valid database ID
        network = self._get_network_by_id(command.args[0], command, destination)

        if not network:
            return destination, "No network with the specified ID exists"

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

        # Join our response list and return
        self.log.info('Returning network information to ' + command.source.nick)
        return destination, ' '.join(response_list)

    def admin_command_enable(self, command):
        """
        Enables a networks autojoin flag
        Syntax: admin network enable <id>

        Args:
            command(src.Command): The IRC command instance

        Raises:
            NotEnoughArgumentsError: Command requires 1 argument
            InvalidSyntaxError: Argument 1 must be a valid integer
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            raise NotEnoughArgumentsError(command, error_message='Please specify a valid network ID',
                                          destination=destination)

        # Make sure we have a valid database ID
        network = self._get_network_by_id(command.args[0], command, destination)

        # Enable autojoin
        network.autojoin = True
        self.network_list.dbs.commit()

        return destination, "Network <strong>{name}</strong> successfully enabled".format(name=network.name)

    def admin_command_disable(self, command):
        """
        Disables a networks autojoin flag
        Syntax: admin network disable <id>

        Args:
            command(src.Command): The IRC command instance

        Raises:
            NotEnoughArgumentsError: Command requires 1 argument
            InvalidSyntaxError: Argument 1 (db_id) must be a valid integer
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            raise NotEnoughArgumentsError(command, error_message='Please specify a valid network ID',
                                          destination=destination)

        # Make sure we have a valid database ID
        network = self._get_network_by_id(command.args[0], command, destination)

        # Enable autojoin
        network.autojoin = False
        self.network_list.dbs.commit()

        return destination, "Network <strong>{name}</strong> successfully disabled".format(name=network.name)

    def admin_command_edit(self, command):
        """
        Modify a network attribute
        Syntax: admin network edit <id> <attribute> <value>

        Args:
            command(src.Command): The IRC command instance

        Raises:
            NotEnoughArgumentsError: Command requires 3 arguments
            InvalidSyntaxError: Argument 1 (db_id) must be a valid integer
        """
        destination = self._get_destination(command.public)
        if len(command.args) < 3: raise NotEnoughArgumentsError(command, 3)

        # Make sure we have a valid database ID
        network = self._get_network_by_id(command.args[0], command, destination)

        # Make sure we have a valid attribute
        attribute = str(command.args[1]).lower()
        value = command.args[2]
        if attribute not in self.network_list.validAttributes:
            return destination, "Invalid attribute, valid attributes include: <strong>{attrs}</strong>"\
                .format(attrs=', '.join(self.network_list.validAttributes))

        if not network:
            return destination, "No network with the specified ID exists"

        # Update the attribute
        name = network.name  # Just in case we update the name attribute
        setattr(network, attribute, value)
        self.network_list.dbs.commit()
        self.log.info('{network} network attribute "{attr}" updated to "{value}" by {nick}'
                      .format(network=name, attr=attribute, value=value, nick=command.source.nick))

        return destination, "Attribute <strong>{attr}</strong> successfully updated to <strong>{value}</strong> for"\
                            " network <strong>{name}</strong>".format(attr=attribute, value=value, name=name)

    def admin_command_create(self, command):
        """
        Create a new network
        Syntax: admin network create <name> <host> <port>

        Args:
            command(src.Command): The IRC command instance

        Raises:
            NotEnoughArgumentsError: Command requires 3 arguments
            InvalidSyntaxError: Argument 3 (port) must be a valid integer
        """
        destination = self._get_destination(command.public)
        if len(command.args) < 3: raise NotEnoughArgumentsError(command, 3)

        # Set the attributes
        name = str(command.args[0])
        host = str(command.args[1])
        try:
            port = int(command.args[2])
        except ValueError:
            raise InvalidSyntaxError(command, 'Please specify a valid port number. Syntax: admin network <strong>{syntax}</strong>',
                                     destination=destination)

        # Create the network entry
        self.network_list.create(name, host, port)

        return destination, "Network <strong>{name}</strong> successfully created (<strong>{host}:{port}</strong>)"\
            .format(name=name, host=host, port=port)

    def admin_command_remove(self, command):
        """
        Delete an existing network
        Syntax: admin network delete <id>

        Args:
            command(src.Command): The IRC command instance

        Raises:
            NotEnoughArgumentsError: Command requires 1 argument
            InvalidSyntaxError: Argument 1 (db_id) must be a valid integer
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            raise NotEnoughArgumentsError(command, error_message='Please specify a valid network ID',
                                          destination=destination)

        # Make sure we have a valid database ID
        network = self._get_network_by_id(command.args[0], command, destination)

        if not network:
            return destination, "No network with the specified ID exists"

        # Delete the network
        name = network.name
        self.log.info('Removing network "{name}" at the request of {nick}'.format(name=name, nick=command.source.nick))
        self.network_list.remove(network)

        return destination, "Network <strong>{name}</strong> successfully removed".format(name=name)