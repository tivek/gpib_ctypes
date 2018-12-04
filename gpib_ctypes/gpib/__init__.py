# -*- coding: utf-8 -*-

"""Python interface for the linux-gpib library or the NI GPIB C
library on Windows and Linux. Adheres to the linux-gpib Python API.

All functions return the value of ibsta except where otherwise specified.
"""

__author__ = """Tomislav Ivek"""
__email__ = 'tomislav.ivek@gmail.com'
__version__ = '0.1.0'

from .constants import *
from .gpib import \
    ask,\
    clear,\
    close,\
    command,\
    config,\
    dev,\
    find,\
    ibcnt,\
    ibloc,\
    ibsta,\
    interface_clear,\
    lines,\
    listener,\
    read,\
    remote_enable,\
    serial_poll,\
    spoll_bytes,\
    timeout,\
    trigger,\
    version,\
    wait,\
    write,\
    write_async,\
    GpibError,\
    _load_lib
