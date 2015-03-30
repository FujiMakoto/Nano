import logging
from src.ignore import IgnoreList, IgnoreEntryAlreadyExistsError


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

    def __init__(self):
        """
        Initialize a new Admin Ignore Commands instance
        """
        self.log = logging.getLogger('nano.plugins.admin.ignore.irc.commands')
        self.ignore_list = IgnoreList()
        self.whois = []

    def _get_destination(self, public):
        """
        Get the message destination

        Args:
            public(bool): Whether or not the command was executed in a public channel
        """
        return 'private_notice' if public else 'private_message'

    # TODO This is not production ready code
    def _add(self, command, irc):
        def start_whois(callback_connection, callback_event):
            irc.connection.remove_global_handler('whoisuser', start_whois)
            self.log.debug('WHOIS response: ' + str(callback_event.args))

            self.whois = callback_event.arguments

        def end_whois(callback_connection, callback_event):
            irc.connection.remove_global_handler('endofwhois', end_whois)
            self.log.debug('End of WHOIS response')
            # self.whois = []

            # Add an ignore list entry
            destination = self._get_destination(command.public)
            if not self.whois:
                irc.postmaster.deliver((destination, "No user with the nick {nick} appears to be connected."
                                       .format(nick=command.args[0])), command.source, irc.channel, command.public)
                return

            try:
                self.log.info('Adding {nick} to the client ignore list'.format(nick=self.whois[0]))
                self.ignore_list.add(self.whois[3])
                return destination, "{host} ({nick}) successfully added to the ignore list"\
                    .format(host=self.whois[0], nick=self.whois[3])
            except IgnoreEntryAlreadyExistsError as e:
                self.log.info(e)

        irc.connection.add_global_handler('whoisuser', start_whois)
        irc.connection.add_global_handler('endofwhois', end_whois)
        self.log.debug('Executing WHOIS command')
        irc.connection.whois(command.args[0])

    def admin_command_list(self, command, irc):
        """
        Lists all currently ignored clients

        Args:
            command(src.Command): The IRC command instance
            irc(src.NanoIRC): The IRC connection instance
        """
        destination = self._get_destination(command.public)
        # Fetch our ignore list entries
        ignore_list = self.ignore_list.all()
        if not ignore_list:
            return destination, "There are no entries in the ignore list."

        # Loop through the entries and format them into a string response
        response_list = []
        for entry in ignore_list:
            # Append the formatted the response string to our response list
            db_id, source, mask = entry
            response_list.append('<strong>{id}:</strong> {source} ({mask})'.format(id=db_id, source=source, mask=mask))

        return destination, ' '.join(response_list)

    def admin_command_add(self, command, irc):
        """
        Adds a client to the ignore list

        Args:
            command(src.Command): The IRC command instance
            irc(src.NanoIRC): The IRC connection instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            return destination, "Please specify the nick you wish to have ignored."

        self._add(command, irc)

    def admin_command_delete(self, command, irc):
        """
        Deletes a client from the ignore list

        Args:
            command(src.Command): The IRC command instance
            irc(src.NanoIRC): The IRC connection instance
        """
        destination = self._get_destination(command.public)
        if not len(command.args):
            return destination, "Please specify the ID of the ignore entry you wish to remove. (See the list command)"

        # Make sure we have a valid database ID
        try:
            db_id = int(command.args[0])
        except ValueError:
            return destination, "Please specify a valid ignore list ID entry. (See the list command)"

        # Remove the ignore list entry
        delete_status = self.ignore_list.delete_by_id(db_id)

        if delete_status is True:
            return destination, "Ignore list entry successfully removed."

        return destination, "No such ignore list entry exists."

    def admin_command_clear(self, command, irc):
        """
        Deletes all ignore list entries

        Args:
            command(src.Command): The IRC command instance
            irc(src.NanoIRC): The IRC connection instance
        """
        destination = self._get_destination(command.public)
        self.ignore_list.clear()
        return destination, "Ignore list cleared successfully."