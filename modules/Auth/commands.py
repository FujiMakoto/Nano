from validator import ValidationError
from ..User.exceptions import UserDoesNotExistsError
from .module import Auth
from .exceptions import *


class AuthCommands:
    """
    IRC Commands for the Auth module
    """
    def __init__(self):
        """
        Initialize a new Auth Commands instance
        """
        self.auth = Auth()

    def command_login(self, args, opts, irc, source, public, **kwargs):
        """
        Attempt to log the user in
        """
        if public:
            return "%s, you can't run this command in public channels, please send me a query!" % source.nick

        try:
            self.auth.attempt(args[0], args[1], str(source), irc.network)
            response = "You have successfully logged in as <strong>%s</strong>" % args[0]
            return {'private_notice': response}
        except IndexError:
            return "You must specify an email and password to log in"
        except AlreadyAuthenticatedError as e:
            user = self.auth.user(str(source), irc.network)
            return "You are already logged in as %s!" % user.email
        except ValidationError as e:
            return e.error_message
        except (UserDoesNotExistsError, InvalidPasswordError):
            return "Either no account under this email exists or you supplied an incorrect password, please double" \
                   " check your login credentials and try again"

    def command_logout(self, args, opts, irc, source, public, **kwargs):
        """
        Attempt to log the user out
        """
        if public:
            return "%s, you can't run this command in public channels, please send me a query!" % source.nick

        try:
            self.auth.logout(str(source), irc.network)
            return "You have been successfully logged out"
        except NotAuthenticatedError:
            return "You are not logged in"

    def command_whoami(self, args, opts, irc, source, public, **kwargs):
        """
        Return the e-mail of the account the user is currently logged into (if they are logged in)
        """
        if public:
            return "%s, you can't run this command in public channels, please send me a query!" % source.nick

        if self.auth.check(str(source), irc.network):
            user = self.auth.user(str(source), irc.network)
            response = "You are logged in as <strong>%s</strong>" % user.email
            return response

        return "You are not logged in"