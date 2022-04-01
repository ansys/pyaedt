import setuptools
import sys
import pip
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
)

is_ironpython = "IronPython" in sys.version or ".NETFramework" in sys.version


def install(package):
    if hasattr(pip, "main"):
        pip.main(["install", package])
    else:
        pip._internal.main(["install", package])


if sys.version_info >= (3, 9):
    install_requires = [
        "jupyterlab;platform_system=='Linux'",
        "pywin32 >= 303;platform_system=='Windows'",
        "rpyc==5.0.1",
        "pyvista<=0.33.3",
        "numpy",
        "ipython",
        "matplotlib",
    ]
    install("https://github.com/pyansys/PyAEDT/raw/release/0.3/pythonnet-2.5.2-cp39-cp39-win_amd64.whl")
elif sys.version_info >= (3, 0):
    install_requires = [
        "pywin32 >= 303;platform_system=='Windows'",
        "pythonnet >= 2.5.2;platform_system=='Windows'",
        "jupyterlab;platform_system=='Linux'",
        "rpyc==5.0.1",
        "pyvista<=0.33.3",
        "numpy",
        "ipython",
        "matplotlib",
    ]
elif not is_ironpython and sys.version_info < (3, 0):
    install_requires = ["pywin32 == 228;platform_system=='Windows'", "pythonnet >= 2.5.2;platform_system=='Windows'"]
else:
    install_requires = []


setuptools.setup(
    name=name,
    version=version,
    author=author,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=install_requires,
    packages=packages,
    data_files=data_files,
    include_package_data=True,
    license=license,
    classifiers=classifiers,
)
