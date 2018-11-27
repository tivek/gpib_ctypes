# -*- coding: utf-8 -*-

"""Top-level package for gpib-ctypes."""

__author__ = """Tomislav Ivek"""
__email__ = 'tomislav.ivek@gmail.com'
__version__ = '0.1.0dev'

__all__ = ['gpib', 'Gpib', 'make_default_gpib']

import gpib_ctypes.gpib
import gpib_ctypes.Gpib


def make_default_gpib():
    """Monkeypatches gpib_ctypes.gpib and gpib_ctypes.Gpib modules to be
    used as the only gpib and Gpib modules by the running process.

    Example usage with pyvisa-py:

    from gpib_ctypes import make_default_gpib
    make_default_gpib() # call early in __main__

    import visa
    rm = visa.ResourceManager('@py') # rm now uses gpib_ctypes
    """

    import sys

    for m in ['gpib', 'Gpib']:
        try:
            del sys.modules[m]
        except KeyError:
            pass

    _temp = __import__('gpib_ctypes', fromlist=['gpib', 'Gpib'])
    sys.modules['gpib'], sys.modules['Gpib'] = _temp.gpib, _temp.Gpib
