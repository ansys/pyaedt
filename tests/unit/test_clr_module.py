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
from pathlib import Path
import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

DOTNET_ROOT = "dummy/root/path"
DOTNET_ROOT_PATH = Path(DOTNET_ROOT)
DOTNETCORE2_FILE = "dummy/dotnetcore2/file"
DOTNETCORE2_BIN = "dummy/dotnetcore2/bin"
PYAEDT_FILE = "dummy/pyaedt/file"


@pytest.fixture
def clean_environment():
    initial_sys_modules = sys.modules.copy()
    initial_os_environ = os.environ.copy()

    if "ansys.aedt.core.internal.clr_module" in sys.modules:
        del sys.modules["ansys.aedt.core.internal.clr_module"]
    if "DOTNET_ROOT" in os.environ:
        del os.environ["DOTNET_ROOT"]

    yield

    sys.modules.clear()
    sys.modules.update(initial_sys_modules)
    os.environ.clear()
    os.environ.update(initial_os_environ)


@pytest.mark.skipif(os.name != "posix", reason="test for linux behavior")
@patch("pythonnet.load")
@patch("clr_loader.get_coreclr")
def test_use_system_dotnet(mock_get_coreclr, mock_load, clean_environment) -> None:
    mock_runtime = MagicMock()
    mock_runtime.dotnet_root = DOTNET_ROOT_PATH
    mock_get_coreclr.return_value = mock_runtime

    import ansys.aedt.core.internal.clr_module as cm

    assert cm.is_clr
    assert DOTNET_ROOT_PATH.as_posix() == os.environ["DOTNET_ROOT"]
    del os.environ["DOTNET_ROOT"]
