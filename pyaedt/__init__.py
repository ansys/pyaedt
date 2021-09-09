import os

# Import exception handling here due to:
# https://github.com/pyansys/PyAEDT/pull/243
import sys

is_ironpython = "IronPython" in sys.version or ".NETFramework" in sys.version
_pythonver = sys.version_info[0]
try:
    import ScriptEnv

    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
    inside_desktop = True
except:
    inside_desktop = False

try:
    from .generic.general_methods import aedt_exception_handler, generate_unique_name, retry_ntimes
    from .hfss3dlayout import Hfss3dLayout
    from .hfss import Hfss
    from .circuit import Circuit
    from .q3d import Q2d, Q3d
    from .siwave import Siwave
    from .icepak import Icepak
    from .edb import Edb
    from .maxwell import Maxwell2d, Maxwell3d
    from .mechanical import Mechanical
    from .rmxprt import Rmxprt
    from .simplorer import Simplorer
    from .desktop import Desktop
    from .emit import Emit
except:
    from .generic.general_methods import aedt_exception_handler, generate_unique_name, retry_ntimes
    from .hfss3dlayout import Hfss3dLayout
    from .hfss import Hfss
    from .circuit import Circuit
    from .q3d import Q2d, Q3d
    from .siwave import Siwave
    from .icepak import Icepak
    from .edb import Edb
    from .maxwell import Maxwell2d, Maxwell3d
    from .mechanical import Mechanical
    from .rmxprt import Rmxprt
    from .simplorer import Simplorer
    from .desktop import Desktop
    from .emit import Emit
