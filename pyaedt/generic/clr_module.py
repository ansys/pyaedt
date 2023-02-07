import os
import pkgutil
import sys
import warnings

modules = [tup[1] for tup in pkgutil.iter_modules()]
pyaedt_path = os.path.dirname(os.path.dirname(__file__))
cpython = "IronPython" not in sys.version and ".NETFramework" not in sys.version
if os.name == "posix" and cpython:  # pragma: no cover
    try:
        if os.environ.get("DOTNET_ROOT") is None:
            try:
                import dotnet

                runtime = os.path.join(os.path.dirname(dotnet.__path__))
            except:
                import dotnetcore2

                runtime = os.path.join(os.path.dirname(dotnetcore2.__file__), "bin")
            finally:
                os.environ["DOTNET_ROOT"] = runtime

        from pythonnet import load

        json_file = os.path.abspath(os.path.join(pyaedt_path, "misc", "pyaedt.runtimeconfig.json"))
        load("coreclr", runtime_config=json_file, dotnet_root=os.environ["DOTNET_ROOT"])
        print("DotNet Core correctly loaded.")
        if "Delcross" not in os.getenv("LD_LIBRARY_PATH", "") or "mono" not in os.getenv("LD_LIBRARY_PATH", ""):
            warnings.warn("LD_LIBRARY_PATH needs to be setup to use pyaedt.")
            warnings.warn("export ANSYSEM_ROOT222=/path/to/AnsysEM/v222/Linux64")
            msg = "export LD_LIBRARY_PATH="
            msg += "$ANSYSEM_ROOT222/common/mono/Linux64/lib64:$ANSYSEM_ROOT222/Delcross:$LD_LIBRARY_PATH"
            warnings.warn(msg)
    except ImportError:
        msg = "pythonnet or dotnetcore not installed. Pyaedt will work only in client mode."
        warnings.warn(msg)


try:  # work around a number formatting bug in the EDB API for non-English locales
    # described in #1980
    import clr as _clr
    from System.Globalization import CultureInfo as _CultureInfo

    _CultureInfo.DefaultThreadCurrentCulture = _CultureInfo.InvariantCulture
    from System import Array
    from System import Convert
    from System import Double
    from System import String
    from System import Tuple
    from System.Collections.Generic import Dictionary
    from System.Collections.Generic import List

    edb_initialized = True

except ImportError:  # pragma: no cover
    if os.name != "posix":
        warnings.warn(
            "The clr is missing. Install PythonNET or use an IronPython version if you want to use the EDB module."
        )
        edb_initialized = False
    elif sys.version[0] == 3 and sys.version[1] < 7:
        warnings.warn("EDB requires Linux Python 3.7 or later.")
    _clr = None
    String = None
    Double = None
    Convert = None
    List = None
    Tuple = None
    Dictionary = None
    Array = None
    edb_initialized = False
if "win32com" in modules:
    try:
        import win32com.client as win32_client
    except ImportError:
        try:
            import win32com.client as win32_client
        except ImportError:
            win32_client = None
