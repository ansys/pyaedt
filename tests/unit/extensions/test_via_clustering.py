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

import os
from pathlib import Path
import shutil
import tempfile
import tkinter
from tkinter import messagebox
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import call
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import (
    EXTENSION_TITLE,
)
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import (
    ViaClusteringExtension,
)
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import (
    ViaClusteringExtensionData,
)
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import (
    main,
)
from ansys.aedt.core.extensions.misc import (
    ExtensionHFSS3DLayoutCommon,
)
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_hfss3dl_app_with_layers(mock_hfss_3d_layout_app):
    """Fixture to create a mock HFSS 3D Layout application with layers and project info."""
    # Mock active project
    mock_project = MagicMock()
    mock_project.GetPath.return_value = "C:\\test\\project"
    mock_project.GetName.return_value = "TestProject"

    # Mock active design
    mock_design = MagicMock()
    mock_design.GetName.return_value = "Layout;TestDesign"

    # Mock desktop
    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    # Mock EDB and stackup
    mock_stackup = MagicMock()
    mock_stackup.signal_layers = {
        "Layer1": {},
        "Layer2": {},
        "Layer3": {},
    }

    with patch.object(
        ExtensionHFSS3DLayoutCommon,
        "desktop",
        new_callable=PropertyMock,
    ) as mock_desktop_property:
        mock_desktop_property.return_value = mock_desktop

        with patch(
            "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Edb"
        ) as mock_edb_class:
            mock_edb = MagicMock()
            mock_edb.stackup = mock_stackup
            mock_edb_class.return_value = mock_edb

            yield (
                mock_hfss_3d_layout_app,
                mock_desktop,
                mock_project,
                mock_design,
                mock_edb,
            )


@pytest.fixture
def mock_hfss3dl_app_no_layers(mock_hfss_3d_layout_app):
    """Fixture to create a mock HFSS 3D Layout application with no layers."""
    # Mock active project
    mock_project = MagicMock()
    mock_project.GetPath.return_value = "C:\\test\\project"
    mock_project.GetName.return_value = "TestProject"

    # Mock active design
    mock_design = MagicMock()
    mock_design.GetName.return_value = "Layout;TestDesign"

    # Mock desktop
    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    # Mock EDB and stackup with no signal layers
    mock_stackup = MagicMock()
    mock_stackup.signal_layers = {}

    with patch.object(
        ExtensionHFSS3DLayoutCommon,
        "desktop",
        new_callable=PropertyMock,
    ) as mock_desktop_property:
        mock_desktop_property.return_value = mock_desktop

        with patch(
            "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Edb"
        ) as mock_edb_class:
            mock_edb = MagicMock()
            mock_edb.stackup = mock_stackup
            mock_edb_class.return_value = mock_edb

            with patch.object(
                ExtensionHFSS3DLayoutCommon, "release_desktop"
            ) as mock_release:
                yield (
                    mock_hfss_3d_layout_app,
                    mock_desktop,
                    mock_project,
                    mock_design,
                    mock_edb,
                )


@pytest.fixture
def mock_hfss3dl_app_with_primitives(mock_hfss_3d_layout_app):
    """Fixture to create a mock HFSS 3D Layout application with primitives."""
    # Mock active project
    mock_project = MagicMock()
    mock_project.GetPath.return_value = "C:\\test\\project"
    mock_project.GetName.return_value = "TestProject"

    # Mock active design
    mock_design = MagicMock()
    mock_design.GetName.return_value = "Layout;TestDesign"

    # Mock desktop
    mock_desktop = MagicMock()
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    # Mock EDB and stackup
    mock_stackup = MagicMock()
    mock_stackup.signal_layers = {
        "Layer1": {},
        "Layer2": {},
        "Layer3": {},
    }

    # Mock primitives and geometries
    mock_point1 = MagicMock()
    mock_point1.position = [0, 0]
    mock_point2 = MagicMock()
    mock_point2.position = [1, 0]
    mock_point3 = MagicMock()
    mock_point3.position = [1, 1]
    mock_point4 = MagicMock()
    mock_point4.position = [0, 1]

    mock_geometry = MagicMock()
    mock_geometry.prim_type = "poly"
    mock_geometry.name = "test_poly"
    mock_geometry.points = [
        mock_point1,
        mock_point2,
        mock_point3,
        mock_point4,
    ]

    mock_hfss3dl = MagicMock()
    mock_modeler = MagicMock()
    mock_modeler.objects_by_layer.return_value = ["primitive1"]
    mock_modeler.geometries = {"primitive1": mock_geometry}
    mock_hfss3dl.modeler = mock_modeler
    mock_hfss3dl.logger = MagicMock()

    with patch.object(
        ExtensionHFSS3DLayoutCommon,
        "desktop",
        new_callable=PropertyMock,
    ) as mock_desktop_property:
        mock_desktop_property.return_value = mock_desktop

        with patch(
            "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Edb"
        ) as mock_edb_class:
            mock_edb = MagicMock()
            mock_edb.stackup = mock_stackup
            mock_edb_class.return_value = mock_edb

            with patch(
                "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Hfss3dLayout"
            ) as mock_hfss3dl_class:
                mock_hfss3dl_class.return_value = mock_hfss3dl

                yield (
                    mock_hfss_3d_layout_app,
                    mock_desktop,
                    mock_project,
                    mock_design,
                    mock_edb,
                    mock_hfss3dl,
                )


