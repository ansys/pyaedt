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

import importlib.util
from pathlib import Path
import sys

from ansys.aedt.core.generic.general_methods import is_windows


def load_native_module(module_name: str, base_dir: Path | str) -> object:
    """
    Dynamically load a compiled native Python module (.pyd or .so) from a base directory.
    Automatically choose the correct file extension based on the platform and Python version.

    The module name must end with '_lib' or '_dynload'.

    Example:
        module_name='nastran_import_lib' on Python 3.11 → loads 'nastran_import_lib_311.so' on Linux

    Parameters
    ----------
        module_name: str
            The name of the module to load (e.g. 'nastran_import').

        base_dir: Path, str
            Path to the directory containing the compiled module.

    Returns
    -------
        The loaded module object.

    Raises
    ------
        FileNotFoundError: If the compiled module file is not found.
        ImportError: If the module cannot be imported.
    """
    base_path = Path(base_dir)

    # Validate the module name
    if not module_name.endswith(("_lib", "_dynload")):
        raise ValueError("Module name must end with '_lib' or '_dynload'.")

    # Get Python version as suffix (e.g., '311' for Python 3.11)
    version_suffix = f"{sys.version_info.major}{sys.version_info.minor}"

    if version_suffix not in ["310", "311", "312", "313"]:
        raise ValueError(
            f"Unsupported Python version for {module_name}: {sys.version_info.major}.{sys.version_info.minor} \n"
            f"Supported versions are 3.10, 3.11, 3.12, and 3.13."
        )

    # Determine the platform-specific extension
    ext = ".pyd" if is_windows else ".so"

    # Construct the full module path
    file_name = f"{module_name}_{version_suffix}{ext}"
    module_path = base_path / file_name

    if not module_path.is_file():
        raise FileNotFoundError(f"Module file not found at: {module_path}")

    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to create import spec for {module_path}")

    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)

    return mod
