# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import tkinter
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import ViaClusteringExtension
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import ViaClusteringExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_hfss_3d_layout_app_with_layers(mock_hfss_3d_layout_app):
    """Fixture to create a mock HFSS 3D Layout application with layers."""
    # Mock desktop and project structure
    mock_desktop = MagicMock()
    mock_project = MagicMock()
    mock_design = MagicMock()

    mock_project.GetPath.return_value = "/test/project/path"
    mock_project.GetName.return_value = "test_project"
    mock_design.GetName.return_value = "layout;test_design"

    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    # Mock EDB with signal layers
    mock_edb = MagicMock()
    mock_stackup = MagicMock()
    mock_stackup.signal_layers = {"layer1": MagicMock(), "layer2": MagicMock(), "layer3": MagicMock()}
    mock_edb.stackup = mock_stackup

    # Mock the extension base class to return our mock desktop
    base_path = "ansys.aedt.core.extensions.hfss3dlayout.via_clustering"
    with patch(f"{base_path}.ExtensionHFSS3DLayoutCommon.desktop", mock_desktop):
        with patch(f"{base_path}.Edb", return_value=mock_edb):
            yield mock_hfss_3d_layout_app


@pytest.fixture
def mock_hfss_3d_layout_app_no_layers(mock_hfss_3d_layout_app):
    """Fixture to create a mock HFSS 3D Layout app with no layers."""
    # Mock desktop and project structure
    mock_desktop = MagicMock()
    mock_project = MagicMock()
    mock_design = MagicMock()

    mock_project.GetPath.return_value = "/test/project/path"
    mock_project.GetName.return_value = "test_project"
    mock_design.GetName.return_value = "layout;test_design"

    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    # Mock EDB with no signal layers
    mock_edb = MagicMock()
    mock_stackup = MagicMock()
    mock_stackup.signal_layers = {}
    mock_edb.stackup = mock_stackup

    # Mock the extension base class to return our mock desktop
    base_path = "ansys.aedt.core.extensions.hfss3dlayout.via_clustering"
    with patch(f"{base_path}.ExtensionHFSS3DLayoutCommon.desktop", mock_desktop):
        with patch(f"{base_path}.Edb", return_value=mock_edb):
            yield mock_hfss_3d_layout_app


def test_via_clustering_extension_data_post_init() -> None:
    """Test ViaClusteringExtensionData __post_init__ method."""
    # Test with None values
    data = ViaClusteringExtensionData()
    assert data.nets_filter == []
    assert data.contour_list == []

    # Test with existing values
    data = ViaClusteringExtensionData(nets_filter=["net1"], contour_list=[[[0, 0], [1, 1]]])
    assert data.nets_filter == ["net1"]
    assert data.contour_list == [[[0, 0], [1, 1]]]


def test_via_clustering_extension_default(mock_hfss_3d_layout_app_with_layers) -> None:
    """Test instantiation of the Via Clustering extension."""
    extension = ViaClusteringExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_via_clustering_extension_no_layers_exception(mock_hfss_3d_layout_app_no_layers) -> None:
    """Test exception when no signal layers are defined."""
    with pytest.raises(AEDTRuntimeError, match="No signal layers are defined in this design."):
        ViaClusteringExtension(withdraw=True)


def test_via_clustering_extension_ui_elements(mock_hfss_3d_layout_app_with_layers) -> None:
    """Test that all UI elements are created correctly."""
    extension = ViaClusteringExtension(withdraw=True)

    # Check that widgets are created and stored
    assert "project_label" in extension._widgets
    assert "project_name_entry" in extension._widgets
    assert "label_start_layer" in extension._widgets
    assert "start_layer_combo" in extension._widgets
    assert "label_stop_layer" in extension._widgets
    assert "stop_layer_combo" in extension._widgets
    assert "button_add_layer" in extension._widgets
    assert "button_merge_vias" in extension._widgets

    # Check initial values
    assert extension.start_layer_var.get() == "layer1"  # First layer
    assert extension.stop_layer_var.get() == "layer3"  # Last layer

    # Check project name entry has default value
    project_name = extension.project_name_entry.get("1.0", tkinter.END).strip()
    assert "test_project" in project_name

    extension.root.destroy()


def test_via_clustering_extension_add_layer_button(mock_hfss_3d_layout_app_with_layers) -> None:
    """Test the add layer button functionality."""
    extension = ViaClusteringExtension(withdraw=True)

    # Mock Hfss3dLayout for the add_drawing_layer function
    mock_hfss = MagicMock()
    mock_layer = MagicMock()
    mock_stackup = MagicMock()
    mock_stackup.add_layer.return_value = mock_layer
    mock_modeler = MagicMock()
    mock_modeler.stackup = mock_stackup
    mock_hfss.modeler = mock_modeler

    base_path = "ansys.aedt.core.extensions.hfss3dlayout.via_clustering"
    with patch(f"{base_path}.Hfss3dLayout", return_value=mock_hfss):
        # Click the add layer button
        extension.root.nametowidget("add_layer").invoke()

        # Verify that add_layer was called with correct name
        mock_stackup.add_layer.assert_called_once_with("via_merging")
        # Verify that usp was set to True
        assert mock_layer.usp is True
        # Verify desktop was released
        mock_hfss.desktop_class.release_desktop.assert_called_once_with(False, False)

    extension.root.destroy()


