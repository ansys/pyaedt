from ansys.aedt.core.generic.general_methods import is_linux
import ctypes
import os
from tests.conftest import DESKTOP_VERSION

reduced_version = DESKTOP_VERSION[2:6].replace(".", "")
base_path = os.environ[f"ANSYSEM_ROOT{reduced_version}"]
if is_linux:
    ctypes.cdll.LoadLibrary(
        os.path.join(base_path, "common", "mono", "Linux64", "lib", "libmonosgen-2.0.so.1")
    )
    ctypes.cdll.LoadLibrary(os.path.join(base_path, "libEDBCWrapper.so"))