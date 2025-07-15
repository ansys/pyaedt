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

from pathlib import Path
import tkinter
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.project.points_cloud import EXTENSION_TITLE
from ansys.aedt.core.extensions.project.points_cloud import PointsCloudExtension
from ansys.aedt.core.extensions.project.points_cloud import PointsCloudExtensionData
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_aedt_app():
    """Fixture to create a mock AEDT application."""

    mock_modeler = MagicMock()
    mock_modeler.get_objects_in_group.return_value = ["dummy_solid"]

    mock_aedt_application = MagicMock()
    mock_aedt_application.modeler = mock_modeler

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = mock_aedt_application
        yield mock_aedt_application


def test_point_cloud_extension_default(mock_aedt_app):
    """Test instantiation of the point cloud extension."""

    extension = PointsCloudExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_point_cloud_extension_generate_button(mock_aedt_app):
    """Test update of extension data after clicking on "Generate" button."""

    extension = PointsCloudExtension(withdraw=True)
    extension.objects_list_lb.selection_set(1)
    extension.root.nametowidget("generate").invoke()
    data: PointsCloudExtensionData = extension.data

    assert ["dummy_solid"] == data.choice
    assert 1000 == data.points
    assert "" == data.output_file


@patch("tkinter.filedialog.asksaveasfilename")
def test_point_cloud_extension_browse_button(mock_filedialog, mock_aedt_app):
    """Test call to pyvista plotter after clicking on "Preview" button."""

    extension = PointsCloudExtension(withdraw=True)
    extension.root.nametowidget("browse_output").invoke()

    mock_filedialog.assert_called_once()


@patch("ansys.aedt.core.extensions.project.points_cloud.generate_point_cloud")
def test_point_cloud_extension_preview_button(mock_generate_cloud, mock_aedt_app, patch_graphics_modules):
    """Test call to pyvista plotter after clicking on "Preview" button."""

    extension = PointsCloudExtension(withdraw=True)
    extension.objects_list_lb.selection_set(1)
    extension.root.nametowidget("preview").invoke()

    patch_graphics_modules["pyvista"].Plotter().show.assert_called_once()


def test_point_cloud_extension_exceptions(mock_aedt_app):
    """Test exceptions thrown by the point cloud extension."""

    mock_aedt_app.modeler.get_objects_in_group.return_value = []

    with pytest.raises(AEDTRuntimeError):
        extension = PointsCloudExtension(withdraw=True)

    mock_aedt_app.modeler.get_objects_in_group.return_value = ["dummy_solid"]
    extension = PointsCloudExtension(withdraw=True)

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    extension = PointsCloudExtension(withdraw=True)
    extension.objects_list_lb.selection_set(1)
    extension.points_entry.delete("1.0", tkinter.END)
    extension.points_entry.insert(tkinter.END, "0")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    extension = PointsCloudExtension(withdraw=True)
    extension.objects_list_lb.selection_set(1)
    extension.output_file_entry.insert(tkinter.END, str(Path(__file__))[1:])

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()
