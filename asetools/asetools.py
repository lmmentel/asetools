
'''asetools package'''

import os
import sys

def which(prog):
    '''
    Python equivalent of the unix which command, returns the absolute path of
    the "prog" if it is found on the system PATH.
    '''

    if sys.platform == "win32" and os.path.splitext(prog)[1].lower() != '.exe':
        prog += '.exe'
    for path in os.getenv('PATH').split(os.path.pathsep):
        fprog = os.path.join(path, prog)
        if os.path.exists(fprog) and os.access(fprog, os.X_OK):
            return fprog

def get_template(tname=None):
    '''
    Return the contents of the tempalte file "tname" if it can be fousn in the
    templates path, otherwise raise an error.
    '''

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")
    tempfilepath = os.path.join(path, tname)

    if tname is None:
        raise ValueError("File name not specified")

    if os.path.exists(tempfilepath):
        with open(tempfilepath) as tfile:
            contents = tfile.read()
        return contents
    else:
        raise IOError("File: '{f:s}' not found in {p:s}".format(f=tname, p=path))
