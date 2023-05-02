import imp
from importlib import import_module
import os
import sys

from pyaedt import pyaedt_logger as logger

EMIT_API_PYTHON = None

delcross_python_path = os.environ.get("ANSYS_DELCROSS_PYTHON_PATH")
if delcross_python_path:
    sys.path.append(delcross_python_path)


def emit_api_python():
    """
    Get the Emit backend API.

    """
    return EMIT_API_PYTHON


# need this as a function so that it can be set
# for the correct aedt version that the user is running
def _set_api(aedt_version):
    numeric_version = int(aedt_version[-3:])
    desktop_path = os.environ.get(aedt_version)
    if desktop_path and numeric_version > 231:
        path = os.path.join(desktop_path, "Delcross")
        sys.path.insert(0, path)
        module_path = imp.find_module("EmitApiPython")[1]
        logger.info("Importing EmitApiPython from: {}".format(module_path))
        global EMIT_API_PYTHON
        EMIT_API_PYTHON = import_module("EmitApiPython")
        logger.info("Loaded {}".format(EMIT_API_PYTHON.EmitApi().get_version(True)))