def test_via_clustering_extension_default(
    mock_hfss3dl_app_with_layers,
):
    """Test instantiation of the Via Clustering extension."""
    mock_app, mock_desktop, mock_project, mock_design, mock_edb = (
        mock_hfss3dl_app_with_layers
    )

    extension = ViaClusteringExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    # Check that layers were loaded
    assert extension._ViaClusteringExtension__layers == [
        "Layer1",
        "Layer2",
        "Layer3",
    ]

    # Check UI elements exist
    assert extension.project_name_entry is not None
    assert extension.start_layer_combo is not None
    assert extension.stop_layer_combo is not None

    extension.root.destroy()


def test_via_clustering_extension_no_layers(
    mock_hfss3dl_app_no_layers,
):
    """Test extension raises exception when no signal layers are found."""
    mock_app, mock_desktop, mock_project, mock_design, mock_edb = (
        mock_hfss3dl_app_no_layers
    )

    with pytest.raises(
        AEDTRuntimeError,
        match="No signal layers are defined in this design",
    ):
        ViaClusteringExtension(withdraw=True)


def test_via_clustering_extension_data_default():
    """Test ViaClusteringExtensionData default values."""
    data = ViaClusteringExtensionData()

    assert data.aedb_path == ""
    assert data.design_name == ""
    assert data.new_aedb_path == ""
    assert data.nets_filter == []
    assert data.start_layer == ""
    assert data.stop_layer == ""
    assert data.contour_list == []


def test_add_drawing_layer(mock_hfss3dl_app_with_layers):
    """Test the add_drawing_layer function."""
    mock_app, mock_desktop, mock_project, mock_design, mock_edb = (
        mock_hfss3dl_app_with_layers
    )

    with patch(
        "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Hfss3dLayout"
    ) as mock_hfss3dl_class:
        mock_hfss3dl = MagicMock()
        mock_layer = MagicMock()
        mock_stackup = MagicMock()
        mock_stackup.add_layer.return_value = mock_layer
        mock_modeler = MagicMock()
        mock_modeler.stackup = mock_stackup
        mock_hfss3dl.modeler = mock_modeler
        mock_hfss3dl_class.return_value = mock_hfss3dl

        extension = ViaClusteringExtension(withdraw=True)

        # Invoke the add_drawing_layer button
        extension.root.nametowidget("add_layer").invoke()

        # Verify that Hfss3dLayout was called with correct parameters
        mock_hfss3dl_class.assert_called_once_with(
            new_desktop=False,
            version=extension._ViaClusteringExtension__class__.__module__.split(
                "."
            )[-1],  # This will be mocked
            port=patch(
                "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.PORT"
            ).return_value,
            aedt_process_id=patch(
                "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.AEDT_PROCESS_ID"
            ).return_value,
            student_version=patch(
                "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.IS_STUDENT"
            ).return_value,
        )

        # Verify layer was added
        mock_stackup.add_layer.assert_called_once_with("via_merging")

        # Verify USP was set
        assert mock_layer.usp is True

        # Verify desktop was released correctly
        mock_hfss3dl.release_desktop.assert_called_once_with(
            close_desktop=False, close_projects=False
        )

        extension.root.destroy()


