# -*- coding: utf-8 -*-

import ctypes
import os
import sys
import platform

from .constants import *

# load the GPIB dynamic library using ctypes
_lib = None


def _load_lib(filename=None):
    """Attempt to load the GPIB library from the given filename.
    If filename is ommitted, try several likely paths.

    Args:
        filename (str): path to GPIB library, default None

    Returns:
        bool: library found and loaded
    """

    global _lib
    _lib = None

    if platform.system() == "Windows":
        libnames = [filename] if filename else \
                   ['gpib-32.dll',
                    'c:\\windows\\system32\\gpib-32.dll',
                    'c:\\windows\\system\\gpib-32.dll',
                    'c:\\gpib\\gpib-32.dll',
                    'gpib-32.so', 'libgpib.so.0']
        loader = ctypes.windll.LoadLibrary
    else:
        # most likely Linux with linux-gpib
        libnames = [filename] if filename else ['libgpib.so.0', 'gpib-32.so']
        loader = ctypes.cdll.LoadLibrary

    for libname in libnames:
        try:
            _lib = loader(libname)
            break
        except OSError:
            continue

    if not _lib:
        # Warn the user but still load the module.
        # This is necessary for eg. docs generators to work without having
        # GPIB installed.
        import warnings
        message = "GPIB library not found. Please manually load it using _load_lib(filename). All GPIB functions will raise OSError until the library is manually loaded."
        warnings.warn(message)

        class MockGPIB(object):
            def __getattr__(self, n):
                def f(*args):
                    raise OSError(message)
                return f

        _lib = MockGPIB()
        return False

    # prepare ctypes bindings
    for name, argtypes, restype in (
        ("ibask", [ctypes.c_int, ctypes.c_int,
                   ctypes.POINTER(ctypes.c_int)], ctypes.c_int),
        ("ibclr", [ctypes.c_int], ctypes.c_int),
        ("ibcmd", [ctypes.c_int, ctypes.c_char_p, ctypes.c_long], ctypes.c_int),
        ("ibconfig", [ctypes.c_int, ctypes.c_int, ctypes.c_int], ctypes.c_int),
        ("ibdev", [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                   ctypes.c_int, ctypes.c_int, ctypes.c_int], ctypes.c_int),
        ("ibln", [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                  ctypes.POINTER(ctypes.c_short)], ctypes.c_int),
        ("ibloc", [ctypes.c_int], ctypes.c_int),
        ("ibonl", [ctypes.c_int, ctypes.c_int], ctypes.c_int),
        ("ibrd", [ctypes.c_int, ctypes.c_char_p, ctypes.c_long], ctypes.c_int),
        ("ibrsp", [ctypes.c_int, ctypes.c_char_p], ctypes.c_int),
        ("ibsic", [ctypes.c_int], ctypes.c_int),
        ("ibsre", [ctypes.c_int, ctypes.c_int], ctypes.c_int),
        ("ibtmo", [ctypes.c_int, ctypes.c_int], ctypes.c_int),
        ("ibtrg", [ctypes.c_int], ctypes.c_int),
        ("ibwait", [ctypes.c_int, ctypes.c_int], ctypes.c_int),
        ("ibwrta", [ctypes.c_int, ctypes.c_char_p,
                    ctypes.c_long], ctypes.c_int),
        ("ibwrt", [ctypes.c_int, ctypes.c_char_p, ctypes.c_long], ctypes.c_int),
        ("iblines", [ctypes.c_int, ctypes.POINTER(
            ctypes.c_short)], ctypes.c_int)
    ):
        libfunction = _lib[name]
        libfunction.argtypes = argtypes
        libfunction.restype = restype

    # implementation-specific special cases
    try:
        _old_ibfind = _lib.ibfind
        _old_ibfind.argtypes = [ctypes.c_char_p]
        _old_ibfind.restype = ctypes.c_int
        setattr(_lib, "ibfind", lambda name: _old_ibfind(name.encode('ascii')))
    except AttributeError:
        # Windows Unicode version ibfindW
        _lib.ibfindW.argtypes = [ctypes.c_wchar_p]
        _lib.ibfindW.restype = ctypes.c_int
        setattr(_lib, "ibfind", _lib.ibfindW)

    try:
        _lib.ibspb.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_short)]
        _lib.ibspb.restype = ctypes.c_int
    except AttributeError:
        # some Windows GPIB libraries do not provide ibsp
        # but maybe it is not needed, so gently warn the user it is missing
        import warnings
        message = "{:s} does not implement ibspb() on this platform.".format(
            _lib._name)
        warnings.warn(message, ImportWarning)

        def _ibspb(*args):
            raise NotImplementedError(message)
        setattr(_lib, "ibspb", _ibspb)

    try:
        _lib.ThreadIbsta.restype = ctypes.c_int
        setattr(_lib, "getibsta", _lib.ThreadIbsta)
    except AttributeError:
        setattr(_lib, "getibsta", lambda: ctypes.c_int.in_dll(_lib, "ibsta"))

    try:
        _lib.ThreadIbcntl.restype = ctypes.c_long
        setattr(_lib, "getibcntl", _lib.ThreadIbcntl)
    except AttributeError:
        setattr(_lib, "getibcntl", lambda: ctypes.c_long.in_dll(_lib, "ibcntl"))

    try:
        _lib.ThreadIberr.restype = ctypes.c_int
        setattr(_lib, "getiberr", _lib.ThreadIberr)
    except AttributeError:
        setattr(_lib, "getiberr", lambda: ctypes.c_int.in_dll(_lib, "iberr"))

    return True


