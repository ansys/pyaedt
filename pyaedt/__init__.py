# -*- coding: utf-8 -*-
import os
import sys

os.environ["ANSYSEM_FEATURE_SF6694_NON_GRAPHICAL_COMMAND_EXECUTION_ENABLE"] = "1"
os.environ["ANSYSEM_FEATURE_SF159726_SCRIPTOBJECT_ENABLE"] = "1"
__version__ = ""
if os.path.exists(os.path.join(os.path.dirname(__file__), "version.txt")):
    with open(os.path.join(os.path.dirname(__file__), "version.txt"), "r") as f:
        __version__ = f.read().strip()
if os.name == "posix" and "IronPython" not in sys.version and ".NETFramework" not in sys.version:
    try:
        base_path = ""
        if os.getenv("ANSYSEM_ROOT231", ""):
            base_path = os.environ["ANSYSEM_ROOT231"]
        elif os.getenv("ANSYSEM_ROOT222", ""):
            base_path = os.environ["ANSYSEM_ROOT222"]
        elif os.getenv("ANSYSEM_ROOT221", ""):
            base_path = os.environ["ANSYSEM_ROOT221"]
        if base_path:
            pkg_dir = os.path.join(base_path, "common", "mono", "Linux64")
            if os.getenv("LD_LIBRARY_PATH", None):
                os.environ["LD_LIBRARY_PATH"] = (
                    os.path.join(pkg_dir, "lib64")
                    + os.pathsep
                    + os.path.join(pkg_dir, "lib")
                    + os.pathsep
                    + os.environ["LD_LIBRARY_PATH"]
                )
            else:
                os.environ["LD_LIBRARY_PATH"] = (
                    os.path.join(pkg_dir, "lib64") + os.pathsep + os.path.join(pkg_dir, "lib")
                )
        print(os.environ["LD_LIBRARY_PATH"])
        from clr_loader import get_coreclr
        from pythonnet import set_runtime

        os.path.dirname(__file__)
        runtime = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dotnetcore2", "bin"))
        json_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "misc", "pyaedt.runtimeconfig.json"))
        rt = get_coreclr(json_file, runtime)
        set_runtime(rt)
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
