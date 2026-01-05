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

import shutil

import pytest

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import ViaClusteringExtension
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import ViaClusteringExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.via_clustering import main
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_EXTENSIONS_PATH


@pytest.mark.flaky_linux
def test_via_clustering_main_function(test_tmp_dir):
    """Test the main function of the Via Clustering extension."""
    # Copy test model to scratch directory
    file_path = test_tmp_dir / "test_via_merging.aedb"
    new_file = test_tmp_dir / "new_test_via_merging.aedb"

    original_file = TESTS_EXTENSIONS_PATH / "example_models" / "T45" / "test_via_merging.aedb"
    shutil.copytree(original_file, file_path)

    # Create test data following the reference pattern
    data = ViaClusteringExtensionData(
        aedb_path=str(file_path),
        design_name="test",
        new_aedb_path=str(new_file),
        start_layer="TOP",
        stop_layer="INT5",
        contour_list=[
            [
                [0.143, 0.04],
                [0.1476, 0.04],
                [0.1476, 0.03618],
                [0.143, 0.036],
            ]
        ],
    )

    # Test the main function
    assert main(data)

    # Verify the new AEDB file was created
    assert new_file.exists()


@pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
def test_via_clustering_extension_ui(add_app_example):
    """Test the Via Clustering extension UI components."""
    # Create an HFSS 3D Layout application for testing
    hfss3d = add_app_example(
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / "T45",
        application=Hfss3dLayout,
        project="test_via_merging",
        is_edb=True,
    )
    hfss3d.save_project()

    # Initialize the extension (withdraw=True to avoid showing UI)
    extension = ViaClusteringExtension(withdraw=True)

    # Test that the extension initialized correctly
    assert extension is not None
    assert hasattr(extension, "data")

    # Test widget access
    assert extension._widgets["project_name_entry"] is not None
    assert extension._widgets["start_layer_combo"] is not None
    assert extension._widgets["stop_layer_combo"] is not None

    # Test that layers were loaded
    assert extension._ViaClusteringExtension__layers is not None
    assert len(extension._ViaClusteringExtension__layers) > 0

    # Test that project info was loaded
    assert extension._ViaClusteringExtension__active_project_name is not None
    assert extension._ViaClusteringExtension__active_project_path is not None
    assert extension._ViaClusteringExtension__aedb_path is not None

    hfss3d.close_project(save=False)


def test_via_clustering_exceptions():
    """Test exceptions thrown by the Via Clustering extension."""
    # Test missing AEDB path
    data = ViaClusteringExtensionData(aedb_path="", design_name="test", new_aedb_path="new_test")
    with pytest.raises(AEDTRuntimeError, match="No AEDB path provided"):
        main(data)

    # Test missing design name
    data = ViaClusteringExtensionData(
        aedb_path="test.aedb",
        design_name="",
        new_aedb_path="new_test",
    )
    with pytest.raises(AEDTRuntimeError, match="No design name provided"):
        main(data)

    # Test missing new AEDB path
    data = ViaClusteringExtensionData(aedb_path="test.aedb", design_name="test", new_aedb_path="")
    with pytest.raises(AEDTRuntimeError, match="No new AEDB path provided"):
        main(data)


@pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
def test_via_clustering_button_functions(add_app_example):
    """Test the button functions in the Via Clustering extension."""
    # Copy the test model to scratch directory
    hfss3d = add_app_example(
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / "T45",
        application=Hfss3dLayout,
        project="test_via_merging",
        is_edb=True,
    )
    hfss3d.save_project()

    # Initialize the extension
    extension = ViaClusteringExtension(withdraw=True)

    # Test add layer button functionality by invoking it
    add_layer_button = extension.root.nametowidget("add_layer")
    assert add_layer_button is not None

    # The button should exist and be clickable
    # (we can't easily test the actual click without mocking)
    assert add_layer_button.winfo_exists()

    # Test merge vias button exists
    merge_vias_button = extension.root.nametowidget("merge_vias")
    assert merge_vias_button is not None
    assert merge_vias_button.winfo_exists()

    # Clean up
    hfss3d.close_project(save=False)


def test_via_clustering_data_class():
    """Test the ViaClusteringExtensionData data class."""
    # Test default initialization
    data = ViaClusteringExtensionData()
    assert data.aedb_path == ""
    assert data.design_name == ""
    assert data.new_aedb_path == ""
    assert data.nets_filter == []
    assert data.start_layer == ""
    assert data.stop_layer == ""
    assert data.contour_list == []

    # Test initialization with parameters
    test_contour = [[0.1, 0.2], [0.3, 0.4]]
    test_nets = ["net1", "net2"]

    data = ViaClusteringExtensionData(
        aedb_path="test.aedb",
        design_name="test_design",
        new_aedb_path="new_test.aedb",
        nets_filter=test_nets,
        start_layer="TOP",
        stop_layer="BOTTOM",
        contour_list=test_contour,
    )

    assert data.aedb_path == "test.aedb"
    assert data.design_name == "test_design"
    assert data.new_aedb_path == "new_test.aedb"
    assert data.nets_filter == test_nets
    assert data.start_layer == "TOP"
    assert data.stop_layer == "BOTTOM"
    assert data.contour_list == test_contour
