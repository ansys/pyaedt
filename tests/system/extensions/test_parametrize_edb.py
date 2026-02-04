# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import shutil

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb import ParametrizeEdbExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb import main
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_EXTENSIONS_PATH

pytest.importorskip("pyedb", "0.21.0")

TEST_SUBFOLDER = "T45"
EDB_PROJECT = "ANSYS-HSD_V1.aedb"
SI_VERSE_PATH = TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER / EDB_PROJECT


@pytest.mark.skipif(is_linux, reason="Long test for Linux VM.")
def test_parametrize_layout(desktop, test_tmp_dir):
    """Test parametrizing EDB layout with comprehensive settings."""
    file_path = test_tmp_dir / "ANSYS-HSD_V1_param.aedb"

    shutil.copytree(SI_VERSE_PATH, file_path, dirs_exist_ok=True)

    data = ParametrizeEdbExtensionData(
        aedb_path=str(file_path),
        parametrize_layers=True,
        parametrize_materials=True,
        parametrize_padstacks=True,
        parametrize_traces=True,
        nets_filter=["GND"],
        expansion_polygon_mm=0.1,
        expansion_void_mm=0.1,
        relative_parametric=True,
        project_name="new_parametrized",
    )

    result = main(data)
    assert result is True


def test_parametrize_edb_exceptions(desktop):
    """Test exceptions thrown by the Parametrize EDB extension."""
    # Test with negative polygon expansion
    data = ParametrizeEdbExtensionData(
        expansion_polygon_mm=-0.5,
        project_name="test_project",
    )
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with negative void expansion
    data = ParametrizeEdbExtensionData(
        expansion_void_mm=-0.2,
        project_name="test_project",
    )
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with empty project name
    data = ParametrizeEdbExtensionData(
        project_name="",
    )
    with pytest.raises(AEDTRuntimeError):
        main(data)


@pytest.mark.skipif(is_linux, reason="Long test for Linux VM.")
def test_parametrize_edb_custom_settings(desktop, test_tmp_dir):
    """Test Parametrize EDB extension with custom settings."""
    file_path = test_tmp_dir / "ANSYS-HSD_V1_param.aedb"

    shutil.copytree(SI_VERSE_PATH, file_path)

    # Test with custom parametrization settings
    data = ParametrizeEdbExtensionData(
        aedb_path=str(file_path),
        parametrize_layers=False,
        parametrize_materials=True,
        parametrize_padstacks=False,
        parametrize_traces=True,
        nets_filter=["GND"],
        expansion_polygon_mm=1.0,
        expansion_void_mm=0.5,
        relative_parametric=False,
        project_name="custom_parametric_project",
    )

    result = main(data)
    assert result is True


@pytest.mark.skipif(is_linux, reason="Long test for Linux VM.")
def test_parametrize_edb_zero_expansions(desktop, test_tmp_dir):
    """Test Parametrize EDB extension with zero expansions."""
    file_path = test_tmp_dir / "ANSYS-HSD_V1_zero.aedb"

    shutil.copytree(SI_VERSE_PATH, file_path)

    # Test with zero expansions (should work fine)
    data = ParametrizeEdbExtensionData(
        aedb_path=str(file_path),
        expansion_polygon_mm=0.0,
        expansion_void_mm=0.0,
        project_name="zero_expansion_project",
    )

    result = main(data)
    assert result is True
