import logging
from src.network import Network


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
            'Syntax: list'
        ],

        'show': [
            'Displays detailed information about the specified network.',
            'Syntax: show <strong><id></strong>'
        ],

        'enable': [
            'Enables the networks <strong>autojoin</strong> flag',
            'Syntax: enable <strong><id></strong>'
        ],

        'disable': [
            'Disables the networks <strong>autojoin</strong> flag',
            'Syntax: disable <strong><id></strong>'
        ],

        'edit': [
            'Modifies an attribute for a saved network',
            'Syntax: edit <strong><id> <attribute> <value></strong>'
        ],

        'create': [
            'Creates a new network',
            'Syntax: create <strong><name> <host> <port></strong>'
        ],

        'remove': [
            'Removes a saved network',
            'Syntax: remove <strong><id></strong>'
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

    def _get_network_by_id(self, db_id):
        """
        Retrieve a network by its database ID

        Args:
            db_id(int): The database ID

        Returns:
            database.models.Network

        Raises:
            ValueError: Raised if the supplied ID is not a valid integer
        """
        # Retrieve the network
        db_id = int(db_id)
        return self.network_list.get(db_id)

    def admin_command_list(self, command):
        """
        Lists all saved networks

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

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            return destination, "Please specify a valid network ID (See the list command)"

        # Make sure we have a valid database ID
        try:
            network = self._get_network_by_id(command.args[0])
        except ValueError:
            return destination, "Please specify a valid ignore list ID entry (See the list command)"

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

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            return destination, "Please specify a valid network ID (See the list command)"

        # Make sure we have a valid database ID
        try:
            network = self._get_network_by_id(command.args[0])
        except ValueError:
            return destination, "Please specify a valid ignore list ID entry (See the list command)"

        # Enable autojoin
        network.autojoin = True
        self.network_list.dbs.commit()

        return destination, "Network <strong>{name}</strong> successfully enabled".format(name=network.name)

    def admin_command_disable(self, command):
        """
        Disables a networks autojoin flag

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            return destination, "Please specify a valid network ID (See the list command)"

        # Make sure we have a valid database ID
        try:
            network = self._get_network_by_id(command.args[0])
        except ValueError:
            return destination, "Please specify a valid ignore list ID entry (See the list command)"

        # Enable autojoin
        network.autojoin = False
        self.network_list.dbs.commit()

        return destination, "Network <strong>{name}</strong> successfully disabled".format(name=network.name)

    def admin_command_edit(self, command):
        """
        Modify a network attribute

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            return destination, "Please specify a valid network ID (See the list command)"

        if len(command.args) < 3:
            return destination, "Syntax: <strong><id> <setting> <value></strong>"

        # Make sure we have a valid database ID
        try:
            network = self._get_network_by_id(command.args[0])
        except ValueError:
            return destination, "Please specify a valid ignore list ID entry (See the list command)"

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

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        if len(command.args) < 3:
            return destination, "Syntax: <strong><name> <host> <port></strong>"

        # Set the attributes
        name = str(command.args[0])
        host = str(command.args[1])
        try:
            port = int(command.args[2])
        except ValueError:
            return destination, "Please specify a valid port number. Syntax: <strong><name> <host> <port></strong>"

        # Create the network entry
        self.network_list.create(name, host, port)
        return destination, "Network <strong>{name}</strong> successfully created (<strong>{host}:{port}</strong>)"\
            .format(name=name, host=host, port=port)

    def admin_command_remove(self, command):
        """
        Delete an existing network

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            return destination, "Please specify a valid network ID (See the list command)"

        # Make sure we have a valid database ID
        try:
            network = self._get_network_by_id(command.args[0])
        except ValueError:
            return destination, "Please specify a valid ignore list ID entry (See the list command)"

        if not network:
            return destination, "No network with the specified ID exists"

        # Delete the network
        name = network.name
        self.log.info('Removing network "{name}" at the request of {nick}'.format(name=name, nick=command.source.nick))
        self.network_list.remove(network)

        return destination, "Network <strong>{name}</strong> successfully removed".format(name=name)