_load_lib()


class GpibError(Exception):
    """Exception class with helpful GPIB error messages
       GpibError(gpib_function_name)
    """

    _explanation = {
        EDVR: "system error",
        ECIC: "not CIC",
        ENOL: "no listener",
        EADR: "CIC and not addressed before IO",
        EARG: "bad argument to function call",
        ESAC: "not SAC",
        EABO: "IO aborted",
        ENEB: "GPIB board offline",
        EDMA: "DMA hardware error",
        EOIP: "previous IO still in progress",
        ECAP: "not capable",
        EFSO: "file system operation error",
        EBUS: "bus error",
        ESTB: "lost serial poll bytes",
        ESRQ: "SRQ stuck on",
        ETAB: "table overflow",
        ELCK: "interface locked",
        EARM: "failed to rearm",
        EHDL: "invalid handle",
        EWIP: "previous wait still in progress",
        ERST: "event notification cancelled due to reset",
        EPWR: "interface lost power"
    }

    def __init__(self, funcname):
        self.code = _lib.getiberr()
        self.sverrno = None

        if self.code in (EDVR, EFSO):
            self.sverrno = ibcnt()
            message = "{:s}() error: Errno {:d}, {:s}".format(
                funcname, self.sverrno, os.strerror(self.sverrno))
        else:
            try:
                expl = GpibError._explanation[self.code]
            except KeyError:
                expl = "unknown error"
            message = "{:s}() error: Iberr {:d}, {:s}".format(
                funcname, self.code, expl)

        super(GpibError, self).__init__(message)


def ask(handle, conf):
    """Query configuration by calling ibask.

    Args:
        handle (int): board or device handle
        conf (int): gpib.Iba* constant designating configuration settings

    Returns:
        int: configuration setting value
    """

    result = ctypes.c_int()

    sta = _lib.ibask(handle, conf, ctypes.byref(result))
    if sta & ERR:
        raise GpibError("ask")

    return result.value


def clear(handle):
    """Clear device by calling ibclr.

    Args:
        handle (int): device handle

    Returns:
        int: ibsta value
    """

    sta = _lib.ibclr(handle)
    if sta & ERR:
        raise GpibError("clear")

    return sta


def close(handle):
    """Close board or device handle by calling ibonl.

    Args:
        handle (int): board or device handle to close

    Returns:
        int: ibsta value
    """

    sta = _lib.ibonl(handle, 0)
    if sta & ERR:
        raise GpibError("close")

    return sta


def command(handle, cmd):
    """Write command bytes by calling ibcmd.

    Args:
        handle (int): board handle
        cmd (bytes): sequence of bytes to write

    Returns:
        int: ibsta value
    """

    sta = _lib.ibcmd(handle, cmd, len(cmd))
    if sta & ERR:
        raise GpibError("command")

    return sta


def config(handle, conf, value):
    """Change configuration by calling ibconfig.

    Args:
        handle (int): board or device handle
        conf (int): gpib.Ibc* constant designating configuration settings
        value (int): configuration setting value

    Returns:
        int: ibsta value
    """

    sta = _lib.ibconfig(handle, conf, value)
    if sta & ERR:
        raise GpibError("config")

    return sta


def dev(board, pad, sad=NO_SAD, tmo=T30s, sendeoi=1, eos=0):
    """Get a device handle by calling ibdev.

    Args:
        board (int): board number
        pad (int): primary address
        sad (int): secondary address, default gpib.NO_SAD
        tmo (int): timeout constant, default gpib.T30s
        sendeoi (int): assert EOI on write, default 1
        eos (int): end-of-string termination, default 0

    Returns:
        int: board or device handle
    """

    ud = _lib.ibdev(board, pad, sad, tmo, sendeoi, eos)
    if ud < 0:
        raise GpibError("dev")
    return ud


def find(name):
    """Get a device handle based on a name from configuration file
    by calling ibfind.

    Args:
        name (string)

    Returns:
        int: board or device handle
    """
    ud = _lib.ibfind(name)
    if ud < 0:
        raise GpibError("find")
    return ud


def ibcnt():
    """Get number of transferred bytes by calling ThreadIbcntl or reading ibcnt.

    Args:
        none

    Returns:
        int: number of transferred bytes
    """

    return _lib.getibcntl()