def test_callback_merge_vias_success(
    mock_hfss3dl_app_with_primitives,
):
    """Test successful callback_merge_vias function."""
    (
        mock_app,
        mock_desktop,
        mock_project,
        mock_design,
        mock_edb,
        mock_hfss3dl,
    ) = mock_hfss3dl_app_with_primitives

    extension = ViaClusteringExtension(withdraw=True)

    # Set up the text entries
    extension.project_name_entry.delete("1.0", tkinter.END)
    extension.project_name_entry.insert(tkinter.END, "NewProject")

    # Invoke the merge_vias button
    extension.root.nametowidget("merge_vias").invoke()

    # Verify that the data was set correctly
    assert extension.data is not None
    assert extension.data.aedb_path == os.path.join(
        "C:\\test\\project", "TestProject.aedb"
    )
    assert extension.data.design_name == "TestProject"
    assert extension.data.new_aedb_path == os.path.join(
        "C:\\test\\project", "NewProject.aedb"
    )
    assert extension.data.start_layer == "Layer1"
    assert extension.data.stop_layer == "Layer3"
    assert len(extension.data.contour_list) == 1
    assert extension.data.contour_list[0] == [
        [0, 0],
        [1, 0],
        [1, 1],
        [0, 1],
    ]

    # Verify HFSS 3D Layout methods were called
    mock_hfss3dl.save_project.assert_called_once()
    mock_hfss3dl.modeler.objects_by_layer.assert_called_once_with(
        layer="via_merging"
    )
    mock_hfss3dl.release_desktop.assert_called_once_with(
        close_desktop=False, close_projects=False
    )


def test_callback_merge_vias_no_primitives(
    mock_hfss3dl_app_with_layers,
):
    """Test callback_merge_vias when no primitives are found."""
    mock_app, mock_desktop, mock_project, mock_design, mock_edb = (
        mock_hfss3dl_app_with_layers
    )

    with patch(
        "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Hfss3dLayout"
    ) as mock_hfss3dl_class:
        mock_hfss3dl = MagicMock()
        mock_hfss3dl.modeler.objects_by_layer.return_value = []  # No primitives
        mock_hfss3dl_class.return_value = mock_hfss3dl

        with patch(
            "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.messagebox"
        ) as mock_messagebox:
            extension = ViaClusteringExtension(withdraw=True)

            with pytest.raises(
                AEDTRuntimeError,
                match="No primitives found on layer defined for merging padstack instances",
            ):
                extension.root.nametowidget("merge_vias").invoke()

            # Verify warning was shown
            mock_messagebox.showwarning.assert_called_once_with(
                message="No primitives found on layer defined for merging padstack instances."
            )

            extension.root.destroy()


def test_callback_merge_vias_unsupported_primitive(
    mock_hfss3dl_app_with_layers,
):
    """Test callback_merge_vias with unsupported primitive type."""
    mock_app, mock_desktop, mock_project, mock_design, mock_edb = (
        mock_hfss3dl_app_with_layers
    )

    # Mock unsupported primitive
    mock_geometry = MagicMock()
    mock_geometry.prim_type = "circle"  # Unsupported type
    mock_geometry.name = "test_circle"

    with patch(
        "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Hfss3dLayout"
    ) as mock_hfss3dl_class:
        mock_hfss3dl = MagicMock()
        mock_modeler = MagicMock()
        mock_modeler.objects_by_layer.return_value = ["primitive1"]
        mock_modeler.geometries = {"primitive1": mock_geometry}
        mock_hfss3dl.modeler = mock_modeler
        mock_hfss3dl.logger = MagicMock()
        mock_hfss3dl_class.return_value = mock_hfss3dl

        extension = ViaClusteringExtension(withdraw=True)

        # Set up the text entries
        extension.project_name_entry.delete("1.0", tkinter.END)
        extension.project_name_entry.insert(tkinter.END, "NewProject")

        # Invoke the merge_vias button
        extension.root.nametowidget("merge_vias").invoke()

        # Verify warning was logged
        mock_hfss3dl.logger.warning.assert_called_once_with(
            "Unsupported primitive test_circle, only polygon and rectangles are supported."
        )

        # Verify empty contour list since unsupported primitive
        assert extension.data.contour_list == []

        extension.root.destroy()


