# -*- coding: utf-8 -*-
import os
import sys
import warnings

os.environ["ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE"] = "1"
os.environ["ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE"] = "1"
pyaedt_path = os.path.dirname(__file__)
__version__ = ""
if os.path.exists(os.path.join(pyaedt_path, "version.txt")):
    with open(os.path.join(pyaedt_path, "version.txt"), "r") as f:
        __version__ = f.read().strip()
if os.name == "posix" and "IronPython" not in sys.version and ".NETFramework" not in sys.version:  # pragma: no cover
    try:
        from pythonnet import load
        from distutils.sysconfig import get_python_lib

        site_package = get_python_lib()
        runtime = os.path.join(site_package, "dotnetcore2", "bin")
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
        pass

from pyaedt.generic.general_methods import settings

from pyaedt.generic import constants
from pyaedt.generic.general_methods import pyaedt_function_handler, generate_unique_name, _retry_ntimes
from pyaedt.generic.general_methods import is_ironpython, _pythonver, inside_desktop, convert_remote_object
from pyaedt.aedt_logger import AedtLogger

try:
    from pyaedt.generic.design_types import Hfss3dLayout
except:
    from pyaedt.generic.design_types import Hfss3dLayout

from pyaedt.generic.design_types import (
    Hfss,
    Circuit,
    Q2d,
    Q3d,
    Siwave,
    Icepak,
    Edb,
    Maxwell3d,
    Maxwell2d,
    MaxwellCircuit,
    Mechanical,
    Rmxprt,
    TwinBuilder,
    Simplorer,
    Emit,
    get_pyaedt_app,
    Desktop,
)
