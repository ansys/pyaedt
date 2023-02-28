import os

from setuptools import setup
import sys
import pip
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger()


from _setup_common import (
    name,
    version,
    author,
    maintainer,
    maintainer_email,
    description,
    long_description,
    packages,
    data_files,
    license,
    classifiers,
    project_urls,
)

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

if sys.version_info > (3, 7):
    install_requires = [
        "cffi == 1.15.0;platform_system=='Linux'",
        "pywin32 >= 301;platform_system=='Windows'",
        "pythonnet == 3.0.1",
        "rpyc==5.3.0",
        "pyvista>=0.34.1",
        "numpy==1.24.2",
        "matplotlib==3.7.0",
        "psutil",
        "pandas==1.5.3",
        "dotnetcore2 ==3.1.23;platform_system=='Linux'",
    ]
elif sys.version_info == (3, 7):
    install_requires = [
        "cffi == 1.15.0;platform_system=='Linux'",
        "pywin32 >= 301;platform_system=='Windows'",
        "pythonnet == 3.0.1",
        "rpyc==5.3.0",
        "pyvista>=0.34.1",
        "numpy==1.21.6",
        "matplotlib==3.5.3",
        "psutil",
        "pandas==1.3.5",
        "scikit-rf",
        "dotnetcore2 ==3.1.23;platform_system=='Linux'",
    ]
elif is_ironpython:
    install_requires = []
    extras_require = []
else:
    sys.exit("PyAEDT supports only CPython 3.7-3.10 and IronPython 2.7.")

setup(
    name=name,
    version=version,
    author=author,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=install_requires,
    extras_require={"full":extras_require},
    packages=packages,
    data_files=data_files,
    include_package_data=True,
    license=license,
    classifiers=classifiers,
    project_urls=project_urls,
)

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
