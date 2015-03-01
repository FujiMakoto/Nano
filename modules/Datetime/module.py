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
        :return: str
        """
        return 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    def day(self):
        """
        Get the day of the month
        :return: str
        """
        # Is the module enabled?
        if not self.enabled:
            return

        day = self.now.strftime("%-d")
        return day + self.suffix(int(day))

    def day_of_week(self):
        """
        Get the day of the week
        :return: str
        """
        # Is the module enabled?
        if not self.enabled:
            return

        return self.now.strftime("%A")

    def month(self):
        """
        Get the current month
        :return: str
        """
        # Is the module enabled?
        if not self.enabled:
            return

        return self.now.strftime("%B")

    def year(self):
        """
        Get the current year
        :return: str
        """
        # Is the module enabled?
        if not self.enabled:
            return

        return self.now.strftime("%Y")

    def time(self, timezone=False):
        """
        Get the current time in the format HH:MM AM/PM
        :param timezone: boolean: Include the timezone at the end of the response
        :return: str
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

    def how_long_ago(self, epoch):
        """
        Get the difference from the provided epoch to now in days or years
        :param epoch: The Unix timestamp to subtract from
        :return: str
        """
        # Is the module enabled?
        if not self.enabled:
            return

        now_epoch = self.now.timestamp()
        epoch     = int(epoch)

        # Is our provided epoch in the future?
        if epoch > now_epoch:
            return "0 days"

        difference_epoch = now_epoch - epoch

        # Not a full day?
        if difference_epoch < 86400:
            return "0 days"

        # How many days ago?
        difference_days = difference_epoch / 86400

        # Was this more than a year (365 days) ago, and if so, how many years is it?
        if difference_days >= 365:
            difference_years = difference_days / 365
            difference = int(difference_years)

            # Singular or plural?
            if difference == 1:
                difference = "1 year"
            else:
                difference = str(difference) + " years"
        else:
            difference = int(difference_days)

            # Singular or plural?
            if difference == 1:
                difference = "1 day"
            else:
                difference = str(difference) + " days"

        return difference