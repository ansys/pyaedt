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

from pathlib import Path
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest
import toml

from ansys.aedt.core.extensions.hfss3dlayout.via_design import EXPORT_EXAMPLES
from ansys.aedt.core.extensions.hfss3dlayout.via_design import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.via_design import ViaDesignExtension

MOCK_EXAMPLE_PATH = "/mock/path/configuration.toml"
MOCK_CONTENT = "Dummy content"
MOCK_TOML_CONTENT = {
    "stacked_vias": {
        "type_1": {"param1": "value1"},
    },
    "signals": {
        "sig_1": {"stacked_vias": "type_1"},
    },
    "differential_signals": {
        "diff_1": {"stacked_vias": "type_1"},
    },
}
MOCK_CALL_OPEN = mock_open(read_data=MOCK_CONTENT)
ORIGINAL_CALL_OPEN = open


@pytest.fixture
def toml_file_path(tmp_path):
    """Create a temporary TOML file with mock content."""
    file_path = tmp_path / "config.toml"
    with file_path.open("w") as f:
        toml.dump(MOCK_TOML_CONTENT, f)
    return file_path


def conditional_open(file=None, mode: str = "r", *args, **kwargs):
    """Open mocked TOML files, otherwise call real open."""
    if file is None or str(file).endswith(".toml"):
        return MOCK_CALL_OPEN(file, mode, *args, **kwargs)
    else:
        return ORIGINAL_CALL_OPEN(file, mode, *args, **kwargs)


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_via_design_extension_default(mock_desktop, mock_hfss_3d_layout_app) -> None:
    """Test instantiation of the Via Design extension."""
    mock_desktop.return_value = MagicMock()

    extension = ViaDesignExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert EXPORT_EXAMPLES == extension.export_examples
    assert extension.create_design_path is None
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("tkinter.filedialog.asksaveasfilename")
@patch("builtins.open", side_effect=conditional_open)
def test_via_design_extension_select_configuration_example(
    mock_file_open,
    mock_asksaveasfilename,
    mock_hfss_3d_layout_app,
) -> None:
    """Test saving examples configuration success"""
    mock_asksaveasfilename.return_value = MOCK_EXAMPLE_PATH

    extension = ViaDesignExtension(withdraw=True)

    for example in EXPORT_EXAMPLES:
        example_name = example.toml_file_path.stem
        widget_name = f".!notebook.!frame.button_{example_name}"
        button = extension.root.nametowidget(widget_name)
        button.invoke()

        mock_file_open.assert_any_call(
            example.toml_file_path,
            "r",
            encoding="utf-8",
        )
    mock_file_open.assert_any_call(
        MOCK_EXAMPLE_PATH,
        "w",
        encoding="utf-8",
    )
    mock_file_open().write.assert_any_call(MOCK_CONTENT)

    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename", return_value=MOCK_EXAMPLE_PATH)
@patch("builtins.open", side_effect=conditional_open)
def test_via_design_extension_create_design_failure(
    mock_file_open,
    mock_askopenfilename,
    mock_hfss_3d_layout_app,
) -> None:
    """Test create design with non existing file"""
    extension = ViaDesignExtension(withdraw=True)

    widget_name = ".!frame.button_create_design"
    button = extension.root.nametowidget(widget_name)
    with pytest.raises(TclError):
        button.invoke()
    extension.root.destroy()


@patch("ansys.aedt.core.extensions.hfss3dlayout.via_design.Hfss3dLayout")
@patch("ansys.aedt.core.extensions.hfss3dlayout.via_design.ViaDesignBackend")
@patch("tkinter.filedialog.askopenfilename")
@patch("builtins.open", side_effect=conditional_open)
@patch.object(Path, "is_file", return_value=True)
def test_via_design_extension_create_design_sucess(
    mock_path_is_file,
    mock_file_open,
    mock_askopenfilename,
    mock_via_design_backend,
    mock_hfss3dlayout_class,
    toml_file_path,
    mock_hfss_3d_layout_app,
) -> None:
    """Test create design success"""
    EXPECTED_RESULT = {
        "signals": {
            "sig_1": {"stacked_vias": {"param1": "value1"}},
        },
        "differential_signals": {
            "diff_1": {"stacked_vias": {"param1": "value1"}},
        },
    }
    mock_askopenfilename.return_value = toml_file_path

    # Ensure the mocked backend provides an app with an edbpath attribute
    mock_via_design_backend.return_value.app.edbpath = "/path/mock.aedb"

    extension = ViaDesignExtension(withdraw=True)

    widget_name = ".!frame.button_create_design"
    button = extension.root.nametowidget(widget_name)
    button.invoke()

    # Verify the ViaDesignBackend was instantiated with the expected configuration
    mock_via_design_backend.assert_called_with(EXPECTED_RESULT)
    extension.root.destroy()


@patch("tkinter.filedialog.asksaveasfilename")
def test_via_design_examples_success(
    mock_asksaveasfilename,
    tmp_path,
    mock_hfss_3d_layout_app,
) -> None:
    """Test the examples provided in the via design extension."""
    extension = ViaDesignExtension(withdraw=True)

    for example in EXPORT_EXAMPLES:
        example_name = example.toml_file_path.stem
        widget_name = f".!notebook.!frame.button_{example_name}"
        button = extension.root.nametowidget(widget_name)
        path = tmp_path / f"{example_name}.toml"
        mock_asksaveasfilename.return_value = path
        button.invoke()
        assert path.is_file()
    extension.root.destroy()
