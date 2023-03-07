import os

from setuptools import setup
import fnmatch
import sys
# import pip
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger()

is_ironpython = "IronPython" in sys.version or ".NETFramework" in sys.version


# def install(package):
#     if hasattr(pip, "main"):
#         pip.main(["install", package])
#     else:
#         pip._internal.main(["install", package])


# required since Python 2.7's glob.iglob does not support recursive keyword
def recursive_glob(startpath, filepattern):
    """Return a list of files matching a pattern, searching recursively from a start path.
    Keyword Arguments:
    startpath -- starting path (directory)
    filepattern -- fnmatch-style filename pattern
    """
    return [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(startpath)
        for filename in filenames
        if fnmatch.fnmatch(filename, filepattern)
    ]

def recursive_glob_folder(startpath, exclude_list=["dlls", "__pycache__",]):
    """Return a list of files matching a pattern, searching recursively from a start path.
    Keyword Arguments:
    startpath -- starting path (directory)
    """
    list_in =  [
        dirpath.replace(startpath, "pyaedt").replace("\\", ".")
        for dirpath, _, filenames in os.walk(startpath)
    ]
    list_excl = [el for i in exclude_list for el in list_in  if i in el]
    return [i for i in list_in if i not in list_excl]


open3 = open
if sys.version_info < (3, 0):
    import io
    open3 = io.open

# loosely from https://packaging.python.org/guides/single-sourcing-package-version/
HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "pyaedt", "version.txt"), "r") as f:
    version = f.readline()

# Get the long description from the README file
with open3(os.path.join(HERE, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

packages = recursive_glob_folder(os.path.join(HERE, "pyaedt"))

data_files = [
    ("dlls", recursive_glob(os.path.join("pyaedt", "dlls"), "*")),
    ("misc", recursive_glob(os.path.join("pyaedt", "misc"), "*")),
    ("License", recursive_glob(".", "*.md")),
    ("xaml", ["pyaedt/generic/wpf_template.xaml"]),
    ("version", ["pyaedt/version.txt"]),
    ("setup-distutils", ["setup-distutils.py"]),
]


extras_require = [
    "osmnx",
    "utm",
    "SRTM.py",
]

# if sys.version_info.major == 3 and sys.version_info.minor > 7:
#     install_requires = [
#         "cffi>=1.15.0;platform_system=='Linux'",
#         "pywin32>=301;platform_system=='Windows'",
#         "pythonnet>=3.0.1",
#         "rpyc>=5.3.0",
#         "pyvista>=0.34.1",
#         "numpy>=1.24.2",
#         "matplotlib>=3.7.0",
#         "psutil",
#         "pandas>=1.5.3",
#         "scikit-rf",
#         "dotnetcore2>=3.1.23;platform_system=='Linux'",
#     ]
# elif sys.version_info.major == 3 and sys.version_info.minor == 7:
#     install_requires = [
#         "cffi>=1.15.0;platform_system=='Linux'",
#         "pywin32>=301;platform_system=='Windows'",
#         "pythonnet==3.0.1",
#         "rpyc>=5.3.0",
#         "pyvista>=0.34.1",
#         "numpy<=1.21.6",
#         "matplotlib<=3.5.3",
#         "psutil",
#         "pandas<=1.3.5",
#         "scikit-rf",
#         "dotnetcore2==3.1.23;platform_system=='Linux'",
#     ]

if is_ironpython:
    install_requires = []
    extras_require = []
# else:
#     sys.exit("PyAEDT supports only CPython 3.7-3.10 and IronPython 2.7.")

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

if __name__ == '__main__':
    setup(version=version,
    data_files=data_files,
    include_package_data=True,
    packages=packages)