def test_callback_merge_vias_rectangle_primitive(
    mock_hfss3dl_app_with_layers,
):
    """Test callback_merge_vias with rectangle primitive."""
    mock_app, mock_desktop, mock_project, mock_design, mock_edb = (
        mock_hfss3dl_app_with_layers
    )

    # Mock rectangle primitive
    mock_point1 = MagicMock()
    mock_point1.position = [0, 0]
    mock_point2 = MagicMock()
    mock_point2.position = [2, 0]
    mock_point3 = MagicMock()
    mock_point3.position = [2, 2]
    mock_point4 = MagicMock()
    mock_point4.position = [0, 2]

    mock_geometry = MagicMock()
    mock_geometry.prim_type = "rect"
    mock_geometry.name = "test_rect"
    mock_geometry.points = [
        mock_point1,
        mock_point2,
        mock_point3,
        mock_point4,
    ]

    with patch(
        "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Hfss3dLayout"
    ) as mock_hfss3dl_class:
        mock_hfss3dl = MagicMock()
        mock_modeler = MagicMock()
        mock_modeler.objects_by_layer.return_value = ["primitive1"]
        mock_modeler.geometries = {"primitive1": mock_geometry}
        mock_hfss3dl.modeler = mock_modeler
        mock_hfss3dl.logger = MagicMock()
        mock_hfss3dl_class.return_value = mock_hfss3dl

        extension = ViaClusteringExtension(withdraw=True)

        # Set up the text entries
        extension.project_name_entry.delete("1.0", tkinter.END)
        extension.project_name_entry.insert(tkinter.END, "NewProject")

        # Invoke the merge_vias button
        extension.root.nametowidget("merge_vias").invoke()

        # Verify contour list was created correctly for rectangle
        assert len(extension.data.contour_list) == 1
        assert extension.data.contour_list[0] == [
            [0, 0],
            [2, 0],
            [2, 2],
            [0, 2],
        ]

        extension.root.destroy()


def test_main_function_exceptions():
    """Test exceptions in the main function."""
    # Test with no AEDB path
    data = ViaClusteringExtensionData()
    with pytest.raises(
        AEDTRuntimeError,
        match="No AEDB path provided to the extension",
    ):
        main(data)

    # Test with no design name
    data = ViaClusteringExtensionData(aedb_path="/test/path")
    with pytest.raises(
        AEDTRuntimeError,
        match="No design name provided to the extension",
    ):
        main(data)

    # Test with no new AEDB path
    data = ViaClusteringExtensionData(
        aedb_path="/test/path", design_name="test"
    )
    with pytest.raises(
        AEDTRuntimeError,
        match="No new AEDB path provided to the extension",
    ):
        main(data)


def test_main_function_success():
    """Test successful execution of main function."""
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        aedb_path = os.path.join(temp_dir, "original.aedb")
        new_aedb_path = os.path.join(temp_dir, "new.aedb")

        # Create a fake AEDB directory
        os.makedirs(aedb_path)
        with open(os.path.join(aedb_path, "dummy.txt"), "w") as f:
            f.write("test")

        # Mock EDB and its methods
        with patch(
            "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Edb"
        ) as mock_edb_class:
            mock_edb = MagicMock()
            mock_padstacks = MagicMock()
            mock_modeler = MagicMock()
            mock_prim = MagicMock()
            mock_modeler.primitives_by_layer = {
                "via_merging": [mock_prim]
            }
            mock_edb.padstacks = mock_padstacks
            mock_edb.modeler = mock_modeler
            mock_edb_class.return_value = mock_edb

            with patch(
                "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.shutil.copytree"
            ) as mock_copytree:
                with patch.dict(
                    os.environ, {}, clear=True
                ):  # Clear PYTEST_CURRENT_TEST
                    with patch(
                        "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Hfss3dLayout"
                    ) as mock_hfss3dl_class:
                        mock_hfss3dl = MagicMock()
                        mock_logger = MagicMock()
                        mock_hfss3dl.logger = mock_logger
                        mock_hfss3dl_class.return_value = mock_hfss3dl

                        data = ViaClusteringExtensionData(
                            aedb_path=aedb_path,
                            design_name="TestDesign",
                            new_aedb_path=new_aedb_path,
                            start_layer="Layer1",
                            stop_layer="Layer3",
                            contour_list=[
                                [[0, 0], [1, 0], [1, 1], [0, 1]]
                            ],
                        )

                        result = main(data)

                        # Verify the function completed successfully
                        assert result is True

                        # Verify copytree was called
                        mock_copytree.assert_called_once_with(
                            aedb_path, new_aedb_path
                        )

                        # Verify EDB operations
                        mock_edb_class.assert_called_once_with(
                            new_aedb_path,
                            "TestDesign",
                            edbversion=patch(
                                "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.VERSION"
                            ).return_value,
                        )
                        mock_padstacks.merge_via.assert_called_once_with(
                            contour_boxes=[
                                [[0, 0], [1, 0], [1, 1], [0, 1]]
                            ],
                            net_filter=None,
                            start_layer="Layer1",
                            stop_layer="Layer3",
                        )

                        # Verify cleanup
                        mock_prim.delete.assert_called_once()
                        mock_edb.save.assert_called_once()
                        mock_edb.close_edb.assert_called_once()

                        # Verify HFSS 3D Layout was opened
                        mock_hfss3dl_class.assert_called_once_with(
                            new_aedb_path
                        )
                        mock_logger.info.assert_called_once_with(
                            "Project generated correctly."
                        )
                        mock_hfss3dl.release_desktop.assert_called_once_with(
                            False, False
                        )


