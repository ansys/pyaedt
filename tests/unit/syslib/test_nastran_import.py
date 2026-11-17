# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from pathlib import Path
import shutil

from ansys.aedt.core.syslib.nastran_import import _get_nastran_import_lib
from ansys.aedt.core.syslib.nastran_import import nastran_to_stl
from tests import TESTS_GENERAL_PATH


def test_nastran_native_lib_loads() -> None:
    """The native Nastran library must be available for the running Python version."""
    lib = _get_nastran_import_lib()

    assert hasattr(lib, "nastran_to_stl")


def test_nastran_to_stl(test_tmp_dir) -> None:
    """Convert a real Nastran file to STL with the native library."""
    # test_cad.nas includes the .key files, which must sit next to it
    source_dir = TESTS_GENERAL_PATH / "example_models" / "T20"
    for name in ("test_cad.nas", "assembly1.key", "assembly2.key"):
        shutil.copy2(source_dir / name, test_tmp_dir / name)
    nas_file = test_tmp_dir / "test_cad.nas"

    stl_files, nastran_data, _ = nastran_to_stl(str(nas_file), output_folder=str(test_tmp_dir))

    assert stl_files
    assert all(Path(f).is_file() for f in stl_files)
    assert nastran_data
