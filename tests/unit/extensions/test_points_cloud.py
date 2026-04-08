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
import tkinter
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.common.points_cloud import EXTENSION_TITLE
from ansys.aedt.core.extensions.common.points_cloud import PointsCloudExtension
from ansys.aedt.core.extensions.common.points_cloud import PointsCloudExtensionData
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_hfss_app_with_objects_in_group(mock_hfss_app):
    """Fixture to create a mock AEDT application (extends HFSS mock)."""
    mock_modeler = MagicMock()
    mock_modeler.get_objects_in_group.return_value = ["dummy_solid"]
    mock_hfss_app.modeler = mock_modeler

    yield mock_hfss_app


def test_point_cloud_extension_default(mock_hfss_app_with_objects_in_group) -> None:
    """Test instantiation of the point cloud extension."""
    extension = PointsCloudExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_point_cloud_extension_generate_button(mock_hfss_app_with_objects_in_group) -> None:
    """Test update of extension data after clicking on "Generate" button."""
    extension = PointsCloudExtension(withdraw=True)
    extension._widgets["objects_list"].selection_set(1)
    extension.root.children["buttons_frame"].children["generate"].invoke()
    data: PointsCloudExtensionData = extension.data

    assert ["dummy_solid"] == data.choice
    assert 1000 == data.points
    assert "" == data.output_file


def test_point_cloud_extension_generate_button_multiple_objects(mock_hfss_app_with_objects_in_group) -> None:
    """Test update of extension data after clicking on "Generate" button."""
    long_name = "very_long_name_to_test_scroll_bar_resize"
    mock_hfss_app_with_objects_in_group.modeler.get_objects_in_group.return_value = [long_name] * 4
    extension = PointsCloudExtension(withdraw=True)
    extension._widgets["objects_list"].selection_set(1)
    extension.root.children["buttons_frame"].children["generate"].invoke()
    data: PointsCloudExtensionData = extension.data

    assert [long_name] == data.choice
    assert 1000 == data.points
    assert "" == data.output_file


@patch("tkinter.filedialog.asksaveasfilename")
def test_point_cloud_extension_browse_button(mock_filedialog, mock_hfss_app_with_objects_in_group) -> None:
    """Test call to filedialog.asksaveasfilename method from tkinter after clicking on "Browse" button."""
    extension = PointsCloudExtension(withdraw=True)

    output_widget = extension._widgets["output_file_entry"]
    # Simulate that it has already content
    output_widget.configure(state="normal")
    output_widget.insert("1.0", "old_value")
    output_widget.configure(state="disabled")

    extension.root.children["input_frame"].children["browse_output"].invoke()

    mock_filedialog.assert_called_once()


@patch("ansys.aedt.core.extensions.common.points_cloud.generate_point_cloud")
def test_point_cloud_extension_preview_button(
    mock_generate_cloud, mock_hfss_app_with_objects_in_group, patch_graphics_modules
) -> None:
    """Test call to pyvista plotter after clicking on "Preview" button."""
    extension = PointsCloudExtension(withdraw=True)
    extension._widgets["objects_list"].selection_set(1)
    extension.root.children["buttons_frame"].children["preview"].invoke()

    patch_graphics_modules["pyvista"].Plotter().show.assert_called_once()


def test_point_cloud_extension_exceptions(mock_hfss_app_with_objects_in_group) -> None:
    """Test exceptions thrown by the point cloud extension."""
    # Triggering AEDTRuntimeError due to the absence of objects in current design
    mock_hfss_app_with_objects_in_group.modeler.get_objects_in_group.return_value = []
    with pytest.raises(AEDTRuntimeError):
        extension = PointsCloudExtension(withdraw=True)

    # Triggering TclError when calling "generate" without selecting an object
    mock_hfss_app_with_objects_in_group.modeler.get_objects_in_group.return_value = ["dummy_solid"]
    extension = PointsCloudExtension(withdraw=True)
    with pytest.raises(TclError):
        extension.root.children["buttons_frame"].children["generate"].invoke()

    # Triggering TclError when calling "generate" with an invalid number of points
    extension = PointsCloudExtension(withdraw=True)
    extension._widgets["objects_list"].selection_set(1)
    extension._widgets["points_entry"].delete("1.0", tkinter.END)
    extension._widgets["points_entry"].insert(tkinter.END, "0")
    with pytest.raises(TclError):
        extension.root.children["buttons_frame"].children["generate"].invoke()

    # Triggering TclError when calling "generate" with an invalid output path
    extension = PointsCloudExtension(withdraw=True)
    extension._widgets["objects_list"].selection_set(1)
    extension._widgets["output_file_entry"].config(state="normal")
    extension._widgets["output_file_entry"].insert(tkinter.END, str(Path(__file__))[1:])
    extension._widgets["output_file_entry"].config(state="disabled")
    with pytest.raises(TclError):
        extension.root.children["buttons_frame"].children["generate"].invoke()


def test_check_design_type_invalid(mock_circuit_app) -> None:
    """Unsupported design types raise on init and call release_desktop."""
    with patch.object(PointsCloudExtension, "release_desktop") as mock_release:
        with pytest.raises(AEDTRuntimeError, match="This extension only works"):
            PointsCloudExtension(withdraw=True)
        mock_release.assert_called_once()
