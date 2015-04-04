class CommandError(Exception):
    """
    Command exception master class
    """
    def __init__(self, command, error_message=None, destination=None, message=None):
        """
        Initialize a new Command Error exception instance

         Args:
            command(src.commander.Command): The command instance raising the exception
            error_message(str or None, optional): The public facing error message to return. Defaults to a pre-defined
                generic error message
            destination(str or None, optional): The error message destination. Defaults to channels for public messages
                or queries for private messages.
            message(str or None, optional): The exception error message. Defaults to None
        """
        super(CommandError, self).__init__(message)  # TODO: Is there a reason we're passing arguments to super()?
        self.command = command
        self.error_message = error_message

        # Set the error message destination
        if not destination:
            self.destination = 'public_message' if command.public else 'private_message'
        else:
            self.destination = destination


class NotEnoughArgumentsError(CommandError):
    """
    Not Enough Arguments
    """
    def __init__(self, command, min_args=None, error_message=None, destination=None, message=None):
        """
        Initialize a new Not Enough Arguments Error exception instance

        Args:
            command(src.commander.Command): The command instance raising the exception
            min_args(int or None, optional): The minimum number of required arguments
            error_message(str or None, optional): Overrides the default error message.
            destination(str or None, optional): The error message destination. Defaults to channels for public messages
                or queries for private messages.
            message(str or None, optional): The exception error message. Defaults to None
        """
        # Set the default error message
        if not error_message:
            if min_args:
                error_message = "This command requires at least <strong>{min_args}</strong> arguments. "
            else:
                error_message = "You did not provide enough arguments for this command. "

            if command.syntax:
                error_message += "Syntax: <strong>{syntax}</strong>"
            else:
                error_message += "If you need help, please try running \"help <plugin> <command>\""

        # Format the error message
        error_message = error_message.format(min_args=min_args, syntax=command.syntax)

        super(NotEnoughArgumentsError, self).__init__(command, error_message, destination, message)


class TooManyArgumentsError(CommandError):
    """
    Too Many Arguments
    """
    def __init__(self, command, max_args=None, error_message=None, destination=None, message=None):
        """
        Initialize a new Too Many Arguments Error exception instance

        Args:
            command(src.commander.Command): The command instance raising the exception
            max_args(int or None, optional): The maximum number of allowed arguments
            error_message(str or None, optional): Overrides the default error message.
            destination(str or None, optional): The error message destination. Defaults to channels for public messages
                or queries for private messages.
            message(str or None, optional): The exception error message. Defaults to None
        """
        # Set the default error message
        if not error_message:
            if max_args:
                error_message = "This command can not have more than <strong>{max_args}</strong> arguments. "
            else:
                error_message = "You provided too many arguments for this command. "

            if command.syntax:
                error_message += "Syntax: <strong>{syntax}</strong>"
            else:
                error_message += "If you need help, please try running \"help <plugin> <command>\""

        # Format the error message
        error_message = error_message.format(max_args=max_args, syntax=command.syntax)

        super(TooManyArgumentsError, self).__init__(command, error_message, destination, message)


class PermissionDeniedError(CommandError):
    """
    Permission Denied
    """
    def __init__(self, command, error_message=None, destination=None, message=None):
        """
        Initialize a new Permissions Denied Error exception instance

        Args:
            command(src.commander.Command): The command instance raising the exception
            error_message(str or None, optional): Overrides the default error message.
            destination(str or None, optional): The error message destination. Defaults to channels for public messages
                or queries for private messages.
            message(str or None, optional): The exception error message. Defaults to None
        """
        # Set the default error message
        if not error_message:
            error_message = "Access Denied. You do not have permission to perform the requested action."

        super(PermissionDeniedError, self).__init__(command, error_message, destination, message)


class InvalidSyntaxError(CommandError):
    """
    Invalid Syntax
    """
    def __init__(self, command, error_message=None, destination=None, message=None):
        """
        Initialize a new Invalid Syntax Error exception instance

        Args:
            command(src.commander.Command): The command instance raising the exception
            error_message(str or None, optional): Overrides the default error message.
            destination(str or None, optional): The error message destination. Defaults to channels for public messages
                or queries for private messages.
            message(str or None, optional): The exception error message. Defaults to None
        """
        # Set the default error message
        if not error_message:
            if command.syntax:
                error_message = "Invalid syntax. Please use the following command syntax: <strong>{syntax}</strong>"
            else:
                error_message = "Invalid syntax. If you need help, please try running \"help <plugin> <command>\""

        # Format the error message
        error_message = error_message.format(syntax=command.syntax)

        super(InvalidSyntaxError, self).__init__(command, error_message, destination, message)