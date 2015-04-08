import logging


class Postmaster:
    """
    Handles message deliveries
    """
    # Explicit destinations
    PRIVATE = "private"
    PRIVATE_NOTICE = "private_notice"
    PRIVATE_ACTION = "private_action"
    PUBLIC = "public"
    PUBLIC_NOTICE = "public_notice"
    PUBLIC_ACTION = "public_action"

    # Implicit destinations
    ACTION = "action"

    # Special destinations
    COMMAND = "command"

    _nameToDestination = {
        'PRIVATE': PRIVATE,
        'PRIVATE_NOTICE': PRIVATE_NOTICE,
        'PRIVATE_ACTION': PRIVATE_ACTION,
        'PUBLIC': PUBLIC,
        'PUBLIC_NOTICE': PUBLIC_NOTICE,
        'PUBLIC_ACTION': PUBLIC_ACTION,
        'ACTION': ACTION,
        'COMMAND': COMMAND
    }
    _destinationToName = {
        PRIVATE: 'PRIVATE',
        PRIVATE_NOTICE: 'PRIVATE_NOTICE',
        PRIVATE_ACTION: 'PRIVATE_ACTION',
        PUBLIC: 'PUBLIC',
        PUBLIC_NOTICE: 'PUBLIC_NOTICE',
        PUBLIC_ACTION: 'PUBLIC_ACTION',
        ACTION: 'ACTION',
        COMMAND: 'COMMAND'
    }

    def __init__(self, irc):
        """
        Initialize a new Postmaster instance

        Args:
            irc(src.NanoIRC): The active IRC connection
        """
        self.log = logging.getLogger('nano.irc.postmaster')
        self.irc = irc
        self.privmsg = getattr(irc.connection, 'privmsg')
        self.notice = getattr(irc.connection, 'notice')
        self.action = getattr(irc.connection, 'action')

    def _get_handler(self, response):
        """
        Returns the message handler for the supplied message's destination

        Args:
            response(tuple or str): The response message to parse

        Returns:
            (irc.client.privmsg), irc.client.notice or irc.client.action)
        """
        # Set the default handler and return if we have no explicit destination
        default_handler = self.privmsg
        if not isinstance(response, tuple):
            return default_handler

        # Retrieve our message destination
        # http://docs.python-guide.org/en/latest/writing/gotchas/#mutable-default-arguments
        # destination, message = message.popitem()
        destination, message = response

        # Channel / query responses
        if destination in [self.PRIVATE, self.PUBLIC]:
            self.log.debug('Setting the message handler to privmsg')
            return self.privmsg

        # Notice responses
        if destination in [self.PRIVATE_NOTICE, self.PUBLIC_NOTICE]:
            self.log.debug('Setting the message handler to notice')
            return self.notice

        # Action responses
        if destination in [self.PRIVATE_ACTION, self.PUBLIC_ACTION, self.ACTION]:
            self.log.debug('Setting the message handler to action')
            return self.action

        # Return our default handler if we don't recognize the request
        return default_handler

    def _get_destination(self, response, source, channel, public):
        """
        Returns the destination a supplied message should be delivered to

        Args:
            response(tuple or str): The response message to parse
            source(irc.client.NickMask): The NickMask of our client
            channel(database.models.Channel): The channel we are currently active in
            public(bool): Whether or not we are responding to a public message

        Returns:
            str
        """
        # Set the default destination and return if we have no explicit destination
        default_destination = source.nick if not public else channel.name
        if not isinstance(response, tuple):
            return default_destination

        # Retrieve our message destination
        destination, message = response

        # Debug logging stuff
        if destination in self._destinationToName:
            self.log.debug('Registering message destination as ' + self._destinationToName[destination])
        else:
            self.log.debug('Registering message destination as DEFAULT ({default})'.format(default=default_destination))

        # If we're sending an implicit action, send it to our default destination
        if destination == self.ACTION:
            return default_destination

        # If we're sending a command response, return COMMAND to trigger a firing event
        if destination == self.COMMAND:
            return self.COMMAND

        # Send private responses to the clients nick
        if destination in [self.PRIVATE, self.PRIVATE_NOTICE, self.PRIVATE_ACTION]:
            return source.nick

        # Send public responses to the active channel
        if destination in [self.PUBLIC, self.PUBLIC_NOTICE, self.PUBLIC_ACTION]:
            return channel.name

        # Return our default destination if we don't recognize the request
        return default_destination

    def _fire_command(self, message, source, channel, public):
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
            reply = self.irc.commander.execute(message, source=source, public=public)
        except Exception as e:
            self.log.warn('Exception thrown when executing command "{cmd}": {exception}'
                          .format(cmd=message, exception=str(e)))
            return

        self.log.info('Cycling back to deliver a command response')
        if reply:
            self.deliver(reply, source, channel, public)

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
        message = self.irc.message_parser.html_to_irc(message)
        message = ''.join(message.splitlines())  # Make sure no carriage returns exist in our response
        return message

    def deliver(self, responses, source, channel, public=True):
        """
        Deliver supplied messages to their marked destinations and recipients

        Args:
            responses(list, tuple or str): The message(s) to deliver
            source(irc.client.NickMask): The NickMask of our client
            channel(database.models.Channel): The channel we are currently active in
            public(bool, optional): Whether or not we are responding to a public message. Defaults to True
        """
        # Make sure we have a list of messages to iterate through
        if not isinstance(responses, list):
            responses = [responses]

        # Iterate through our messages
        for response in responses:
            # Get our message handler and destination
            handler = self._get_handler(response)
            destination = self._get_destination(response, source, channel, public)

            # Fetch a formatted message from the response
            message = self._parse_response_message(response)

            # Is our destination the command handler?
            if destination is self.COMMAND:
                self._fire_command(message, source, channel, public)
                continue

            # Deliver the message!
            self.log.info('Delivering message')
            handler(destination, message)