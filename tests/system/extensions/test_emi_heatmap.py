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

import pytest

from ansys.aedt.core.generic.general_methods import is_linux
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"

# Define skip conditions at module level
SKIP_EMIT_PYTHON_VERSION = (
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1"
) or ((sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2")

# Apply markers to all tests in this module
pytestmark = [
    pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux."),
    pytest.mark.skipif(
        SKIP_EMIT_PYTHON_VERSION,
        reason="Emit API version mismatch with Python version for this AEDT release.",
    ),
]

# Conditional import
if not SKIP_EMIT_PYTHON_VERSION:
    from ansys.aedt.core import Emit
    from ansys.aedt.core.extensions.emit.emi_heatmap import EMIHeatmapExtension
    from ansys.aedt.core.extensions.emit.emi_heatmap import EMIHeatmapExtensionData


@pytest.fixture
def emit_app_with_radios(add_app_example):
    """Load the interference example to test the extension."""
    app = add_app_example(project="interference", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def test_extension_initialization(emit_app_with_radios):
    """Test that extension initializes correctly with an active EMIT design."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Verify extension properties
    assert extension.root.title() == "EMIT EMI Heatmap"
    assert extension.active_design_name == emit_app_with_radios.design_name
    assert extension.active_project_name == emit_app_with_radios.project_name
    assert extension.aedt_application.design_type == "EMIT"

    extension.root.destroy()


def test_get_radios_from_project(emit_app_with_radios):
    """Test getting aggressor and victim radios from the project."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Get radios should populate aggressors and victims
    extension._get_radios()

    assert extension._revision is not None
    assert extension._domain is not None
    assert len(extension._aggressors) > 0
    assert len(extension._victims) > 0

    extension.root.destroy()


def test_populate_dropdowns_with_real_data(emit_app_with_radios):
    """Test populating dropdowns with real project data."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Dropdowns should be populated during initialization
    victim_values = extension._victim_combo["values"]
    aggressor_values = extension._aggressor_combo["values"]

    assert len(victim_values) > 0
    assert len(aggressor_values) > 0

    extension.root.destroy()


def test_victim_selection_changes(emit_app_with_radios):
    """Test changing victim radio selection."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Get available victims
    victims = extension._victim_combo["values"]
    if len(victims) > 1:
        # Select different victim
        extension._victim_combo.set(victims[1])
        extension._on_victim_changed()

        assert extension._victim == victims[1]
        # Band combo should be populated
        assert len(extension._victim_band_combo["values"]) > 0

    extension.root.destroy()


def test_aggressor_selection_changes(emit_app_with_radios):
    """Test changing aggressor radio selection."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Get available aggressors
    aggressors = extension._aggressor_combo["values"]
    if len(aggressors) > 0:
        # Select aggressor
        extension._aggressor_combo.set(aggressors[0])
        extension._on_aggressor_changed()

        assert extension._aggressor == aggressors[0]
        # Band combo should be populated
        assert len(extension._aggressor_band_combo["values"]) > 0

    extension.root.destroy()


def test_extract_emi_data(emit_app_with_radios):
    """Test extracting EMI data from the project."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Ensure selections are made
    if extension._victim and extension._aggressor:
        # Extract data
        extension._extract_data()

        # Verify data was extracted
        assert extension._emi is not None
        assert len(extension._emi) > 0
        assert extension._rx_power is not None
        assert extension._desense is not None
        assert extension._sensitivity is not None

    extension.root.destroy()


def test_export_to_csv(emit_app_with_radios, test_tmp_dir):
    """Test exporting EMI data to CSV file."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Extract data first
    extension._extract_data()

    # Set up file path
    csv_path = test_tmp_dir / "emi_results.csv"

    # Format and save CSV
    extension._format_csv(str(csv_path))

    # Verify file was created
    assert csv_path.exists()
    assert csv_path.suffix == ".csv"
    assert csv_path.stat().st_size > 0

    # Verify CSV content
    with open(csv_path, "r") as f:
        content = f.read()
        assert "Aggressor_Radio" in content
        assert "Victim_Radio" in content
        assert "EMI" in content

    extension.root.destroy()


@patch("matplotlib.pyplot.show")
def test_generate_heatmap_plot(mock_show, emit_app_with_radios):
    """Test generating heatmap plot with real data."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Extract data
    extension._extract_data()

    # Generate heatmap
    extension._on_generate_heatmap()

    # Verify plot was created
    assert mock_show.called

    extension.root.destroy()


@patch("matplotlib.pyplot.show")
def test_heatmap_with_custom_thresholds(mock_show, emit_app_with_radios):
    """Test heatmap generation with custom threshold values."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Extract data
    extension._extract_data()

    # Generate heatmap with custom thresholds
    if extension._emi:
        extension._plot_matrix_heatmap(red_threshold=5.0, yellow_threshold=-5.0)
        assert mock_show.called

    extension.root.destroy()


def test_emi_heatmap_extension_data_class():
    """Test EMIHeatmapExtensionData dataclass."""
    import numpy as np

    data = EMIHeatmapExtensionData(
        emi=np.array([[1, 2], [3, 4]]),
        rx_power=np.array([[5, 6], [7, 8]]),
        sensitivity=np.array([[9, 10], [11, 12]]),
        desense=np.array([[13, 14], [15, 16]]),
        victim="TestVictim",
        victim_band="TestVictimBand",
        aggressor="TestAggressor",
        aggressor_band="TestAggressorBand",
    )

    assert data.victim == "TestVictim"
    assert data.aggressor == "TestAggressor"
    assert np.array_equal(data.emi, np.array([[1, 2], [3, 4]]))


def test_band_selection_workflow(emit_app_with_radios):
    """Test complete workflow of selecting victim and aggressor bands."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Verify initial state
    assert extension._victim is not None
    assert extension._aggressor is not None

    # Change victim band
    victim_bands = extension._victim_band_combo["values"]
    if len(victim_bands) > 0:
        extension._victim_band_combo.set(victim_bands[0])
        extension._on_victim_band_changed()
        assert extension._victim_band == victim_bands[0]

    # Change aggressor band
    aggressor_bands = extension._aggressor_band_combo["values"]
    if len(aggressor_bands) > 0:
        extension._aggressor_band_combo.set(aggressor_bands[0])
        extension._on_aggressor_band_changed()
        assert extension._aggressor_band == aggressor_bands[0]

    extension.root.destroy()


@patch("tkinter.filedialog.asksaveasfilename")
@patch("tkinter.messagebox.showinfo")
def test_csv_export_workflow(mock_info, mock_filedialog, emit_app_with_radios, test_tmp_dir):
    """Test complete CSV export workflow."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Extract data first
    extension._extract_data()

    # Set up file path
    csv_path = test_tmp_dir / "emi_export.csv"
    mock_filedialog.return_value = str(csv_path)

    # Trigger export
    extension._on_export_csv()

    # Verify file was created and info message shown
    assert csv_path.exists()
    assert mock_info.called

    extension.root.destroy()


@patch("matplotlib.pyplot.show")
def test_heatmap_colorbar_labels(mock_show, emit_app_with_radios):
    """Test that heatmap colorbar displays correct labels."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Extract data
    extension._extract_data()

    # Generate heatmap
    if extension._emi:
        extension._plot_matrix_heatmap(red_threshold=0.0, yellow_threshold=-10.0)

        # Verify matplotlib show was called
        assert mock_show.called

    extension.root.destroy()
