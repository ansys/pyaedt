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

"""Test utility functions of PyAEDT.
"""

import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import settings

SETTINGS_RELEASE_ON_EXCEPTION = settings.release_on_exception
SETTINGS_ENABLE_ERROR_HANDLER = settings.enable_error_handler
ERROR_MESSAGE = "Dummy message."


@pyaedt_function_handler(deprecated_arg="trigger_exception")
def foo(trigger_exception=True):
    """Some dummy function used for testing."""
    if trigger_exception:
        raise Exception(ERROR_MESSAGE)


@patch("pyaedt.generic.desktop_sessions._desktop_sessions")
def test_handler_release_on_exception(mock_sessions):
    """Test handler while activating or deactivating error handler."""
    mock_session = MagicMock()
    mock_sessions.values.return_value = [mock_session]
    settings.enable_error_handler = True
    settings.release_on_exception = True

    # Check that release desktop is called once
    foo()
    assert mock_session.release_desktop.assert_called_once

    # Check that release desktop is not called
    settings.release_on_exception = False
    foo()
    assert mock_session.release_desktop.assert_called

    # Teardown
    settings.enable_error_handler = SETTINGS_ENABLE_ERROR_HANDLER
    settings.release_on_exception = SETTINGS_RELEASE_ON_EXCEPTION


def test_handler_enable_error_handler():
    """Test handler while activating/deactivating error handler."""
    settings.enable_error_handler = True
    assert foo() == False

    settings.enable_error_handler = False
    with pytest.raises(Exception) as exec_info:
        foo()
    assert str(exec_info.value) == ERROR_MESSAGE

    # Teardown
    settings.enable_error_handler = SETTINGS_ENABLE_ERROR_HANDLER


def test_handler_deprecation_log_warning(caplog):
    """Test handler deprecation argument mechanism."""
    EXPECTED_ARGUMENT = "Argument `deprecated_arg` is deprecated for method `foo`; use `trigger_exception` instead."

    with caplog.at_level(logging.WARNING, logger="Global"):
        foo(deprecated_arg=False)
    assert len(caplog.records) == 1
    assert "WARNING" == caplog.records[0].levelname
    assert EXPECTED_ARGUMENT == caplog.records[0].message

    foo(trigger_exception=False)
    assert len(caplog.records) == 1