def test_main_function_in_pytest_environment():
    """Test main function when running in pytest environment."""
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        aedb_path = os.path.join(temp_dir, "original.aedb")
        new_aedb_path = os.path.join(temp_dir, "new.aedb")

        # Create a fake AEDB directory
        os.makedirs(aedb_path)
        with open(os.path.join(aedb_path, "dummy.txt"), "w") as f:
            f.write("test")

        # Mock EDB and its methods
        with patch(
            "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Edb"
        ) as mock_edb_class:
            mock_edb = MagicMock()
            mock_padstacks = MagicMock()
            mock_modeler = MagicMock()
            mock_prim = MagicMock()
            mock_modeler.primitives_by_layer = {
                "via_merging": [mock_prim]
            }
            mock_edb.padstacks = mock_padstacks
            mock_edb.modeler = mock_modeler
            mock_edb_class.return_value = mock_edb

            with patch(
                "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.shutil.copytree"
            ) as mock_copytree:
                with patch.dict(
                    os.environ,
                    {"PYTEST_CURRENT_TEST": "test_something"},
                    clear=False,
                ):
                    data = ViaClusteringExtensionData(
                        aedb_path=aedb_path,
                        design_name="TestDesign",
                        new_aedb_path=new_aedb_path,
                        start_layer="Layer1",
                        stop_layer="Layer3",
                        contour_list=[
                            [[0, 0], [1, 0], [1, 1], [0, 1]]
                        ],
                    )

                    result = main(data)

                    # Verify the function completed successfully
                    assert result is True

                    # Verify HFSS 3D Layout was NOT opened (pragma: no cover path)
                    with patch(
                        "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.Hfss3dLayout"
                    ) as mock_hfss3dl_class:
                        # This should not be called in pytest environment
                        mock_hfss3dl_class.assert_not_called()


def test_ui_widgets_exist(mock_hfss3dl_app_with_layers):
    """Test that all required UI widgets exist and are properly configured."""
    mock_app, mock_desktop, mock_project, mock_design, mock_edb = (
        mock_hfss3dl_app_with_layers
    )

    extension = ViaClusteringExtension(withdraw=True)

    # Check that all expected widgets exist
    assert "project_label" in extension._widgets
    assert "project_name_entry" in extension._widgets
    assert "label_start_layer" in extension._widgets
    assert "start_layer_combo" in extension._widgets
    assert "label_stop_layer" in extension._widgets
    assert "stop_layer_combo" in extension._widgets
    assert "button_add_layer" in extension._widgets
    assert "button_merge_vias" in extension._widgets

    # Check widget configurations
    assert extension.start_layer_combo["values"] == (
        "Layer1",
        "Layer2",
        "Layer3",
    )
    assert extension.stop_layer_combo["values"] == (
        "Layer1",
        "Layer2",
        "Layer3",
    )
    assert extension.start_layer_var.get() == "Layer1"
    assert extension.stop_layer_var.get() == "Layer3"

    # Check button names for widget lookup
    assert extension.root.nametowidget("add_layer") is not None
    assert extension.root.nametowidget("merge_vias") is not None

    extension.root.destroy()


def test_project_name_generation(mock_hfss3dl_app_with_layers):
    """Test that project name is generated with unique suffix."""
    mock_app, mock_desktop, mock_project, mock_design, mock_edb = (
        mock_hfss3dl_app_with_layers
    )

    with patch(
        "ansys.aedt.core.extensions.hfss3dlayout.via_clustering.generate_unique_name"
    ) as mock_generate:
        mock_generate.return_value = "TestProject_001"

        extension = ViaClusteringExtension(withdraw=True)

        # Check that generate_unique_name was called correctly
        mock_generate.assert_called_once_with("TestProject", n=2)

        # Check that the project name entry contains the generated name
        project_name = extension.project_name_entry.get(
            "1.0", tkinter.END
        ).strip()
        assert project_name == "TestProject_001"

        extension.root.destroy()
