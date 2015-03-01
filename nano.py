#!/usr/bin/python

from rivescript import RiveScript
from modules.exceptions import ModuleDisabledError
import re

rs = RiveScript()
rs.load_directory("./intelligence")
rs.sort_replies()


class Handler():
    def __init__(self, name="localuser"):
        self.name = name

    def send(self, source, message, directed=False):
        # Perform some parsing on our response
        message = re.sub("\x03(?:\d{1,2}(?:,\d{1,2})?)?", "", message, 0, re.UNICODE)
        directed_pattern = re.compile("^nano(\W)?\s+", re.IGNORECASE)

        # Was this message directed at us?
        if not directed:
            directed = bool(directed_pattern.match(message))

        """
        if directed:
            message = directed_pattern.sub("", message)
        """

        rs.set_uservar(source, "directed", directed)

        # Get and return our reply
        try:
            return rs.reply(source, message)
        except IndexError:
            print("Empty set matched")
        except ModuleDisabledError:
            print("Disabled module called")


    def set_name(self, source, name):
        rs.set_uservar(source, "name", name)


"""
while True:
    msg = input("You> ")
    if msg == '/quit':
        quit()
    reply = rs.reply("localuser", msg)
    print("Bot>", reply)
"""