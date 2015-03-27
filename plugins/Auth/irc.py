import logging
from src.validator import ValidationError
from ..User.exceptions import UserDoesNotExistsError
from .module import Auth
from .exceptions import *


class Commands:
    """
    IRC Commands for the Auth module
    """
    commands_help = {
        'main': [
            'Provides user authentication and registration services.',
            'Available commands: <strong>login, logout, whoami</strong>'
        ],

        'login': [
            'Log in to an existing account. This command can not be used in public channels.',
            'Syntax: login <strong><email></strong> <strong><password></strong>'
        ],

        'logout': [
            'Destroy your current login session. This command can not be used in public channels.',
        ],

        'whoami': [
            'Returns the email of the account you are currently logged into. '
            'This command can not be used in public channels.',
        ]
    }

    def __init__(self):
        """
        Initialize a new auth Commands instance
        """
        self.auth = Auth()
        self.log = logging.getLogger('nano.modules.auth.irc.commands')

    def command_login(self, args, opts, irc, source, public, **kwargs):
        """
        Attempt to log the user in
        """
        if public:
            self.log.info('Refusing to run private command LOGIN in a public channel')
            return source.nick + ", you can't run this command in public channels, please send me a query!"

        self.log.info('Attempting to authenticate ' + source.nick)
        try:
            self.auth.attempt(args[0], args[1], str(source), irc.network)
            response = "You have successfully logged in as <strong>{login}</strong>".format(login=args[0])
            self.log.info('{nick} successfully authenticated as {login}'.format(nick=source.nick, login=args[0]))
            return 'private_notice', response
        except IndexError:
            self.log.info(source.nick + ' did not supply both an email and password when attempting to authenticate')
            return "You must specify an email and password to log in"
        except AlreadyAuthenticatedError:
            self.log.info(source.nick + ' attempted to authenticate when already authenticated')
            user = self.auth.user(str(source), irc.network)
            return "You are already logged in as {login}!".format(login=user.email)
        except ValidationError as e:
            self.log.info(source.nick + ' provided login credentials that did not pass validation')
            return e.error_message
        except (UserDoesNotExistsError, InvalidPasswordError):
            self.log.info(source.nick + ' attempted to login using an invalid email/password combination')
            return "Either no account under this email exists or you supplied an incorrect password, please double" \
                   " check your login credentials and try again"

    def command_logout(self, args, opts, irc, source, public, **kwargs):
        """
        Attempt to log the user out
        """
        if public:
            self.log.debug('Refusing to run private command LOGOUT in a public channel')
            return source.nick + ", you can't run this command in public channels, please send me a query!"

        try:
            self.auth.logout(str(source), irc.network)
            self.log.info(source.nick + ' successfully logged out')
            return "You have been successfully logged out"
        except NotAuthenticatedError:
            self.log.info(source.nick + ' attempted to log out when they were not logged in')
            return "You are not logged in"

    def command_whoami(self, args, opts, irc, source, public, **kwargs):
        """
        Return the e-mail of the account the user is currently logged into (if they are logged in)
        """
        if public:
            self.log.debug('Refusing to run private command WHOAMI in a public channel')
            return source.nick + ", you can't run this command in public channels, please send me a query!"

        if self.auth.check(str(source), irc.network):
            user = self.auth.user(str(source), irc.network)
            self.log.debug('{nick} called WHOAMI while logged in as {login}'.format(nick=source.nick, login=user.email))
            response = "You are logged in as <strong>{login}</strong>".format(login=user.email)
            return response

        self.log.debug('{nick} called WHOAMI when not logged in'.format(nick=source.nick))
        return "You are not logged in"


class Events:
    """
    IRC Events for the Auth module
    """
    def __init__(self):
        """
        Initialize a new Auth Events instance
        """
        self.auth = Auth()
        self.log = logging.getLogger('nano.modules.auth.irc.events')

    def on_quit(self, event, irc):
        """
        Destroy a users authentication session on IRC quit

        Args:
            event(irc.client.Event): The IRC event instance
            irc(NanoIRC): The IRC connection instance
        """
        self.log.debug('[QUIT] Destroying any active auth sessions for ' + event.source.nick)
        self.auth.session.destroy(network=irc.network, hostmask=event.source.host)