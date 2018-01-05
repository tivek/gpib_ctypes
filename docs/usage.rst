=====
Usage
=====

To use ``gpib-ctypes`` in a project, import all submodules at once::

    import gpib_ctypes

... or import ``gpib`` and ``Gpib`` submodules separately as below.

Handle-level GPIB API::

    # Identify instrument at board 0, primary address 23.
    
    from gpib_ctypes import gpib

    try:
        dev_handle = gpib.dev(0, 23)

        gpib.write(dev_handle, b'*IDN?')
        result = gpib.read(dev_handle, 1000)

    except gpib.GpibError as err:
        # do something with err.code
        pass


Object-oriented GPIB API::

    # Identify instrument at board 0, primary address 23.
    
    from gpib_ctypes import Gpib

    try:
        dev = Gpib.Gpib(0, 23)

        dev.write(b'*IDN?')
        result = dev.read(1000)

    except gpib.GpibError as err:
        # do something with err.code
        pass

Example use with ``pyvisa`` and the pure Python backend ``pyvisa-py``::

    # pyvisa-py will try to load the root-level gpib module, eg. from the linux-gpib project.
    # To make pyvisa-py use gpib_ctypes.gpib instead, monkey patch it by calling gpib_ctypes.make_default_gpib().

    from gpib_ctypes import make_default_gpib
    make_default_gpib()
    
    import visa
    rm = visa.ResourceManager('@py')
    
    resources = rm.list_resources()
    # example result: ('GPIB0::14::INSTR', 'GPIB0::23::INSTR')
    
    dev = rm.open_resource('GPIB0::23::INSTR')
