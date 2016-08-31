# -*- coding: utf-8 -*-

'useful tools'


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
