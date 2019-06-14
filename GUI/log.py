import sys
from datetime import datetime

startTime = datetime.now()

"""Escape sequences used to color output"""
ENDC = '\033[0m'
COLOUR_RED = '\033[0;31m'
COLOUR_GREEN = '\033[0;32m'
COLOUR_YELLOW = '\033[0;33m'
COLOUR_BLUE = '\033[0;34m'
COLOUR_CYAN = '\033[2;96m'


def logInfo(*args):
    """Syntax the same as for builtin print() command"""
    print(COLOUR_BLUE + "[{0:06f}|".format((datetime.now() - startTime).total_seconds())
          + COLOUR_CYAN + '{:^10s}'.format(sys._getframe(1).f_code.co_name[:10]) + COLOUR_BLUE + ']'
          + COLOUR_GREEN + '[+]' + ENDC, " ".join(map(str, args)))


def logError(*args):
    """Syntax the same as for builtin print() command"""
    print(COLOUR_BLUE + "[{0:06f}|".format((datetime.now() - startTime).total_seconds())
          + COLOUR_CYAN + '{:^10s}'.format(sys._getframe(1).f_code.co_name[:10]) + COLOUR_BLUE + ']'
          + COLOUR_RED + '[!!!]' + ENDC, " ".join(map(str, args)))
