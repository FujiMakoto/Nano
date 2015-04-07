import logging

from plugins.exceptions import NotEnoughArgumentsError, InvalidSyntaxError
from interfaces.irc.ignore import IgnoreList, IgnoreEntryAlreadyExistsError


# noinspection PyMethodMayBeStatic
class Commands:
    """
    IRC Commands for the Admin Ignore plugin
    """
    commands_help = {
        'main': [
            'Manages the client ignore list.',
            'Available commands: <strong>list, add, delete, clear</strong>'
        ],

        'list': [
            'Lists all currently ignored clients.',
            'Syntax: list'
        ],

        'add': [
            'Add an annoying user to the ignore list.',
            'Syntax: add <strong><nick></strong>'
        ],

        'delete': [
            'Removes an ignore list entry by its ID.'
            'Syntax: delete <strong><id></strong>',
        ],

        'clear': [
            'Removes <strong>ALL</strong> ignore list entries.',
            'Syntax: clear'
        ]
    }

    def __init__(self, plugin):
        """
        Initialize a new Admin Ignore Commands instance

        Args:
            plugin(src.plugins.Plugin): The plugin instance
        """
        self.log = logging.getLogger('nano.plugins.admin.ignore.irc.commands')
        self.plugin = plugin
        self.ignore_list = IgnoreList()

    def _get_destination(self, public):
        """
        Get the message destination

        Args:
            public(bool): Whether or not the command was executed in a public channel
        """
        return 'private_notice' if public else 'private_message'

    def _add(self, command, whois):
        """
        Admin add command event callback

        Args:
            command(src.commander.Command): The IRC command instance
            event(list): The WHOIS event response data
        """
        destination = self._get_destination(command.public)

        # Make sure we received a whois response
        if not whois:
            return command.deliver_response((destination, "No user with the nick {nick} appears to be connected"
                                             .format(command.args[0])))

        # Attempt to add the user to the client ignore list
        try:
            whois = whois.pop(0)
            self.log.info('Adding {nick} to the client ignore list'.format(nick=command.args[0]))
            self.ignore_list.add(whois[2])
            command.irc.ignore_list.synchronize()
            return command.deliver_response((destination, "{host} ({nick}) successfully added to the ignore list"
                                            .format(host=command.args[0], nick=whois[2])))
        except IgnoreEntryAlreadyExistsError as e:
            self.log.info(e)
            return command.deliver_response((destination, "{host} ({nick}) is already on the ignore list"
                                             .format(host=command.args[0], nick=whois[2])))

    def admin_command_list(self, command):
        """
        Lists all currently ignored clients
        Syntax: admin ignore list

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        # Fetch our ignore list entries
        ignore_list = self.ignore_list.all()
        if not ignore_list:
            return destination, "There are no entries in the ignore list"

        # Loop through the entries and format them into a string response
        response_list = []
        for entry in ignore_list:
            # Append the formatted response string to our response list
            db_id, source, mask = entry
            response_list.append('<strong>{id}:</strong> {source} ({mask})'.format(id=db_id, source=source, mask=mask))

        return destination, ' '.join(response_list)

    def admin_command_add(self, command):
        """
        Adds a client to the ignore list
        Syntax: admin ignore add <nick>

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            raise NotEnoughArgumentsError(command, 1, "Please specify the nick you wish to have ignored. "
                                                      "Syntax: <strong>{syntax}</strong>", destination=destination)

        # Admin sanity check
        if str(command.source.nick).lower() == str(command.args[0]).lower():
            return destination, "You can't add yourself to the ignore list! Why would you try and do that?"

        command.bind_whois_event(command.args[0], self._add)

    def admin_command_delete(self, command):
        """
        Deletes a client from the ignore list
        Syntax: admin ignore delete <id>

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            raise NotEnoughArgumentsError(command, 1, destination=destination)

        # Make sure we have a valid database ID
        try:
            db_id = int(command.args[0])
        except ValueError:
            raise InvalidSyntaxError(command, "Please specify a valid ignore list ID entry (See the list command)",
                                     destination=destination)

        # Remove the ignore list entry
        delete_status = self.ignore_list.delete_by_id(db_id)

        if delete_status is True:
            command.irc.ignore_list.synchronize()
            return destination, "Ignore list entry successfully removed"

        return destination, "No such ignore list entry exists"

    def admin_command_clear(self, command):
        """
        Deletes all ignore list entries
        Syntax: admin ignore clear

        Args:
            command(src.Command): The IRC command instance
        """
        destination = self._get_destination(command.public)
        self.ignore_list.clear()
        command.irc.ignore_list.synchronize()
        return destination, "Ignore list cleared successfully"