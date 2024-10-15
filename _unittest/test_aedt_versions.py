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

from ansys.aedt.core.generic.aedt_versions import AedtVersions
from ansys.aedt.core.generic.settings import settings
import pytest


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


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


@pytest.fixture
def aedt_versions():
    """Fixture to return a new instance of AedtVersions."""
    return AedtVersions()


def test_list_installed_ansysem(mock_os_environ, aedt_versions):
    """Test the list_installed_ansysem function."""
    result = aedt_versions.list_installed_ansysem
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


def test_installed_versions(mock_os_environ, aedt_versions):
    """Test the installed_versions function."""
    result = aedt_versions.installed_versions
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


@mock.patch("ansys.aedt.core.generic.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2024.2)
def test_current_version_1(mock_os_environ, aedt_versions):
    """Test the current_version function."""
    assert aedt_versions.current_version == "2024.2"


@mock.patch("ansys.aedt.core.generic.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2023.2)
def test_current_version_2(mock_os_environ, aedt_versions):
    """Test the current_version function."""
    assert aedt_versions.current_version == ""


@mock.patch("ansys.aedt.core.generic.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2024.2)
def test_current_student_version_1(mock_os_environ, aedt_versions):
    """Test the current_student_version function."""
    assert aedt_versions.current_student_version == "2024.2SV"


@mock.patch("ansys.aedt.core.generic.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2023.2)
def test_current_student_version_2(mock_os_environ, aedt_versions):
    """Test the current_student_version function."""
    assert aedt_versions.current_student_version == ""


@mock.patch("ansys.aedt.core.generic.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2024.2)
def test_latest_version_1(mock_os_environ, aedt_versions):
    """Test the current_student_version function."""
    assert aedt_versions.latest_version == "2025.1"


@mock.patch("ansys.aedt.core.generic.aedt_versions.CURRENT_STABLE_AEDT_VERSION", 2023.2)
def test_latest_version_2(mock_os_environ, aedt_versions):
    """Test the current_student_version function."""
    assert aedt_versions.latest_version == "2025.1"


def test_latest_version_property(aedt_versions):
    # Case: _latest_version is None and _installed_versions has versions
    aedt_versions._installed_versions = {"2022.2": "path"}
    assert aedt_versions.latest_version == "2022.2"


def test_latest_version_property2(aedt_versions):
    # Case: _latest_version is None and _installed_versions is empty
    aedt_versions._installed_versions = {}
    assert aedt_versions.latest_version == ""


def test_latest_version_property3(aedt_versions):
    # Case: _latest_version is already set
    aedt_versions._latest_version = "2023.1"
    assert aedt_versions.latest_version == "2023.1"


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
def test_is_minimum_version_installed(aedt_versions):
    # Case: Version satisfies minimum version requirement
    aedt_versions._installed_versions = {"2022.1": "path"}
    assert aedt_versions.is_minimum_version_installed


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
def test_is_minimum_version_installed2(aedt_versions):
    # Case: Version does not satisfy minimum version requirement
    aedt_versions._installed_versions = {"2020.1": "path"}
    assert not aedt_versions.is_minimum_version_installed


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
def test_is_minimum_version_installed3(aedt_versions):
    # Case: ValueError due to invalid version format
    aedt_versions._installed_versions = {"invalid": "path"}
    assert not aedt_versions.is_minimum_version_installed


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
def test_is_minimum_version_installed3(aedt_versions):
    # Case: ValueError due to invalid version format
    aedt_versions._installed_versions = {"2022.2SV": "path"}
    assert aedt_versions.is_minimum_version_installed


def test_split_version_and_release(aedt_versions):
    input_version = "2022.2"
    version, release = aedt_versions.split_version_and_release(input_version)
    assert version == 22
    assert release == 2


def test_env_variable(aedt_versions):
    input_version = "2022.2"
    assert aedt_versions.env_variable(input_version) == "ANSYSEM_ROOT222"


@mock.patch.dict(os.environ, {"ANSYSEM_ROOT222": "/path/to/aedt"})
def test_env_path(aedt_versions):
    input_version = "2022.2"
    assert aedt_versions.env_path(input_version) == "/path/to/aedt"


def test_env_variable_student(aedt_versions):
    input_version = "2022.2"
    assert aedt_versions.env_variable_student(input_version) == "ANSYSEMSV_ROOT222"


@mock.patch.dict(os.environ, {"ANSYSEMSV_ROOT222": "/path/to/aedt_student"})
def test_env_path_student(aedt_versions):
    input_version = "2022.2"
    assert aedt_versions.env_path_student(input_version) == "/path/to/aedt_student"


def test_version_to_text(aedt_versions):
    assert aedt_versions.version_to_text("2022.2") == "2022 R2"


@pytest.mark.parametrize(
    "input_version, expected_output",
    [
        (2024.2, "2024.2"),
        (242, "2024.2"),
        (24.2, "2024.2"),
        ("2024.2", "2024.2"),
        ("242", "2024.2"),
        ("24.2", "2024.2"),
    ],
)
def test_normalize_version(aedt_versions, input_version, expected_output):
    assert aedt_versions.normalize_version(input_version) == expected_output


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
@mock.patch.object(AedtVersions, "is_minimum_version_installed", new_callable=mock.PropertyMock)
def test_assert_version(mock_is_minimum_version_installed, mock_os_environ, aedt_versions):
    # Case 1: AEDT is not installed
    aedt_versions._current_version = ""
    aedt_versions._latest_version = ""
    with pytest.raises(Exception) as excinfo:
        aedt_versions.assert_version(None, False)
    assert "AEDT is not installed on your system." in str(excinfo.value)

    # Case 2: Minimum version is not installed
    aedt_versions._current_version = "2021.1"
    aedt_versions._latest_version = "2021.1"
    mock_is_minimum_version_installed.return_value = False
    with pytest.raises(Exception) as excinfo:
        aedt_versions.assert_version(None, False)
    assert f"PyAEDT requires AEDT version 2022 R1 or higher." in str(excinfo.value)


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
def test_assert_version_no_specified_version1(mock_os_environ, aedt_versions):
    with mock.patch("ansys.aedt.core.generic.aedt_versions.pyaedt_logger.warning") as mock_warning:
        # Case 3: Specified version is None and student version found
        aedt_versions._current_student_version = "2022.2SV"
        aedt_versions._installed_versions = {"2022.2SV": "path"}
        student_version, specified_version, version_string = aedt_versions.assert_version(None, True)
        assert student_version
        assert specified_version == "2022.2SV"
        assert version_string == "Ansoft.ElectronicsDesktop.2022.2"
        mock_warning.assert_not_called()


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
def test_assert_version_no_specified_version2(mock_os_environ, aedt_versions):
    with mock.patch("ansys.aedt.core.generic.aedt_versions.pyaedt_logger.warning") as mock_warning:

        # Case 4: No student version found, use the regular version
        aedt_versions._current_version = "2022.2"
        aedt_versions._current_student_version = ""
        aedt_versions._installed_versions = {"2022.2": "path"}
        student_version, specified_version, version_string = aedt_versions.assert_version(None, True)
        assert not student_version
        assert specified_version == "2022.2"
        mock_warning.assert_called_once_with("AEDT Student Version not found on the system. Using regular version.")


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
def test_assert_version_no_specified_version3(mock_os_environ, aedt_versions):
    with mock.patch("ansys.aedt.core.generic.aedt_versions.pyaedt_logger.warning") as mock_warning:
        # Case 4b: No regular version found, use the student version
        aedt_versions._current_version = "2022.2SV"
        aedt_versions._current_student_version = "2022.2SV"
        aedt_versions._installed_versions = {"2022.2SV": "path"}
        student_version, specified_version, version_string = aedt_versions.assert_version(None, False)
        assert student_version
        assert specified_version == "2022.2SV"
        mock_warning.assert_called_once_with("Only AEDT Student Version found on the system. Using Student Version.")


@mock.patch("ansys.aedt.core.generic.aedt_versions.MINIMUM_COMPATIBLE_AEDT_VERSION", 2022.1)
def test_assert_version2(mock_os_environ, aedt_versions):
    # Case 5: Normalized specified version with SV
    student_version, specified_version, version_string = aedt_versions.assert_version("2024.2", True)
    assert student_version
    assert specified_version == "2024.2SV"

    # Case 6: Normalized specified version regular
    student_version, specified_version, version_string = aedt_versions.assert_version("2024.2", False)
    assert not student_version
    assert specified_version == "2024.2"

    # Case 7: Specified version not found in installed versions
    with pytest.raises(ValueError) as excinfo:
        aedt_versions.assert_version("2023.1", False)
    assert "Specified version 2023.1 is not installed on your system" in str(excinfo.value)


def test_assert_version_remote_rpc_session(monkeypatch, mock_os_environ, aedt_versions):
    # Case 8: Version found and remote session exists
    # Use monkeypatch to temporarily set the remote_rpc_session
    monkeypatch.setattr(settings, "remote_rpc_session", mock.MagicMock())
    settings.remote_rpc_session.aedt_version = "2022.2"
    settings.remote_rpc_session.student_version = False
    student_version, specified_version, version_string = aedt_versions.assert_version("2024.2", False)
    assert student_version == False
    assert specified_version == "2022.2"
    assert version_string == "Ansoft.ElectronicsDesktop.2022.2"


def test_assert_version_specify_version(mock_os_environ, aedt_versions):
    student_version, specified_version, version_string = aedt_versions.assert_version("2024.2", False)
    assert student_version == False
    assert specified_version == "2024.2"
    assert version_string == "Ansoft.ElectronicsDesktop.2024.2"
