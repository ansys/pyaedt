# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from pathlib import Path
import pkgutil
import sys
import warnings

import ansys.aedt.core
from ansys.aedt.core.aedt_logger import pyaedt_logger as logger

existing_showwarning = warnings.showwarning


def custom_show_warning(message, category, filename, lineno, file=None, line=None):
    """Custom warning used to remove <stdin>:loc: pattern."""
    print(f"{category.__name__}: {message}", file=file or sys.stderr)


warnings.showwarning = custom_show_warning

modules = [tup[1] for tup in pkgutil.iter_modules()]
cpython = "IronPython" not in sys.version and ".NETFramework" not in sys.version
is_linux = os.name == "posix"
is_windows = not is_linux
is_clr = False
pyaedt_path = Path(ansys.aedt.core.__file__).parent

if is_linux and cpython:
    from pythonnet import load

    dotnet_root = None
    runtime_config = None
    runtime_spec = None
    # Use system .NET core runtime or fall back to dotnetcore2
    if os.environ.get("DOTNET_ROOT") is None:
        try:
            from clr_loader import get_coreclr

            runtime = get_coreclr()
            load(runtime)
            os.environ["DOTNET_ROOT"] = runtime.dotnet_root.as_posix()
            is_clr = True
        # TODO: Fall backing to dotnetcore2 should be removed in a near future.
        except Exception:
            warnings.warn(
                "Unable to set .NET root and locate the runtime configuration file. Falling back to using dotnetcore2."
            )
            warnings.warn(ansys.aedt.core.DOTNET_LINUX_WARNING)

            import dotnetcore2

            dotnet_root = Path(dotnetcore2.__file__).parent / "bin"
            runtime_config = pyaedt_path / "misc" / "pyaedt.runtimeconfig.json"
    # Use specified .NET root folder
    else:
        dotnet_root = Path(os.environ["DOTNET_ROOT"])
        # Patch the case where DOTNET_ROOT leads to dotnetcore2.
        # TODO: Remove once dotnetcore2 is deprecated
        if dotnet_root.parent.name == "dotnetcore2":
            runtime_config = pyaedt_path / "misc" / "pyaedt.runtimeconfig.json"
        else:
            from clr_loader import find_runtimes

            candidates = [rt for rt in find_runtimes() if rt.name == "Microsoft.NETCore.App"]
            candidates.sort(key=lambda spec: spec.version, reverse=True)
            if not candidates:
                raise RuntimeError(
                    "Configuration file could not be found from DOTNET_ROOT. "
                    "Please ensure that .NET SDK is correctly installed or "
                    "that DOTNET_ROOT is correctly set."
                )
            runtime_spec = candidates[0]
    # Use specific .NET core runtime
    if dotnet_root is not None and (runtime_config is not None or runtime_spec is not None):
        try:
            load(
                "coreclr",
                runtime_config=str(runtime_config) if runtime_config else None,
                runtime_spec=runtime_spec,
                dotnet_root=str(dotnet_root),
            )
            os.environ["DOTNET_ROOT"] = dotnet_root.as_posix()
            if "mono" not in os.getenv("LD_LIBRARY_PATH", ""):
                warnings.warn("LD_LIBRARY_PATH needs to be setup to use pyaedt.")
                warnings.warn("export ANSYSEM_ROOT252=/path/to/AnsysEM/v251/Linux64")
                msg = "export LD_LIBRARY_PATH="
                msg += "$ANSYSEM_ROOT252/common/mono/Linux64/lib64:$LD_LIBRARY_PATH"
                warnings.warn(msg)
            is_clr = True
        except ImportError:
            msg = "pythonnet or dotnetcore not installed. PyAEDT will work only in client mode."
            warnings.warn(msg)
else:
    try:
        from pythonnet import load

        load("coreclr")
        is_clr = True

    except Exception:
        logger.error("An error occurred while loading clr.")

# Work around a number formatting bug in the EDB API for non-English locales, see #1980
try:
    import clr as _clr  # isort:skip
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
    if is_windows:
        warnings.warn("The clr is missing.")
        edb_initialized = False
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

warnings.showwarning = existing_showwarning
