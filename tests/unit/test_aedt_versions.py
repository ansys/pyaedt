# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

import pytest

from ansys.aedt.core.internal.aedt_versions import AedtVersions


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


@pytest.fixture
def mock_path_exist():
    """Fixture to mock pathlib.Path.exists."""
    with mock.patch("pathlib.Path.exists", return_value=True):
        yield


@pytest.fixture
def mock_os_environ():
    """Fixture to mock os.environ."""
    with mock.patch.dict(
        os.environ,
        {
            "ANSYSEM_ROOT241": r"C:\Program Files\AnsysEM\v241\ANSYS",
            "ANSYSEM_ROOT242": r"C:\Program Files\AnsysEM\v242\ANSYS",
            "ANSYSEM_ROOT251": r"C:\Program Files\AnsysInc\v251\AnsysEM",
            "ANSYSEM_ROOT252": r"C:\Program Files\AnsysInc\v252\AnsysEM",
            "ANSYSEMSV_ROOT241": r"C:\Program Files\AnsysEM\v241SV\ANSYS",
            "ANSYSEMSV_ROOT242": r"C:\Program Files\AnsysEM\v242SV\ANSYS",
            "ANSYSEMSV_ROOT251": r"C:\Program Files\AnsysEM\v251SV\ANSYS",
            "ANSYSEMSV_ROOT252": r"C:\Program Files\AnsysEM\v252SV\ANSYS",
            "ANSYSEM_PY_CLIENT_ROOT242": r"C:\Program Files\AnsysEM\v242CLIENT\ANSYS",
            "ANSYSEM_PY_CLIENT_ROOT251": r"C:\Program Files\AnsysEM\v251CLIENT\ANSYS",
            "ANSYSEM_PY_CLIENT_ROOT252": r"C:\Program Files\AnsysEM\v252CLIENT\ANSYS",
            "AWP_ROOT252": r"C:\Program Files\AnsysInc\v252",
            "AWP_ROOT251": r"C:\Program Files\AnsysInc\v251",
            "AWP_ROOT242": r"C:\Program Files\AnsysInc\v242",
        },
        clear=True,
    ):
        yield  # The mock will be active within the scope of each test using this fixture


@pytest.fixture
def aedt_versions():
    """Fixture to return a new instance of AedtVersions."""
    return AedtVersions()


def test_list_installed_ansysem(mock_os_environ, mock_path_exist, aedt_versions):
    """Test the list_installed_ansysem function."""
    result = aedt_versions.list_installed_ansysem
    expected = [
        "ANSYSEM_ROOT252",
        "ANSYSEM_ROOT251",
        "ANSYSEM_ROOT242",
        "ANSYSEM_ROOT241",
        "ANSYSEM_PY_CLIENT_ROOT252",
        "ANSYSEM_PY_CLIENT_ROOT251",
        "ANSYSEM_PY_CLIENT_ROOT242",
        "ANSYSEMSV_ROOT252",
        "ANSYSEMSV_ROOT251",
        "ANSYSEMSV_ROOT242",
        "ANSYSEMSV_ROOT241",
        "AWP_ROOT252",
        "AWP_ROOT251",
        "AWP_ROOT242",
    ]
    assert result == expected


def test_installed_versions(mock_os_environ, mock_path_exist, aedt_versions):
    """Test the installed_versions function."""
    result = aedt_versions.installed_versions
    expected = {
        "2025.2": r"C:\Program Files\AnsysEM\v252\ANSYS",
        "2025.1": r"C:\Program Files\AnsysEM\v251\ANSYS",
        "2024.2": r"C:\Program Files\AnsysEM\v242\ANSYS",
        "2024.1": r"C:\Program Files\AnsysEM\v241\ANSYS",
        "2025.2CL": r"C:\Program Files\AnsysEM\v252CLIENT\ANSYS",
        "2025.1CL": r"C:\Program Files\AnsysEM\v251CLIENT\ANSYS",
        "2024.2CL": r"C:\Program Files\AnsysEM\v242CLIENT\ANSYS",
        "2025.2SV": r"C:\Program Files\AnsysEM\v252SV\ANSYS",
        "2025.1SV": r"C:\Program Files\AnsysEM\v251SV\ANSYS",
        "2024.2SV": r"C:\Program Files\AnsysEM\v242SV\ANSYS",
        "2024.1SV": r"C:\Program Files\AnsysEM\v241SV\ANSYS",
        "2025.2AWP": r"C:\Program Files\AnsysInc\v252",
        "2025.1AWP": r"C:\Program Files\AnsysInc\v251",
        "2024.2AWP": r"C:\Program Files\AnsysInc\v242",
    }
    assert result.keys() == expected.keys()


@mock.patch("ansys.aedt.core.internal.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2024.2)
def test_current_version_1(mock_os_environ, aedt_versions):
    """Test the current_version function."""
    assert aedt_versions.current_version == "2024.2"


@mock.patch("ansys.aedt.core.internal.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2023.2)
def test_current_version_2(mock_os_environ, aedt_versions):
    """Test the current_version function."""
    assert aedt_versions.current_version == ""


@mock.patch("ansys.aedt.core.internal.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2024.2)
def test_current_student_version_1(mock_os_environ, aedt_versions):
    """Test the current_student_version function."""
    assert aedt_versions.current_student_version == "2024.2SV"


@mock.patch("ansys.aedt.core.internal.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2023.2)
def test_current_student_version_2(mock_os_environ, aedt_versions):
    """Test the current_student_version function."""
    assert aedt_versions.current_student_version == ""


@mock.patch("ansys.aedt.core.internal.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2024.2)
def test_latest_version_1(mock_os_environ, aedt_versions):
    """Test the current_student_version function."""
    assert aedt_versions.latest_version == "2025.2"


@mock.patch("ansys.aedt.core.internal.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2023.2)
def test_latest_version_2(mock_os_environ, aedt_versions):
    """Test the current_student_version function."""
    assert aedt_versions.latest_version == "2025.2"


def test_get_version_env_variable(aedt_versions):
    # Test case 1: Version < 20, release < 3
    version_id = "2018.2"
    expected_output = "ANSYSEM_ROOT192"
    assert aedt_versions.get_version_env_variable(version_id) == expected_output

    # Test case 2: Version < 20, release >= 3
    version_id = "2019.3"
    expected_output = "ANSYSEM_ROOT195"
    assert aedt_versions.get_version_env_variable(version_id) == expected_output

    # Test case 3: Version >= 20
    version_id = "2023.2"
    expected_output = "ANSYSEM_ROOT232"
    assert aedt_versions.get_version_env_variable(version_id) == expected_output
