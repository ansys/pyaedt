from importlib import import_module
import os
import sys

from pyaedt.misc.misc import list_installed_ansysem

EMIT_MODULE = None

delcross_python_path = os.environ.get("ANSYS_DELCROSS_PYTHON_PATH")
if delcross_python_path:
    sys.path.append(delcross_python_path)

# the list is reverse sorted, so newest version is first
latest_version = list_installed_ansysem()[0]
desktop_path = os.environ.get(latest_version)
numeric_version = int(latest_version[-3:])
if desktop_path and numeric_version > 231:
    path = os.path.join(desktop_path, "Delcross")
    sys.path.append(path)
    EMIT_MODULE = import_module("EmitApiPython")
