# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import os

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.parametrize_edb import (
    ParametrizeEdbExtensionData,
    main,
)
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests.system.extensions.conftest import (
    local_path as extensions_local_path,
)

pytest.importorskip("pyedb", "0.21.0")


@pytest.mark.skipif(is_linux, reason="Long test for Linux VM.")
def test_parametrize_layout(local_scratch):
    """Test parametrizing EDB layout with comprehensive settings."""
    file_path = os.path.join(
        local_scratch.path, "ANSYS-HSD_V1_param.aedb"
    )

    local_scratch.copyfolder(
        os.path.join(
            extensions_local_path,
            "example_models",
            "T45",
            "ANSYS-HSD_V1.aedb"
        ),
        file_path
    )

    data = ParametrizeEdbExtensionData(
        aedb_path=file_path,
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


def test_parametrize_edb_exceptions():
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
def test_parametrize_edb_custom_settings(local_scratch):
    """Test Parametrize EDB extension with custom settings."""
    file_path = os.path.join(
        local_scratch.path, "ANSYS-HSD_V1_custom.aedb"
    )

    local_scratch.copyfolder(
        os.path.join(
            extensions_local_path,
            "example_models",
            "T45",
            "ANSYS-HSD_V1.aedb"
        ),
        file_path
    )

    # Test with custom parametrization settings
    data = ParametrizeEdbExtensionData(
        aedb_path=file_path,
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
def test_parametrize_edb_zero_expansions(local_scratch):
    """Test Parametrize EDB extension with zero expansions."""
    file_path = os.path.join(
        local_scratch.path, "ANSYS-HSD_V1_zero.aedb"
    )

    local_scratch.copyfolder(
        os.path.join(
            extensions_local_path,
            "example_models",
            "T45",
            "ANSYS-HSD_V1.aedb"
        ),
        file_path
    )

    # Test with zero expansions (should work fine)
    data = ParametrizeEdbExtensionData(
        aedb_path=file_path,
        expansion_polygon_mm=0.0,
        expansion_void_mm=0.0,
        project_name="zero_expansion_project",
    )

    result = main(data)
    assert result is True
