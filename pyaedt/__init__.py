# -*- coding: utf-8 -*-
import os
import sys
import warnings
from distutils.sysconfig import get_python_lib

os.environ["ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE"] = "1"
os.environ["ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE"] = "1"
pyaedt_path = os.path.dirname(__file__)
__version__ = ""
if os.path.exists(os.path.join(pyaedt_path, "version.txt")):
    with open(os.path.join(pyaedt_path, "version.txt"), "r") as f:
        __version__ = f.read().strip()
if os.name == "posix" and "IronPython" not in sys.version and ".NETFramework" not in sys.version:  # pragma: no cover
    try:
        import dotnetcore2

        runtime = os.path.join(os.path.dirname(dotnetcore2.__file__), "bin")
        os.environ["DOTNET_ROOT"] = runtime
        from pythonnet import load

        json_file = os.path.abspath(os.path.join(pyaedt_path, "misc", "pyaedt.runtimeconfig.json"))
        load("coreclr", runtime_config=json_file, dotnet_root=runtime)
        print("DotNet Core correctly loaded.")
        if "Delcross" not in os.getenv("LD_LIBRARY_PATH", "") or "mono" not in os.getenv("LD_LIBRARY_PATH", ""):
            warnings.warn("LD_LIBRARY_PATH needs to be setup to use pyaedt.")
            warnings.warn("export ANSYSEM_ROOT222=/path/to/AnsysEM/v222/Linux64")
            msg = "export LD_LIBRARY_PATH="
            msg += "$ANSYSEM_ROOT222/common/mono/Linux64/lib64:$ANSYSEM_ROOT222/Delcross:$LD_LIBRARY_PATH"
            warnings.warn(msg)
    except ImportError:
        msg = "pythonnet or dotnetcore not installed. Pyaedt will work only in client mode."
        warnings.warn(msg)

from pyaedt.generic import constants
from pyaedt.generic.general_methods import _pythonver
from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import convert_remote_object
from pyaedt.generic.general_methods import generate_unique_folder_name
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import generate_unique_project_name
from pyaedt.generic.general_methods import inside_desktop
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.general_methods import settings

from pyaedt.aedt_logger import AedtLogger  # isort:skip

try:
    from pyaedt.generic.design_types import Hfss3dLayout
except:
    from pyaedt.generic.design_types import Hfss3dLayout

from pyaedt.generic.design_types import Circuit
from pyaedt.generic.design_types import Desktop
from pyaedt.generic.design_types import Edb
from pyaedt.generic.design_types import Emit
from pyaedt.generic.design_types import Hfss
from pyaedt.generic.design_types import Icepak
from pyaedt.generic.design_types import Maxwell2d
from pyaedt.generic.design_types import Maxwell3d
from pyaedt.generic.design_types import MaxwellCircuit
from pyaedt.generic.design_types import Mechanical
from pyaedt.generic.design_types import Q2d
from pyaedt.generic.design_types import Q3d
from pyaedt.generic.design_types import Rmxprt
from pyaedt.generic.design_types import Simplorer
from pyaedt.generic.design_types import Siwave
from pyaedt.generic.design_types import TwinBuilder
from pyaedt.generic.design_types import get_pyaedt_app