def ibloc(handle):
    """Push device to local mode by calling ibloc.

    Args:
        handle (int): device handle

    Returns:
        int: ibsta value
    """

    sta = _lib.ibloc(handle)
    if sta & ERR:
        raise GpibError("ibloc")

    return sta


def ibsta():
    """Get status value by calling ThreadIbsta or reading ibsta.

    Args:
        none

    Returns:
        int: ibsta value
    """

    return _lib.getibsta()


def interface_clear(handle):
    """Clear interface by calling ibsic.

    Args:
        handle (int): board handle

    Returns:
        int: ibsta value
    """

    sta = _lib.ibsic(handle)
    if sta & ERR:
        raise GpibError("interface_clear")

    return sta


def lines(board):
    """Obtain the status of the control and handshaking bus
    lines of the bus.

    Args:
        board (int): board handle

    Returns:
        int: line capability and status bits
    """

    result = ctypes.c_short()

    sta = _lib.iblines(board, ctypes.byref(result))
    if sta & ERR:
        raise GpibError("lines")

    return result.value


def listener(board, pad, sad=NO_SAD):
    """Check if listener is present at address by calling ibln.

    Args:
        board (int): board or device handle, or board number
        pad (int): primary address
        sad (int): secondary address, default gpib.NO_SAD

    Returns:
        bool: True if listener is present, False otherwise
    """

    present = ctypes.c_short()

    sta = _lib.ibln(board, pad, sad, ctypes.byref(present))
    if sta & ERR:
        raise GpibError("listener")

    return bool(present)


def read(handle, length):
    """Read a number of data bytes by calling ibread.

    Args:
        handle (int): board or device handle
        length (int): number of bytes to read

    Returns:
        bytes: sequence of bytes which was read
    """

    retval = ctypes.create_string_buffer(length)

    sta = _lib.ibrd(handle, retval, length)
    if sta & ERR:
        raise GpibError("read")

    return retval[:ibcnt()]


def remote_enable(handle, enable):
    """Set remote enable by calling ibsre.

    Args:
        handle (int): board handle
        enable (int): if non-zero, set remote enable

    Returns:
        int: ibsta value
    """

    sta = _lib.ibsre(handle, enable)
    if sta & ERR:
        raise GpibError("remote_enable")

    return sta


def serial_poll(handle):
    """Read status byte by calling ibrsp.

    Args:
        handle (int): device handle

    Returns:
        int: serial poll status byte
    """

    status = ctypes.c_char()

    sta = _lib.ibrsp(handle, ctypes.byref(status))
    if sta & ERR:
        raise GpibError("serial_poll")

    return int(status.value[0])


def spoll_bytes(handle):
    """Get length of status byte queue by calling ibspb.

    Args:
        handle (int): device handle

    Returns:
        int: status byte queue length
    """

    length = ctypes.c_short()

    sta = _lib.ibspb(handle, ctypes.byref(length))
    if sta & ERR:
        raise GpibError("spoll_bytes")

    return length.value


def timeout(handle, t):
    """Set IO timeout by calling ibtmo.

    Args:
        handle (int): board or device handle
        t (int): timeout, one of constants from gpib.TNONE to gpib.T100s

    Returns:
        int: ibsta value
    """

    sta = _lib.ibtmo(handle, t)
    if sta & ERR:
        raise GpibError("timeout")

    return sta


def trigger(handle):
    """Trigger device by calling ibtrg.

    Args:
        handle (int): device handle

    Returns:
        int: ibsta value
    """

    sta = _lib.ibtrg(handle)
    if sta & ERR:
        raise GpibError("trigger")

    return sta


def version():
    """Get the GPIB library version. Not implemented on Windows.  

    Args:
        none

    Returns:
        str: GPIB library version
    """

    try:
        ver = ctypes.c_char_p()
        _lib.ibvers(ctypes.byref(ver))
        return ver.value
    except AttributeError:
        return None


def wait(handle, eventmask):
    """Wait for event by calling ibwait.

    Args:
        handle (int): board or device handle
        eventmask (int): ibsta bits designating events to wait for

    Returns:
        int: ibsta value
    """

    sta = _lib.ibwait(handle, eventmask)
    if sta & ERR:
        raise GpibError("wait")

    return sta


def write(handle, data):
    """Write data bytes by calling ibwrt.

    Args:
        handle (int): board or device handle
        data (bytes): sequence of bytes to write

    Returns:
        int: ibsta value
    """

    sta = _lib.ibwrt(handle, data, len(data))
    if sta & ERR:
        raise GpibError("write")

    return sta


def write_async(handle, data):
    """Write data bytes asynchronously by calling ibwrta.

    Args:
        handle (int): board or device handle
        data (bytes): sequence of bytes to write

    Returns:
        int: ibsta value
    """

    sta = _lib.ibwrta(handle, data, len(data))
    if sta & ERR:
        raise GpibError("write_async")

    return sta
