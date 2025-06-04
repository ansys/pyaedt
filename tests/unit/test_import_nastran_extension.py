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

from dataclasses import asdict
import os
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.project.import_nastran import EXTENSION_DEFAULT_ARGUMENTS
from ansys.aedt.core.extensions.project.import_nastran import ExtensionData
from ansys.aedt.core.extensions.project.import_nastran import create_ui

MOCK_NAS_PATH = "/mock/path/file1.nas"
MOCK_STL_PATH = "/mock/path/file2.stl"


def test_import_nastran_toggle_theme():
    """Test that the theme toggle button works correctly."""
    root = create_ui()
    assert root.theme == "light"

    toggle_theme = root.nametowidget("theme_button_frame.theme_toggle_button")
    toggle_theme.invoke()

    assert root.theme == "dark"


def test_import_nastran_default_values():
    """Test that the default values of the UI are set correctly."""
    root = create_ui(withdraw=True)
    root.nametowidget("ok_button").invoke()

    from ansys.aedt.core.extensions.project.import_nastran import result

    assert EXTENSION_DEFAULT_ARGUMENTS == asdict(result)


@patch("tkinter.filedialog.askopenfilename")
def test_import_nastran_modified_values(mock_askopenfilename):
    """Test that the modifief values of the UI are returned correctly."""
    EXPECTED_RESULT = ExtensionData(0.5, True, False, MOCK_NAS_PATH)
    mock_askopenfilename.return_value = MOCK_NAS_PATH

    root = create_ui(withdraw=True)

    root.nametowidget("browse_button").invoke()
    root.nametowidget("check_lightweight").invoke()
    root.nametowidget("check_planar_merge").invoke()
    root.nametowidget("decimation_text").delete("1.0", "end")
    root.nametowidget("decimation_text").insert("1.0", "0.5")
    root.nametowidget("ok_button").invoke()

    from ansys.aedt.core.extensions.project.import_nastran import result

    assert EXPECTED_RESULT == result


@pytest.mark.parametrize("mock_path", [MOCK_NAS_PATH, MOCK_STL_PATH])
@patch("tkinter.filedialog.askopenfilename")
def test_import_nastran_preview_on_non_existing_file(mock_askopenfilename, mock_path):
    """Test that the preview button raises an exception when non existing file is selected."""
    mock_askopenfilename.return_value = mock_path
    root = create_ui(withdraw=True)
    root.nametowidget("browse_button").invoke()

    content = root.nametowidget("file_path_text").get("1.0", "end").strip()
    assert content == mock_path

    preview_button = root.nametowidget("preview_button")
    with pytest.raises(Exception):
        preview_button.invoke()
