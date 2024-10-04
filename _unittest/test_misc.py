# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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
from unittest import mock

from ansys.aedt.core.misc import current_student_version
from ansys.aedt.core.misc import current_version
from ansys.aedt.core.misc import installed_versions
from ansys.aedt.core.misc import list_installed_ansysem
import pytest


@pytest.fixture
def mock_os_environ():
    """Fixture to mock os.environ."""
    with mock.patch.dict(
        os.environ,
        {
            "ANSYSEM_ROOT241": r"C:\Program Files\AnsysEM\v241\ANSYS",
            "ANSYSEM_ROOT242": r"C:\Program Files\AnsysEM\v242\ANSYS",
            "ANSYSEM_ROOT251": r"C:\Program Files\AnsysEM\v251\ANSYS",
            "ANSYSEMSV_ROOT241": r"C:\Program Files\AnsysEM\v241SV\ANSYS",
            "ANSYSEMSV_ROOT242": r"C:\Program Files\AnsysEM\v242SV\ANSYS",
            "ANSYSEMSV_ROOT251": r"C:\Program Files\AnsysEM\v251SV\ANSYS",
            "ANSYSEM_PY_CLIENT_ROOT242": r"C:\Program Files\AnsysEM\v242CLIENT\ANSYS",
            "ANSYSEM_PY_CLIENT_ROOT251": r"C:\Program Files\AnsysEM\v251CLIENT\ANSYS",
        },
        clear=True,
    ):
        yield  # The mock will be active within the scope of each test using this fixture


def test_list_installed_ansysem(mock_os_environ):
    """Test the list_installed_ansysem function."""
    result = list_installed_ansysem()
    expected = [
        "ANSYSEM_ROOT251",
        "ANSYSEM_ROOT242",
        "ANSYSEM_ROOT241",
        "ANSYSEM_PY_CLIENT_ROOT251",
        "ANSYSEM_PY_CLIENT_ROOT242",
        "ANSYSEMSV_ROOT251",
        "ANSYSEMSV_ROOT242",
        "ANSYSEMSV_ROOT241",
    ]
    assert result == expected


def test_installed_versions(mock_os_environ):
    """Test the installed_versions function."""
    result = installed_versions()
    expected = {
        "2025.1": r"C:\Program Files\AnsysEM\v251\ANSYS",
        "2024.2": r"C:\Program Files\AnsysEM\v242\ANSYS",
        "2024.1": r"C:\Program Files\AnsysEM\v241\ANSYS",
        "2025.1CL": r"C:\Program Files\AnsysEM\v251CLIENT\ANSYS",
        "2024.2CL": r"C:\Program Files\AnsysEM\v242CLIENT\ANSYS",
        "2025.1SV": r"C:\Program Files\AnsysEM\v251SV\ANSYS",
        "2024.2SV": r"C:\Program Files\AnsysEM\v242SV\ANSYS",
        "2024.1SV": r"C:\Program Files\AnsysEM\v241SV\ANSYS",
    }
    assert result == expected


def test_current_version(mock_os_environ):
    """Test the current_version function."""
    with mock.patch("ansys.aedt.core.misc.misc.CURRENT_STABLE_AEDT_VERSION", 2024.2):
        assert current_version() == "2024.2"
    with mock.patch("ansys.aedt.core.misc.misc.CURRENT_STABLE_AEDT_VERSION", 2023.2):
        assert current_version() == ""


def test_current_student_version(mock_os_environ):
    """Test the current_student_version function."""
    with mock.patch("ansys.aedt.core.misc.misc.CURRENT_STABLE_AEDT_VERSION", 2024.2):
        assert current_student_version() == "2024.2SV"
    with mock.patch("ansys.aedt.core.misc.misc.CURRENT_STABLE_AEDT_VERSION", 2023.2):
        assert current_student_version() == ""
