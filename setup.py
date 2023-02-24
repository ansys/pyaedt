import os

from setuptools import setup
import sys
import pip
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger()


is_ironpython = "IronPython" in sys.version or ".NETFramework" in sys.version


def install(package):
    if hasattr(pip, "main"):
        pip.main(["install", package])
    else:
        pip._internal.main(["install", package])



extras_require = [
    "osmnx",
    "utm",
    "SRTM.py",
]

setup()

if sys.version_info > (3, 7):
    install_requires = [
        "cffi == 1.15.0;platform_system=='Linux'",
        "pywin32 >= 301;platform_system=='Windows'",
        "pythonnet == 3.0.1",
        "rpyc==5.3.0",
        "pyvista>=0.34.1",
        "numpy",
        "matplotlib",
        "psutil",
        "pandas",
        "dotnetcore2 ==3.1.23;platform_system=='Linux'",
    ]
elif sys.version_info == (3, 7):
    install_requires = [
        "cffi == 1.15.0;platform_system=='Linux'",
        "pywin32 >= 301;platform_system=='Windows'",
        "pythonnet == 3.0.1",
        "rpyc==5.3.0",
        "pyvista>=0.34.1",
        "numpy",
        "matplotlib",
        "psutil",
        "pandas==1.3.5",
        "dotnetcore2 ==3.1.23;platform_system=='Linux'",
    ]
elif is_ironpython:
    install_requires = []
    extras_require = []
else:
    sys.exit("PyAEDT supports only CPython 3.7-3.10 and IronPython 2.7.")

if os.name == "posix" and not is_ironpython:
    print("     ")
    print("     ")
    print("     ")
    print("==========================================================================================================")
    print("     ")
    print("Configure ANSYSEM_ROOT222 or later and LD_LIBRARY_PATH to use it on Linux like in the following example.")
    print("Example:")
    print("export ANSYSEM_ROOT222=/path/to/AnsysEM/v222/Linux64")
    msg = "export LD_LIBRARY_PATH="
    msg += "$ANSYSEM_ROOT222/common/mono/Linux64/lib64:$ANSYSEM_ROOT222/Delcross:$LD_LIBRARY_PATH"
    print(msg)
    print("     ")
    print("==========================================================================================================")
    print("     ")
    print("     ")
    print("     ")
