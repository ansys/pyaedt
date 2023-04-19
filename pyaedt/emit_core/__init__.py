from importlib import import_module
import os
import sys

EMIT_MODULE = None

delcross_python_path = os.environ.get("ANSYS_DELCROSS_PYTHON_PATH")
if delcross_python_path:
    sys.path.append(delcross_python_path)
desktop_path = os.environ.get("ANSYSEM_ROOT241")
if not desktop_path:
    desktop_path = os.environ.get("ANSYSEM_ROOT232")
desktop_path = os.environ.get("ANSYSEM_ROOT232")
if desktop_path:
    path = os.path.join(desktop_path, "Delcross")
    sys.path.append(path)
    if sys.version_info < (3, 8):
        EMIT_MODULE = import_module("EmitApiPython")
    elif sys.version_info < (3, 9):
        EMIT_MODULE = import_module("EmitApiPython38")
    elif sys.version_info < (3, 10):
        EMIT_MODULE = import_module("EmitApiPython39")
    elif sys.version_info < (3, 11):
        EMIT_MODULE = import_module("EmitApiPython310")
    elif sys.version_info < (3, 12):
        EMIT_MODULE = import_module("EmitApiPython311")
