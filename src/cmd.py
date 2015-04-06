import sys
import inspect
import cmd
import logging
from src.utilities import MessageParser
from src.validator import ValidationError
from interfaces.cli.commander import CLICommander
from interfaces.cli.postmaster import Postmaster


class NanoCmd(cmd.Cmd):
    """
    Nano Cmd class
    """
    intro = 'Welcome to the Nano shell.  Type \'start\' to initialize. Type \'help\' or \'?\' to list commands.\n'
    prompt = '(nano) '
    file = None

    def __init__(self, *args):
        """
        Initialize a new Nano Cmd instance
        """
        super().__init__()
        # Debug logger
        self.log = logging.getLogger('nano.cmd')

        # Set up our CLICommander, Postmaster and MessageParser instances
        self.commander = CLICommander(self)
        self.postmaster = Postmaster(self)
        self.message_parser = MessageParser()

        # A bit of a crafty method of detecting whether or not we're initializing from another Cmd instance
        if len(args):
            # Enable the "back" command if we're in a sub-process (TODO: This is probably more accurately "home")
            setattr(self, 'do_back', self._do_back)
            self.cmdloop()

    # noinspection PyUnboundLocalVariable
    def validated_input(self, name, validator, prompt_name=None, required=True, default=None, yes_or_no=False,
                        cast=str):
        """
        Prompts for user input, validates that input, and displays an error followed by a re-prompt if validation fails

        Args:
            name(str): The name of the field being requested
            prompt_name(str or None): The public facing name of the field, defaults to a formatted version of name
            validator(method): The validation method to execute
            required(bool): Whether or not this field is required, allows empty responses if false. Defaults to True
            default(str, int or None): The default value to use when the field is not required. Defaults to None
            yes_or_no(bool): Whether the response should convert from a Y/N response to a bool. Defaults to False
            cast(class): Attempt to cast the supplied input to the specified type. Defaults to str (i.e. no casting)
        """
        # Format the prompt value
        prompt_name = prompt_name or str(name).replace('_', ' ').capitalize().strip()

        # Optional Yes or No field
        if yes_or_no and (default and not required):
            prompt_default = 'Yes' if default is True else 'No'
            prompt = '[{prompt}? (Default: {default})] '.format(prompt=prompt_name, default=prompt_default)
        # Required Yes or No field
        elif yes_or_no and (default and required):
            prompt = '[{prompt}? (Yes or No)] '.format(prompt=prompt_name)
        # Optional regular field
        elif default and not required:
            prompt = '[{prompt} (Default: {default})] '.format(prompt=prompt_name, default=default)
        # Required regular field
        else:
            prompt = '[{prompt}] '.format(prompt=prompt_name)

        # Formatting for prompts (added visbility between the prompt / input values)
        prompt = str(prompt).replace('[', '\033[1m\033[94m[\033[39m')
        prompt = str(prompt).replace(']', '\033[94m]\033[0m')

        while True:
            # Prompt the user for input
            input_response = input(prompt)

            # No response entered
            if not input_response:
                # Field is not required, return the default value
                if not required:
                    return default
                # Field is required, display an error and re-prompt
                else:
                    self.printf('The <strong>{prompt}</strong> field is required'.format(prompt=prompt_name))
                    continue

            # Is this a Yes or No response?
            if yes_or_no:
                input_response = input_response.lower().strip()
                # Yes values
                if input_response in ['y', 'yes', 'true', 'enabled']:
                    input_response = True
                elif input_response in ['n', 'no', 'false', 'disabled']:
                    input_response = False
                else:
                    self.printf('Please provide a Yes or No response for the <strong>{prompt}</strong> field')
                    continue

            # Typecasting
            if cast is not str and callable(cast):
                try:
                    input_response = cast(input_response)
                except ValueError:
                    self.printf('The <strong>{prompt}</strong> field must be a valid {type} type'
                                .format(prompt=prompt_name, type=cast.__name__))
                    continue

            # Validate the input, display an error and re-prompt if validation fails
            try:
                validator(**{name: input_response})
            except ValidationError as e:
                print(e.error_message)
                continue

            # Everything checks out, break and return the supplied input
            break

        return input_response

    def _do_back(self, arg):
        """Go back to the previous section"""
        return True

    def do_bye(self, arg):
        """Quit the shell session"""
        sys.exit()

    def get_names(self):
        """
        Custom method for pulling in base class attributes, including those programmatically created
        """
        return [name for name, method in inspect.getmembers(self) if name.startswith('do_')]

    def do_help(self, arg):
        'List available commands with "help" or detailed help with "help cmd".'
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc=inspect.getdoc(getattr(self, 'do_' + arg))
                    if doc:
                        self.stdout.write("%s\n"%str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n"%str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  list(help.keys()),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)

    def printf(self, message):
        """
        Format a message response before printing

        Args:
            message(str): The message to format
        """
        if message:
            formatted_message = self.message_parser.html_to_cli(message)
            print(formatted_message)