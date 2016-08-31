
from __future__ import print_function, division, absolute_import

from builtins import (bytes, dict, int, list, object, range, str,
                      ascii, chr, hex, input, next, oct, open,
                      pow, round, super, filter, map, zip)


def sanitizestr(value, repd=None, keepchars=None):
    'Sanitize the string to get a workable filename'

    if repd is None:
        repd = {'(': '_', ')': '_', '[': '_', ']': '_', ',': '_'}
    if keepchars is None:
        keepchars = ('_', '.', '+', '-')

    rtable = str.maketrans(''.join(repd.keys()), ''.join(repd.values()))
    value = str(value).translate(rtable)

    value = "".join(c for c in value if c.isalnum() or c in keepchars).rstrip()
    return value

