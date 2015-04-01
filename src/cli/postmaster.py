import logging


class Postmaster:
    """
    Handles CLI message deliveries
    """
    def __init__(self, cli):
        """
        Initialize a new Postmaster instance

        Args:
            irc(src.NanoIRC): The active IRC connection
        """
        self.log = logging.getLogger('nano.cli.postmaster')
        self.cli = cli

    def _fire_command(self, message):
        """
        Fire a command and cycle back to deliver its response message(s)

        Args:
            message(str): The response message or "command string"
            source(irc.client.NickMask): The NickMask of our client
            channel(database.models.Channel): The channel we are currently active in
            public(bool): Whether or not we are responding to a public message. Defaults to True
        """
        # Attempt to execute the command
        self.log.info('Attempting to execute a command from a response message')
        try:
            replies = self.cli.commander.execute(message)
        except Exception as e:
            self.log.warn('Exception thrown when executing command "{cmd}": {exception}'
                          .format(cmd=message, exception=str(e)))
            return

        self.log.info('Cycling back to deliver a command response')
        self.deliver(replies)

    def _parse_response_message(self, response):
        """
        Retrieve the message from a response and apply formatting to it

        Args:
            response(tuple or str): The response to retrieve a message from

        Returns:
            str
        """
        # Get our message from the response
        message = response[1] if isinstance(response, tuple) else str(response)

        # Format and return the message string
        message = self.cli.message_parser.html_to_cli(message)
        return message

    def deliver(self, responses):
        """
        Deliver supplied messages to their marked destinations and recipients

        Args:
            responses(list, tuple or str): The message(s) to deliver
        """
        # Make sure we actually have a response
        if not responses:
            return

        # Make sure we have a list of messages to iterate through
        if not isinstance(responses, list):
            responses = [responses]

        # Iterate through our messages
        for response in responses:
            # Fetch a formatted message from the response
            message = self._parse_response_message(response)

            # Is our destination the command handler?
            if str(response[0]).lower() == 'command':
                self._fire_command(message)
                continue

            # Deliver the message!
            self.log.info('Delivering message')
            print(message)