def test_via_clustering_extension_merge_vias_button_with_primitives(mock_hfss_3d_layout_app_with_layers) -> None:
    """Test the merge vias button functionality with valid primitives."""
    extension = ViaClusteringExtension(withdraw=True)

    # Mock primitives
    mock_primitive1 = MagicMock()
    mock_primitive1.prim_type = "poly"
    mock_primitive1.name = "poly1"
    mock_point1 = MagicMock()
    mock_point1.position = [0, 0]
    mock_point2 = MagicMock()
    mock_point2.position = [1, 1]
    mock_primitive1.points = [mock_point1, mock_point2]

    mock_primitive2 = MagicMock()
    mock_primitive2.prim_type = "rect"
    mock_primitive2.name = "rect1"
    mock_point3 = MagicMock()
    mock_point3.position = [2, 2]
    mock_point4 = MagicMock()
    mock_point4.position = [3, 3]
    mock_primitive2.points = [mock_point3, mock_point4]

    # Mock Hfss3dLayout
    mock_hfss = MagicMock()
    mock_modeler = MagicMock()
    mock_modeler.objects_by_layer.return_value = ["primitive1", "primitive2"]
    mock_modeler.geometries = {"primitive1": mock_primitive1, "primitive2": mock_primitive2}
    mock_hfss.modeler = mock_modeler

    base_path = "ansys.aedt.core.extensions.hfss3dlayout.via_clustering"
    with patch(f"{base_path}.Hfss3dLayout", return_value=mock_hfss):
        # Click the merge vias button
        extension.root.nametowidget("merge_vias").invoke()

        # Verify project was saved
        mock_hfss.save_project.assert_called_once()

        # Verify that data was set correctly
        assert extension.data is not None
        assert extension.data.start_layer == "layer1"
        assert extension.data.stop_layer == "layer3"
        assert len(extension.data.contour_list) == 2
        expected_contours = [[[0, 0], [1, 1]], [[2, 2], [3, 3]]]
        assert extension.data.contour_list == expected_contours

        # Verify desktop was released
        mock_hfss.desktop_class.release_desktop.assert_called_once_with(False, False)


def test_via_clustering_extension_merge_vias_unsupported_primitive(mock_hfss_3d_layout_app_with_layers) -> None:
    """Test merge vias with unsupported primitive type."""
    extension = ViaClusteringExtension(withdraw=True)

    # Mock primitive with unsupported type
    mock_primitive = MagicMock()
    mock_primitive.prim_type = "circle"  # Unsupported type
    mock_primitive.name = "circle1"

    # Mock Hfss3dLayout
    mock_hfss = MagicMock()
    mock_logger = MagicMock()
    mock_hfss.logger = mock_logger
    mock_modeler = MagicMock()
    mock_modeler.objects_by_layer.return_value = ["primitive1"]
    mock_modeler.geometries = {"primitive1": mock_primitive}
    mock_hfss.modeler = mock_modeler

    base_path = "ansys.aedt.core.extensions.hfss3dlayout.via_clustering"
    with patch(f"{base_path}.Hfss3dLayout", return_value=mock_hfss):
        # Click the merge vias button
        extension.root.nametowidget("merge_vias").invoke()

        # Verify warning was logged
        mock_logger.warning.assert_called_once()

        # Verify that data was still set (but with empty contour list)
        assert extension.data is not None
        assert extension.data.contour_list == []


def test_main_function_exceptions() -> None:
    """Test exceptions in the main function."""
    # Test with no AEDB path
    data = ViaClusteringExtensionData(aedb_path="")
    with pytest.raises(AEDTRuntimeError, match="No AEDB path provided to the extension."):
        main(data)

    # Test with no design name
    data = ViaClusteringExtensionData(aedb_path="/test/path", design_name="")
    with pytest.raises(AEDTRuntimeError, match="No design name provided to the extension."):
        main(data)

    # Test with no new AEDB path
    data = ViaClusteringExtensionData(aedb_path="/test/path", design_name="test_design", new_aedb_path="")
    with pytest.raises(AEDTRuntimeError, match="No new AEDB path provided to the extension."):
        main(data)


