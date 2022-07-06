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


if sys.version_info >= (3, 7):
    install_requires = [
        "pywin32 >= 303;platform_system=='Windows'",
        "pythonnet == 3.0.0rc2",
        "jupyterlab",
        "rpyc==5.0.1",
        "pyvista>=0.34.1",
        "numpy",
        "ipython",
        "matplotlib",
        "psutil",
        "dotnetcore2 ==3.1.23;platform_system=='Linux'",
    ]
elif is_ironpython:
    install_requires = []
else:
    sys.exit("Pyaedt supports only CPython 3.7-3.10 and Ironpython 2.7")


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
