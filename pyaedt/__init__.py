# -*- coding: utf-8 -*-
import os
import sys
import warnings

os.environ["ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE"] = "1"
os.environ["ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE"] = "1"
__version__ = ""
if os.path.exists(os.path.join(os.path.dirname(__file__), "version.txt")):
    with open(os.path.join(os.path.dirname(__file__), "version.txt"), "r") as f:
        __version__ = f.read().strip()
if os.name == "posix" and "IronPython" not in sys.version and ".NETFramework" not in sys.version:
    try:
        # from clr_loader import get_coreclr
        from pythonnet import load
        from distutils.sysconfig import get_python_lib

        site_package = get_python_lib()
        os.path.dirname(__file__)
        runtime = os.path.join(site_package, "dotnetcore2", "bin")
        print(runtime)
        json_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "misc", "pyaedt.runtimeconfig.json"))
        # rt = get_coreclr(json_file, runtime)
        # set_runtime(rt)
        load("coreclr", runtime_config=json_file, dotnet_root=runtime)
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
