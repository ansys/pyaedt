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

import sys
from typing import List
from unittest.mock import MagicMock

import pytest

UNIT_TEST_PREFIX = "tests/unit"
INTEGRATION_TEST_PREFIX = "tests/integration"
SYSTEM_TEST_PREFIX = "tests/system"
SYSTEM_SOLVERS_TEST_PREFIX = "tests/system/solvers"
SYSTEM_GENERAL_TEST_PREFIX = "tests/system/general"
VISUALIZATION_GENERAL_TEST_PREFIX = "tests/system/visualization"
EXTENSIONS_GENERAL_TEST_PREFIX = "tests/system/extensions"


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    """Hook used to apply marker on tests."""
    for item in items:
        # Mark unit, integration and system tests
        if item.nodeid.startswith(UNIT_TEST_PREFIX):
            item.add_marker(pytest.mark.unit)
        elif item.nodeid.startswith(INTEGRATION_TEST_PREFIX):
            item.add_marker(pytest.mark.integration)
        elif item.nodeid.startswith(SYSTEM_TEST_PREFIX):
            item.add_marker(pytest.mark.system)
        # Finer markers for system tests
        if item.nodeid.startswith(SYSTEM_SOLVERS_TEST_PREFIX):
            item.add_marker(pytest.mark.solvers)
        elif item.nodeid.startswith(SYSTEM_GENERAL_TEST_PREFIX):
            item.add_marker(pytest.mark.general)
        elif item.nodeid.startswith(VISUALIZATION_GENERAL_TEST_PREFIX):
            item.add_marker(pytest.mark.visualization)
        elif item.nodeid.startswith(EXTENSIONS_GENERAL_TEST_PREFIX):
            item.add_marker(pytest.mark.extensions)


@pytest.fixture
def touchstone_file(tmp_path):
    file_path = tmp_path / "dummy.s2p"
    file_content = """
! Terminal data exported
! Port[1] = Port1
! Port[2] = Port2
0.1                            0.1 0.2
"""

    file_path.write_text(file_content)
    return file_path


@pytest.fixture()
def patch_graphics_modules(monkeypatch):
    modules = [
        "matplotlib",
        "matplotlib.pyplot",
        "pyvista",
        "imageio",
        "meshio",
        "vtk",
        "ansys.tools.visualization_interface",
        "ansys.tools.visualization_interface.backends",
        "ansys.tools.visualization_interface.backends.pyvista",
    ]

    mocks = {}
    for module in modules:
        mock = MagicMock(name=f"mock_{module}")
        mocks[module] = mock
        monkeypatch.setitem(sys.modules, module, mock)

    # Specific action to make a mock an attribute of another mock
    mocks["matplotlib"].pyplot = mocks["matplotlib.pyplot"]
    mocks["ansys.tools.visualization_interface"].backends = mocks["ansys.tools.visualization_interface.backends"]
    mocks["ansys.tools.visualization_interface.backends"].pyvista = mocks[
        "ansys.tools.visualization_interface.backends.pyvista"
    ]

    yield mocks
