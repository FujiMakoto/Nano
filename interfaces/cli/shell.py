import cmd


class NanoShell(cmd.Cmd):
    """
    Nano shell interpreter
    """
    intro = 'Welcome to the Nano shell.  Type \'start\' to initialize. Type \'help\' or \'?\' to list commands.\n'
    prompt = '(nano) '
    file = None

    def __init__(self, nano, cli):
        """
        Initialize a new Nano Shell instance

        Args:
            nano(Nano): The master Nano class instance
            cli(src.cli.nano_cli.NanoCLI): The Nano CLI instance
        """
        super().__init__()
        self.nano = nano
        self.cli = cli

    def do_start(self, arg):
        """Establish connections on all enabled protocols"""
        self.nano.irc()

    def do_chat(self, arg):
        """Initialize a chat session with Nano"""
        ChatShell(self.cli).start()

    def do_bye(self, arg):
        """Quit the shell session"""
        print('Bye!')
        return True

    def precmd(self, line):
        """
        Command pre-processing

        Args:
            line(str): The line to pre-process
        """
        return line.lower()


class ChatShell():
    """
    Nano conversation shell
    """
    def __init__(self, cli):
        """
        Initialize a new Chat Shell instance

        Args:
            cli(src.cli.nano_cli.NanoCLI): The Nano CLI instance
        """
        self.cli = cli

    def start(self):
        """
        Start the chat session
        """
        while True:
            message = input('You> ')
            if message == '/quit':
                break

            print('Nano> ', end='')
            self.cli.get_replies(message)
            print()