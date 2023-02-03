import os
import sys
from importlib import import_module

delcross_python_path = os.environ.get("ANSYS_DELCROSS_PYTHON_PATH")
if delcross_python_path:
    sys.path.append(delcross_python_path)
desktop_path = os.environ.get("ANSYSEM_ROOT232")
path = os.path.join(desktop_path, "Delcross")
sys.path.append(path)

EMIT_MODULE = import_module("EmitApiPython")

