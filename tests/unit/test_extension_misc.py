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

"""Test extension utilities functions."""

import os
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.misc import ExtensionTheme
from ansys.aedt.core.extensions.misc import __string_to_bool
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student

DUMMY_ENV_VARS = {
    "PYAEDT_PROCESS_ID": "12345",
    "PYAEDT_DESKTOP_PORT": "6789",
    "PYAEDT_DESKTOP_VERSION": "3024.2",
    "PYAEDT_STUDENT_VERSION": "True",
}


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


@pytest.fixture
def mock_env_vars():
    """Fixture to temporarily set environment variables."""
    with patch.dict(os.environ, DUMMY_ENV_VARS):
        yield


def test_get_process_id(mock_env_vars):
    assert get_process_id() == 12345


def test_get_port(mock_env_vars):
    assert get_port() == 6789


def test_get_aedt_version(mock_env_vars):
    assert get_aedt_version() == "3024.2"


def test_is_student(mock_env_vars):
    assert is_student() is True


def test_get_arguments_with_default_values():
    """Test `get_arguments` when no command-line arguments are passed."""
    mock_argv = ["script_name"]
    with patch("sys.argv", mock_argv):
        result = get_arguments(args={"is_batch": False, "is_test": False})
        assert result["is_batch"] is False
        assert result["is_test"] is False


def test_get_arguments_with_custom_values():
    """Test `get_arguments` with custom command-line arguments."""
    mock_argv = ["script_name", "--is_batch", "true", "--is_test", "false"]
    with patch("sys.argv", mock_argv):
        result = get_arguments(args={"is_batch": False, "is_test": False})
        assert result["is_batch"] is True
        assert result["is_test"] is False


def test_get_arguments_with_invalid_arguments():
    """Test `get_arguments` with invalid command-line arguments."""
    mock_argv = ["script_name", "--invalid_arg", "true"]
    with patch("sys.argv", mock_argv):
        with pytest.raises(SystemExit):
            get_arguments()


@pytest.mark.parametrize(
    "input_value, expected",
    [("true", True), ("false", False), ("1", True), ("0", False), (True, True), (False, False)],
)
def test_string_to_bool(input_value, expected):
    assert __string_to_bool(input_value) == expected


def test_extension_theme():
    mock_style = MagicMock()
    theme = ExtensionTheme()

    # Test light theme application
    theme.apply_light_theme(mock_style)
    mock_style.configure.assert_called()

    # Test dark theme application
    theme.apply_dark_theme(mock_style)
    mock_style.configure.assert_called()
