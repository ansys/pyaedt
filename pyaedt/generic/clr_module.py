import os
import sys
import warnings

try:
    # work around a number formatting bug in the EDB API for non-English locales
    # described in #1980
    import clr as _clr
    from System.Globalization import CultureInfo as _CultureInfo

    _CultureInfo.DefaultThreadCurrentCulture = _CultureInfo.InvariantCulture
    _clr.AddReference("System.Collections")
    _clr.AddReference("System")
    from System import Array
    from System import Convert
    from System import Double
    from System import String
    from System import Tuple
    from System.Collections.Generic import Dictionary
    from System.Collections.Generic import List

    edb_initialized = True

except ImportError:  # pragma: no cover
    if os.name != "posix":
        warnings.warn(
            "The clr is missing. Install PythonNET or use an IronPython version if you want to use the EDB module."
        )
        edb_initialized = False
    elif sys.version[0] == 3 and sys.version[1] < 7:
        warnings.warn("EDB requires Linux Python 3.7 or later.")
    _clr = None
    String = None
    Double = None
    Convert = None
    List = None
    Tuple = None
    Dictionary = None
    Array = None
    edb_initialized = False