def test_main_function_success() -> None:
    """Test successful execution of the main function."""
    # Create test data
    data = ViaClusteringExtensionData(
        aedb_path="/test/original.aedb",
        design_name="test_design",
        new_aedb_path="/test/new.aedb",
        start_layer="layer1",
        stop_layer="layer3",
        contour_list=[[[0, 0], [1, 1]], [[2, 2], [3, 3]]],
    )

    # Mock shutil.copytree
    base_path = "ansys.aedt.core.extensions.hfss3dlayout.via_clustering"
    with patch(f"{base_path}.shutil.copytree"):
        # Mock EDB
        mock_edb = MagicMock()
        mock_padstacks = MagicMock()
        mock_edb.padstacks = mock_padstacks
        mock_modeler = MagicMock()
        mock_modeler.primitives_by_layer = {"via_merging": [MagicMock(), MagicMock()]}
        mock_edb.modeler = mock_modeler

        with patch(f"{base_path}.Edb", return_value=mock_edb):
            # Set environment variable to avoid HFSS 3D Layout instantiation
            with patch.dict(os.environ, {"PYTEST_CURRENT_TEST": "test"}):
                result = main(data)

                # Verify the result
                assert result is True

                # Verify EDB operations
                mock_padstacks.merge_via.assert_called_once_with(
                    contour_boxes=[[[0, 0], [1, 1]], [[2, 2], [3, 3]]],
                    net_filter=None,
                    start_layer="layer1",
                    stop_layer="layer3",
                )

                # Verify primitives were deleted
                for prim in mock_modeler.primitives_by_layer["via_merging"]:
                    prim.delete.assert_called_once()

                # Verify EDB was saved and closed
                mock_edb.save.assert_called_once()
                mock_edb.close.assert_called_once()


def test_main_function_without_pytest_env() -> None:
    """Test main function behavior when not running in pytest environment."""
    # Create test data
    data = ViaClusteringExtensionData(
        aedb_path="/test/original.aedb",
        design_name="test_design",
        new_aedb_path="/test/new.aedb",
        start_layer="layer1",
        stop_layer="layer3",
        contour_list=[],
    )

    # Mock shutil.copytree
    base_path = "ansys.aedt.core.extensions.hfss3dlayout.via_clustering"
    with patch(f"{base_path}.shutil.copytree"):
        # Mock EDB
        mock_edb = MagicMock()
        mock_padstacks = MagicMock()
        mock_edb.padstacks = mock_padstacks
        mock_modeler = MagicMock()
        mock_modeler.primitives_by_layer = {"via_merging": []}
        mock_edb.modeler = mock_modeler

        # Mock Hfss3dLayout
        mock_h3d = MagicMock()
        mock_logger = MagicMock()
        mock_h3d.logger = mock_logger

        with patch(f"{base_path}.Edb", return_value=mock_edb):
            with patch(f"{base_path}.Hfss3dLayout", return_value=mock_h3d):
                # Ensure PYTEST_CURRENT_TEST is not in environment
                env = os.environ.copy()
                if "PYTEST_CURRENT_TEST" in env:
                    del env["PYTEST_CURRENT_TEST"]

                with patch.dict(os.environ, env, clear=True):
                    result = main(data)

                    # Verify the result
                    assert result is True

                    # Verify HFSS 3D Layout was instantiated and used
                    mock_logger.info.assert_called_once_with("Project generated correctly.")
                    mock_h3d.desktop_class.release_desktop.assert_called_once_with(False, False)


def test_via_clustering_extension_wrong_design_type() -> None:
    """Test exception when design type is not HFSS 3D Layout."""
    mock_app = MagicMock()
    mock_app.design_type = "HFSS"

    from ansys.aedt.core.extensions.misc import ExtensionCommon

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_property:
        mock_property.return_value = mock_app

        with pytest.raises(AEDTRuntimeError):
            ViaClusteringExtension(withdraw=True)


def test_via_clustering_extension_layer_selection_change(mock_hfss_3d_layout_app_with_layers) -> None:
    """Test changing layer selections in the UI."""
    extension = ViaClusteringExtension(withdraw=True)

    # Change start layer variable
    extension.start_layer_var.set("layer2")
    assert extension.start_layer_var.get() == "layer2"

    # Change stop layer variable
    extension.stop_layer_var.set("layer1")
    assert extension.stop_layer_var.get() == "layer1"

    extension.root.destroy()


def test_via_clustering_extension_project_name_change(mock_hfss_3d_layout_app_with_layers) -> None:
    """Test changing project name in the UI."""
    extension = ViaClusteringExtension(withdraw=True)

    # Clear and set new project name
    extension.project_name_entry.delete("1.0", tkinter.END)
    extension.project_name_entry.insert(tkinter.END, "custom_project_name")

    project_name = extension.project_name_entry.get("1.0", tkinter.END).strip()
    assert project_name == "custom_project_name"

    extension.root.destroy()
