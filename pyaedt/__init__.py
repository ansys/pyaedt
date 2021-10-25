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
    from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name, retry_ntimes
    from pyaedt.hfss3dlayout import Hfss3dLayout
    from pyaedt.hfss import Hfss
    from pyaedt.circuit import Circuit
    from pyaedt.q3d import Q2d, Q3d
    from pyaedt.siwave import Siwave
    from pyaedt.icepak import Icepak
    from pyaedt.edb import Edb
    from pyaedt.maxwell import Maxwell2d, Maxwell3d
    from pyaedt.mechanical import Mechanical
    from pyaedt.rmxprt import Rmxprt
    from pyaedt.simplorer import Simplorer
    from pyaedt.desktop import Desktop
    from pyaedt.emit import Emit
    from pyaedt.aedt_logger import AedtLogger
except:
    from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name, retry_ntimes
    from pyaedt.hfss3dlayout import Hfss3dLayout
    from pyaedt.hfss import Hfss
    from pyaedt.circuit import Circuit
    from pyaedt.q3d import Q2d, Q3d
    from pyaedt.siwave import Siwave
    from pyaedt.icepak import Icepak
    from pyaedt.edb import Edb
    from pyaedt.maxwell import Maxwell2d, Maxwell3d
    from pyaedt.mechanical import Mechanical
    from pyaedt.rmxprt import Rmxprt
    from pyaedt.simplorer import Simplorer
    from pyaedt.desktop import Desktop
    from pyaedt.emit import Emit
    from pyaedt.aedt_logger import AedtLogger

