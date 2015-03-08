import re
from voluptuous import Invalid

__author__     = "Makoto Fujikawa"
__copyright__  = "Copyright 2015, Makoto Fujikawa"
__version__    = "1.0.0"
__maintainer__ = "Makoto Fujikawa"


# noinspection PyPep8Naming
def Email(msg=None):
    """
    Validate whether or not the input contains a valid e-mail address
    """
    def validate(msg=None):
        msg = str(msg)
        if re.match("[\w\.\-_\+]*@[\w\.\-_\+]*\.\w+", msg):
            return msg
        else:
            raise Invalid(msg or "Incorrect email address")
    return validate