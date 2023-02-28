from importlib import import_module
import os
import sys

EMIT_MODULE = None

delcross_python_path = os.environ.get("ANSYS_DELCROSS_PYTHON_PATH")
if delcross_python_path:
    sys.path.append(delcross_python_path)
desktop_path = os.environ.get("ANSYSEM_ROOT232")
if desktop_path and sys.version_info < (3, 8):
    path = os.path.join(desktop_path, "Delcross")
    sys.path.append(path)
    EMIT_MODULE = import_module("EmitApiPython")
