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

import sys
from unittest.mock import patch
import warnings

import pytest

from ansys.aedt.core import LATEST_DEPRECATED_PYTHON_VERSION
from ansys.aedt.core import PYTHON_VERSION_WARNING
from ansys.aedt.core import deprecation_warning
from pyaedt import ALIAS_WARNING

VALID_PYTHON_VERSION = (LATEST_DEPRECATED_PYTHON_VERSION[0], LATEST_DEPRECATED_PYTHON_VERSION[1] + 1)


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


@patch.object(warnings, "warn")
def test_deprecation_warning_with_deprecated_python_version(mock_warn, monkeypatch):
    """Test that python version warning is triggered."""
    monkeypatch.setattr(sys, "version_info", LATEST_DEPRECATED_PYTHON_VERSION)

    deprecation_warning()

    mock_warn.assert_called_once_with(PYTHON_VERSION_WARNING, FutureWarning)


@patch.object(warnings, "warn")
def test_deprecation_warning_with_valid_python_version(mock_warn, monkeypatch):
    """Test that python version warning is not triggered."""
    monkeypatch.setattr(sys, "version_info", VALID_PYTHON_VERSION)

    deprecation_warning()

    mock_warn.assert_not_called()


def test_alias_deprecation_warning():
    """Test that pyaedt alias warning is triggered."""
    import importlib

    import pyaedt

    with pytest.warns(FutureWarning, match=ALIAS_WARNING):
        importlib.reload(pyaedt)
