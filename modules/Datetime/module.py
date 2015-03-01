import datetime
import configparser
from modules.exceptions import ModuleDisabledError


class Datetime():
    def __init__(self):
        # Get the module configuration
        self.config  = configparser.ConfigParser()
        self.config.read('modules/Datetime/module.cfg')
        self.enabled = self.config.getboolean('Module', 'Enabled')
        self.now     = datetime.datetime.now()

        # Is the module enabled?
        if not self.enabled:
            raise ModuleDisabledError


    @staticmethod
    def suffix(day):
        """
        Get the English suffix for the specified day of the month
        """
        return 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    def day(self):
        """
        Get the day of the month
        """
        # Is the module enabled?
        if not self.enabled:
            return

        day = self.now.strftime("%-d")
        return day + self.suffix(int(day))

    def day_of_week(self):
        """
        Get the day of the week
        """
        # Is the module enabled?
        if not self.enabled:
            return

        return self.now.strftime("%A")

    def month(self):
        """
        Get the current month
        """
        # Is the module enabled?
        if not self.enabled:
            return

        return self.now.strftime("%B")

    def year(self):
        """
        Get the current year
        """
        # Is the module enabled?
        if not self.enabled:
            return

        return self.now.strftime("%Y")

    def time(self, timezone=False):
        """
        Return the time in the format HH:MM AM/PM
        """
        # Is the module enabled?
        if not self.enabled:
            return

        time = self.now.strftime("%-I:%M %p")

        # Are we suffixing the time zone to our result?
        if timezone:
            time = self.now.strftime("%-I:%M %p") + " " + self.now.strftime("%Z")
            time = time.rstrip(" ")

        return time