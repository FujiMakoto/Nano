import re
import logging
from html.parser import unescape


class MessageParser:
    """
    Universal message parsing for the CLI, IRC and web based protocols
    """
    # IRC Contextual controls
    IRC_BOLD = "\x02"
    IRC_ITALICS = "\x1D"
    IRC_UNDERLINE = "\x1F"
    IRC_COLOR = "\x03"

    _nameToIRCContext = {
        'IRC_BOLD': IRC_BOLD,
        'IRC_ITALICS': IRC_ITALICS,
        'IRC_UNDERLINE': IRC_UNDERLINE,
        'IRC_COLOR': IRC_COLOR
    }
    _IRCContextToName = {
        IRC_BOLD: 'IRC_BOLD',
        IRC_ITALICS: 'IRC_ITALICS',
        IRC_UNDERLINE: 'IRC_UNDERLINE',
        IRC_COLOR: 'IRC_COLOR'
    }

    # IRC color formatting codes
    IRC_WHITE = "00"
    IRC_BLACK = "01"
    IRC_BLUE = "02"
    IRC_GREEN = "03"
    IRC_RED = "04"
    IRC_BROWN = "05"
    IRC_PURPLE = "06"
    IRC_ORANGE = "07"
    IRC_YELLOW = "08"
    IRC_LIME = "09"
    IRC_TEAL = "10"
    IRC_AQUA = "11"
    IRC_ROYAL = "12"
    IRC_PINK = "13"
    IRC_GREY = "14"
    IRC_SILVER = "15"

    _nameToIRCColor = {
        'IRC_WHITE': IRC_WHITE,
        'IRC_BLACK': IRC_BLACK,
        'IRC_BLUE': IRC_BLUE,
        'IRC_GREEN': IRC_GREEN,
        'IRC_RED': IRC_RED,
        'IRC_BROWN': IRC_BROWN,
        'IRC_PURPLE': IRC_PURPLE,
        'IRC_ORANGE': IRC_ORANGE,
        'IRC_YELLOW': IRC_YELLOW,
        'IRC_LIME': IRC_LIME,
        'IRC_TEAL': IRC_TEAL,
        'IRC_AQUA': IRC_AQUA,
        'IRC_ROYAL': IRC_ROYAL,
        'IRC_PINK': IRC_PINK,
        'IRC_GREY': IRC_GREY,
        'IRC_SILVER': IRC_SILVER
    }
    _IRCColorToName = {
        IRC_WHITE: 'IRC_WHITE',
        IRC_BLACK: 'IRC_BLACK',
        IRC_BLUE: 'IRC_BLUE',
        IRC_GREEN: 'IRC_GREEN',
        IRC_RED: 'IRC_RED',
        IRC_BROWN: 'IRC_BROWN',
        IRC_PURPLE: 'IRC_PURPLE',
        IRC_ORANGE: 'IRC_ORANGE',
        IRC_YELLOW: 'IRC_YELLOW',
        IRC_LIME: 'IRC_LIME',
        IRC_TEAL: 'IRC_TEAL',
        IRC_AQUA: 'IRC_AQUA',
        IRC_ROYAL: 'IRC_ROYAL',
        IRC_PINK: 'IRC_PINK',
        IRC_GREY: 'IRC_GREY',
        IRC_SILVER: 'IRC_SILVER'
    }

    # CLI ANSI controls
    CLI_RESET = '\033[0m'  # Toggle's for bold, italics and underline are not widely supported, so we have to use reset
    CLI_BOLD = "\033[1m"
    CLI_ITALICS = "\033[3m"  # Not widely supported
    CLI_UNDERLINE = "\033[4m"

    _nameToCLIContext = {
        'CLI_RESET': CLI_RESET,
        'CLI_BOLD': CLI_BOLD,
        'CLI_ITALICS': CLI_ITALICS,
        'CLI_UNDERLINE': CLI_UNDERLINE,
    }
    _CLIContextToName = {
        CLI_RESET: 'CLI_RESET',
        CLI_BOLD: 'CLI_BOLD',
        CLI_ITALICS: 'CLI_ITALICS',
        CLI_UNDERLINE: 'CLI_UNDERLINE',
    }

    # CLI ANSI color formatting codes
    CLI_DEFAULT = "\033[39m"
    CLI_WHITE = "\033[97m"
    CLI_BLACK = "\033[30m"
    CLI_BLUE = "\033[34m"
    CLI_GREEN = "\033[32m"
    CLI_RED = "\033[31m"
    CLI_BROWN = "\033[33m"
    CLI_PURPLE = "\033[35m"
    CLI_ORANGE = "\033[33m"  # Actually brown / yellow
    CLI_YELLOW = "\033[93m"
    CLI_LIME = "\033[92m"
    CLI_TEAL = "\033[36m"
    CLI_AQUA = "\033[96m"
    CLI_ROYAL = "\033[94m"
    CLI_PINK = "\033[95m"
    CLI_GREY = "\033[37m"
    CLI_SILVER = "\033[37m"
    
    _nameToCLIColor = {
        'CLI_WHITE': CLI_WHITE,
        'CLI_BLACK': CLI_BLACK,
        'CLI_BLUE': CLI_BLUE,
        'CLI_GREEN': CLI_GREEN,
        'CLI_RED': CLI_RED,
        'CLI_BROWN': CLI_BROWN,
        'CLI_PURPLE': CLI_PURPLE,
        'CLI_ORANGE': CLI_ORANGE,
        'CLI_YELLOW': CLI_YELLOW,
        'CLI_LIME': CLI_LIME,
        'CLI_TEAL': CLI_TEAL,
        'CLI_AQUA': CLI_AQUA,
        'CLI_ROYAL': CLI_ROYAL,
        'CLI_PINK': CLI_PINK,
        'CLI_GREY': CLI_GREY,
        'CLI_SILVER': CLI_SILVER
    }
    _CLIColorToName = {
        CLI_WHITE: 'CLI_WHITE',
        CLI_BLACK: 'CLI_BLACK',
        CLI_BLUE: 'CLI_BLUE',
        CLI_GREEN: 'CLI_GREEN',
        CLI_RED: 'CLI_RED',
        CLI_BROWN: 'CLI_BROWN',
        CLI_PURPLE: 'CLI_PURPLE',
        CLI_ORANGE: 'CLI_ORANGE',
        CLI_YELLOW: 'CLI_YELLOW',
        CLI_LIME: 'CLI_LIME',
        CLI_TEAL: 'CLI_TEAL',
        CLI_AQUA: 'CLI_AQUA',
        CLI_ROYAL: 'CLI_ROYAL',
        CLI_PINK: 'CLI_PINK',
        CLI_GREY: 'CLI_GREY',
        CLI_SILVER: 'CLI_SILVER'
    }
    
    # CLI ANSI background color formatting codes
    CLI_BG_DEFAULT = "\033[49m"
    CLI_BG_WHITE = "\033[107m"
    CLI_BG_BLACK = "\033[40m"
    CLI_BG_BLUE = "\033[44m"
    CLI_BG_GREEN = "\033[42m"
    CLI_BG_RED = "\033[41m"
    CLI_BG_BROWN = "\033[43m"
    CLI_BG_PURPLE = "\033[45m"
    CLI_BG_ORANGE = "\033[43m"  # Actually brown / yellow
    CLI_BG_YELLOW = "\033[103m"
    CLI_BG_LIME = "\033[102m"
    CLI_BG_TEAL = "\033[46m"
    CLI_BG_AQUA = "\033[106m"
    CLI_BG_ROYAL = "\033[104m"
    CLI_BG_PINK = "\033[105m"
    CLI_BG_GREY = "\033[47m"
    CLI_BG_SILVER = "\033[47m"
    
    _nameToCLIBackgroundColor = {
        'CLI_BG_DEFAULT': CLI_BG_DEFAULT,
        'CLI_BG_WHITE': CLI_BG_WHITE,
        'CLI_BG_BLACK': CLI_BG_BLACK,
        'CLI_BG_BLUE': CLI_BG_BLUE,
        'CLI_BG_GREEN': CLI_BG_GREEN,
        'CLI_BG_RED': CLI_BG_RED,
        'CLI_BG_BROWN': CLI_BG_BROWN,
        'CLI_BG_PURPLE': CLI_BG_PURPLE,
        'CLI_BG_ORANGE': CLI_BG_ORANGE,
        'CLI_BG_YELLOW': CLI_BG_YELLOW,
        'CLI_BG_LIME': CLI_BG_LIME,
        'CLI_BG_TEAL': CLI_BG_TEAL,
        'CLI_BG_AQUA': CLI_BG_AQUA,
        'CLI_BG_ROYAL': CLI_BG_ROYAL,
        'CLI_BG_PINK': CLI_BG_PINK,
        'CLI_BG_GREY': CLI_BG_GREY,
        'CLI_BG_SILVER': CLI_BG_SILVER
    }
    _CLIBackgroundColorToName = {
        CLI_BG_DEFAULT: 'CLI_BG_DEFAULT',
        CLI_BG_WHITE: 'CLI_BG_WHITE',
        CLI_BG_BLACK: 'CLI_BG_BLACK',
        CLI_BG_BLUE: 'CLI_BG_BLUE',
        CLI_BG_GREEN: 'CLI_BG_GREEN',
        CLI_BG_RED: 'CLI_BG_RED',
        CLI_BG_BROWN: 'CLI_BG_BROWN',
        CLI_BG_PURPLE: 'CLI_BG_PURPLE',
        CLI_BG_ORANGE: 'CLI_BG_ORANGE',
        CLI_BG_YELLOW: 'CLI_BG_YELLOW',
        CLI_BG_LIME: 'CLI_BG_LIME',
        CLI_BG_TEAL: 'CLI_BG_TEAL',
        CLI_BG_AQUA: 'CLI_BG_AQUA',
        CLI_BG_ROYAL: 'CLI_BG_ROYAL',
        CLI_BG_PINK: 'CLI_BG_PINK',
        CLI_BG_GREY: 'CLI_BG_GREY',
        CLI_BG_SILVER: 'CLI_BG_SILVER'
    }

    def __init__(self):
        """
        Initialize a new Message Parser instance
        """
        # Bold, Italics, Underline
        self.html_bold = re.compile("(<strong>|</strong>)", re.UNICODE)
        self.html_italics = re.compile("(<em>|</em>)", re.UNICODE)
        self.html_underline = re.compile("(<u>|</u>)", re.UNICODE)

        self.html_bold_start = re.compile("<strong>", re.UNICODE)
        self.html_italics_start = re.compile("<em>", re.UNICODE)
        self.html_underline_start = re.compile("<u>", re.UNICODE)

        self.html_bold_stop = re.compile("(</strong>)", re.UNICODE)
        self.html_italics_stop = re.compile("(</em>)", re.UNICODE)
        self.html_underline_stop = re.compile("(</u>)", re.UNICODE)

        # These aren't really useful at the moment, don't try and use them
        self.irc_bold = re.compile(re.escape(self.IRC_BOLD), re.UNICODE)
        self.irc_italics = re.compile(re.escape(self.IRC_ITALICS), re.UNICODE)
        self.irc_underline = re.compile(re.escape(self.IRC_UNDERLINE), re.UNICODE)

        self.cli_reset = re.compile(re.escape(self.CLI_RESET), re.UNICODE)
        self.cli_bold = re.compile(re.escape(self.CLI_BOLD), re.UNICODE)
        self.cli_italics = re.compile(re.escape(self.CLI_ITALICS), re.UNICODE)
        self.cli_underline = re.compile(re.escape(self.CLI_UNDERLINE), re.UNICODE)

        # Color formatting
        self.html_color = re.compile("(?P<opening_tag><p(\s)?\sclass=[\"']([a-zA-Z-_\s]+\s)?(fg-|bg-)([A-Za-z]+)"
                                     "(\s[a-zA-Z-_\s]+)?[\"'](\s)?>)(?P<message>[^<]+)(<\/p>)", re.UNICODE)
        self.html_fg_color = re.compile("(?P<opening_tag><p(\s.*)?\sclass=[\"'](.*\s)?fg-(?P<fg_color>[A-Za-z]+)(\s.*)?"
                                        "[\"'](\s.*)?>)", re.UNICODE)
        self.html_bg_color = re.compile("(?P<opening_tag><p(\s.*)?\sclass=[\"'](.*\s)?bg-(?P<bg_color>[A-Za-z]+)(\s.*)?"
                                        "[\"'](\s.*)?>)", re.UNICODE)

    def html_to_irc(self, message):
        """
        Replaces HTML contextual formatting with IRC control codes

        Args:
            message(str): The message to format

        Returns:
            str
        """
        # Bold, Italics, Underline
        message = self.html_bold.sub(self.IRC_BOLD, message)
        message = self.html_italics.sub(self.IRC_ITALICS, message)
        message = self.html_underline.sub(self.IRC_UNDERLINE, message)

        # Color code replacement method
        def color_replace(match):
            fg_match = self.html_fg_color.match(match.group('opening_tag'))
            bg_match = self.html_bg_color.match(match.group('opening_tag'))

            # Set foreground / background colors
            fg_color = self.IRC_BLACK
            bg_color = None

            # Foreground
            if fg_match:
                fg_color_name = 'IRC_' + fg_match.group('fg_color').upper()
                if fg_color_name in self._nameToIRCColor:
                    fg_color = self._nameToIRCColor[fg_color_name]
            # Background
            if bg_match:
                bg_color_name = 'IRC_' + bg_match.group('bg_color').upper()
                if bg_color_name in self._nameToIRCColor:
                    bg_color = self._nameToIRCColor[bg_color_name]

            # Apply foreground / background colors
            if fg_match or bg_match:
                # Foreground and background or foreground only?
                if bg_color:
                    message_template = "{color_ctrl}{fg_code},{bg_code}{message}{color_ctrl}"
                else:
                    message_template = "{color_ctrl}{fg_code}{message}{color_ctrl}"

                # Format the message template
                formatted = message_template.format(color_ctrl=self.IRC_COLOR, fg_code=fg_color, bg_code=bg_color,
                                                    message=match.group('message'))
                return formatted

        # Substitute foreground / background color matches
        message = self.html_color.sub(color_replace, message)

        # Unescape HTML entities
        message = unescape(message)

        # Return the formatted message
        return message

    def html_to_cli(self, message):
        """
        Replaces HTML contextual formatting with CLI ANSI codes

        Args:
            message(str): The message to format

        Returns:
            str
        """
        # Bold, Italics, Underline
        message = self.html_bold_start.sub(self.CLI_BOLD, message)
        message = self.html_bold_stop.sub(self.CLI_RESET, message)

        message = self.html_italics_start.sub(self.CLI_ITALICS, message)
        message = self.html_italics_stop.sub(self.CLI_RESET, message)

        message = self.html_underline_start.sub(self.CLI_UNDERLINE, message)
        message = self.html_underline_stop.sub(self.CLI_RESET, message)

        # Color code replacement method
        def color_replace(match):
            fg_match = self.html_fg_color.match(match.group('opening_tag'))
            bg_match = self.html_bg_color.match(match.group('opening_tag'))

            # Set foreground / background colors
            fg_color = self.CLI_DEFAULT
            bg_color = None

            # Foreground
            if fg_match:
                fg_color_name = 'CLI_' + fg_match.group('fg_color').upper()
                if fg_color_name in self._nameToCLIColor:
                    fg_color = self._nameToCLIColor[fg_color_name]
            # Background
            if bg_match:
                bg_color_name = 'CLI_BG_' + bg_match.group('bg_color').upper()
                if bg_color_name in self._nameToCLIBackgroundColor:
                    bg_color = self._nameToCLIBackgroundColor[bg_color_name]

            # Apply foreground / background colors
            if fg_match or bg_match:
                # Foreground and background or foreground only?
                if bg_color:
                    message_template = "{fg_code}{bg_code}{message}{bg_default}{fg_default}"
                else:
                    message_template = "{fg_code}{message}{fg_default}"

                # Format the message template
                formatted = message_template.format(fg_code=fg_color, bg_code=bg_color, message=match.group('message'),
                                                    bg_default=self.CLI_BG_DEFAULT, fg_default=self.CLI_DEFAULT)
                return formatted

        # Substitute foreground / background color matches
        message = self.html_color.sub(color_replace, message)

        # Unescape HTML entities
        message = unescape(message)

        # Return the formatted message
        return message