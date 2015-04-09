import shlex

from interfaces.cli.cmd import NanoCmd
from src.user import User, UserNotFoundError


class Commands(NanoCmd):
    """
    User management commands
    """
    prompt = '(user) '

    def __init__(self, plugin, *args, **kwargs):
        """
        Initialize a new User Commands instance
        """
        super().__init__()
        self.user_list = User()
        self.validator = self.user_list.validate.single

        # Sigh.
        if type(plugin) is str:
            self.cmdloop()

    def do_list(self, line):
        """
        Lists all registered users
        Syntax: list
        """
        # Retrieve the list of users
        users = self.user_list.all()

        if not users:
            return print('No users have been registered yet')

        # Loop through the users and print them out
        for user in users:
            # Set and print the formatted response string
            message = '<strong>{id}:</strong> {email} ({name})'
            message = message.format(id=user.id, email=user.email, name=user.nick)
            self.printf(message)

    def do_show(self, line):
        """
        Display detailed information about a specified user
        Syntax: show <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return print('Please specify a valid user ID')

        # Attempt to fetch the requested user
        try:
            user = self.user_list.get_by_id(int(args[0]))
        except ValueError:
            return print('Please specify a valid user ID')
        except UserNotFoundError:
            return print('No user with the specified ID exists')

        # Set the is_admin status
        is_admin = 'Yes' if user.is_admin else 'No'

        # Format the response strings
        response_list = ['<strong>E-Mail:</strong> {email}'.format(email=user.email),
                         '<strong>Nick:</strong> {nick}'.format(nick=user.nick),
                         '<strong>Administrator:</strong> {is_admin}'.format(is_admin=is_admin)]

        # Return our response strings
        for response in response_list:
            self.printf(response)

    def do_edit(self, line):
        """
        Modify a user attribute
        Syntax: edit <id> <attribute> <value>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if len(args) < 3:
            return self.printf('Not enough arguments provided. Syntax: <strong>edit <id> <attribute> <value></strong>')

        # Attempt to fetch the requested user
        try:
            user = self.user_list.get_by_id(int(args[0]))
        except ValueError:
            return print('Please specify a valid user ID')
        except UserNotFoundError:
            return print('No user with the specified ID exists')
        
        # Make sure we have a valid attribute
        attribute = str(args[1]).lower()
        value = args[2]
        if attribute not in self.user_list.validAttributes:
            return self.printf('Invalid attribute, valid attributes include: <strong>{attrs}</srong>'
                               .format(attrs=', '.join(self.user_list.validAttributes)))
        
        # Update the attribute
        nick = user.nick  # Just in case we update the nick attribute
        setattr(user, attribute, value)
        self.user_list.dbs.commit()
        
        return self.printf('Attribute <strong>{attr}</strong> successfully updated to <strong>{value}</strong> for '
                           'user <strong>{nick}</strong'.format(attr=attribute, value=value, nick=nick))
    
    def do_create(self, line):
        """
        Create a new user account
        Syntax: create
        """
        # Request / set the input attributes
        inputs = {'email': self.validated_input('email', self.validator),
                  'password': self.validated_input('password', self.validator),
                  'nick': self.validated_input('nick', self.validator),
                  'is_admin': self.validated_input('is_admin', self.validator, required=False, default=False, 
                                                   yes_or_no=True)}
        
        # Create the user account
        self.user_list.create(**inputs)
        
    def do_remove(self, line):
        """
        Delete an existing user
        Syntax: remove <id>
        """
        # Format our args / opts and make sure we have enough args
        args = shlex.split(line)
        if not len(args):
            return self.printf('Please specify a valid user ID')
        
        # Attempt to fetch the requested channel
        try:
            user = self.user_list.get_by_id(int(args[0]))
        except ValueError:
            return print('Please specify a valid user ID')
        except UserNotFoundError:
            return print('No user with the specified ID exists')

        # Delete the user
        email = user.email
        nick = user.nick
        self.user_list.remove(user)

        return self.printf('User <strong>{email} ({nick})</strong> successfully deleted'.format(email=email, nick=nick))