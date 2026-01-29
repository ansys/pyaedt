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

from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from ansys.aedt.core.extensions.emit.emi_heat_map import EMIHeatmapExtension
from ansys.aedt.core.extensions.emit.emi_heat_map import EMIHeatmapExtensionData


@pytest.fixture
def mock_emit_environment():
    """Fixture to set up a mocked EMIT environment for testing."""
    with (
        patch("ansys.aedt.core.extensions.misc.Desktop") as mock_desktop,
        patch("ansys.aedt.core.extensions.misc.active_sessions") as mock_active_sessions,
        patch("ansys.aedt.core.extensions.misc.get_pyaedt_app") as mock_get_pyaedt_app,
    ):
        # Mock desktop and project
        mock_project = MagicMock()
        mock_project.GetName.return_value = "TestProject"

        mock_design = MagicMock()
        mock_design.GetName.return_value = "TestDesign"

        mock_desktop_instance = MagicMock()
        mock_desktop_instance.active_project.return_value = mock_project
        mock_desktop_instance.active_design.return_value = mock_design
        mock_desktop.return_value = mock_desktop_instance
        mock_active_sessions.return_value = {0: 0}

        # Mock AEDT application with EMIT design type
        mock_emit_app = MagicMock()
        mock_emit_app.design_type = "EMIT"
        mock_get_pyaedt_app.return_value = mock_emit_app

        yield {
            "desktop": mock_desktop,
            "desktop_instance": mock_desktop_instance,
            "active_sessions": mock_active_sessions,
            "get_pyaedt_app": mock_get_pyaedt_app,
            "emit_app": mock_emit_app,
            "project": mock_project,
            "design": mock_design,
        }


def test_emi_heatmap_extension_data_class():
    """Test EMIHeatmapExtensionData class."""
    data = EMIHeatmapExtensionData(
        emi=np.array([[1, 2], [3, 4]]),
        rx_power=np.array([[5, 6], [7, 8]]),
        sensitivity=np.array([[9, 10], [11, 12]]),
        desense=np.array([[13, 14], [15, 16]]),
        victim="Radio1",
        victim_band="Band1",
        aggressor="Radio2",
        aggressor_band="Band2",
    )

    assert np.array_equal(data.emi, np.array([[1, 2], [3, 4]]))
    assert np.array_equal(data.rx_power, np.array([[5, 6], [7, 8]]))
    assert data.victim == "Radio1"
    assert data.victim_band == "Band1"
    assert data.aggressor == "Radio2"
    assert data.aggressor_band == "Band2"


def test_emi_heatmap_extension_initialization(mock_emit_environment):
    """Test that extension initializes correctly with an active EMIT design."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Verify extension properties
    assert extension.root.title() == "EMIT EMI Heat Map"
    assert extension.active_design_name == "TestDesign"
    assert extension.active_project_name == "TestProject"
    assert extension.aedt_application.design_type == "EMIT"

    extension.root.destroy()


def test_emi_heatmap_widgets_created(mock_emit_environment):
    """Test that UI widgets are correctly created."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Check that combo boxes exist
    assert hasattr(extension, "_victim_combo")
    assert hasattr(extension, "_victim_band_combo")
    assert hasattr(extension, "_aggressor_combo")
    assert hasattr(extension, "_aggressor_band_combo")

    # Verify combo boxes are configured
    assert extension._victim_combo is not None
    assert extension._aggressor_combo is not None

    extension.root.destroy()


def test_get_radios(mock_emit_environment):
    """Test getting aggressor and victim radios from the project."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()
    mock_domain = MagicMock()

    # Mock radio names
    mock_analyze.get_interferer_names.return_value = ["TxRadio1", "TxRadio2"]
    mock_analyze.get_receiver_names.return_value = ["RxRadio1", "RxRadio2"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = mock_domain
    mock_aedt_app.results = mock_results

    extension = EMIHeatmapExtension(withdraw=True)
    extension._get_radios()

    assert extension._revision == mock_analyze
    assert extension._domain == mock_domain
    assert extension._aggressors == ["TxRadio1", "TxRadio2"]
    assert extension._victims == ["RxRadio1", "RxRadio2"]

    extension.root.destroy()


def test_populate_dropdowns(mock_emit_environment):
    """Test populating victim and aggressor combo boxes."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    mock_analyze.get_interferer_names.return_value = ["TxRadio1", "TxRadio2"]
    mock_analyze.get_receiver_names.return_value = ["RxRadio1", "RxRadio2"]
    mock_analyze.get_band_names.return_value = ["Band1", "Band2"]
    mock_analyze.get_active_frequencies.return_value = ["2400MHz", "2450MHz"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = EMIHeatmapExtension(withdraw=True)

    assert extension._victim_combo.get() == "RxRadio1"
    assert extension._aggressor_combo.get() == "TxRadio1"

    extension.root.destroy()


def test_on_victim_changed(mock_emit_environment):
    """Test handling victim radio selection change."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    mock_analyze.get_interferer_names.return_value = ["TxRadio1"]
    mock_analyze.get_receiver_names.return_value = ["RxRadio1", "RxRadio2"]
    mock_analyze.get_band_names.return_value = ["Band1", "Band2"]
    mock_analyze.get_active_frequencies.return_value = ["2400MHz", "2450MHz"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = EMIHeatmapExtension(withdraw=True)

    # Change victim selection
    extension._victim_combo.set("RxRadio2")
    extension._on_victim_changed()

    assert extension._victim == "RxRadio2"
    assert extension._victim_band_combo["values"] == ("Band1", "Band2")

    extension.root.destroy()


def test_on_victim_band_changed(mock_emit_environment):
    """Test handling victim band selection change."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    mock_analyze.get_interferer_names.return_value = ["TxRadio1"]
    mock_analyze.get_receiver_names.return_value = ["RxRadio1"]
    mock_analyze.get_band_names.return_value = ["Band1", "Band2"]
    mock_analyze.get_active_frequencies.return_value = ["2400MHz", "2450MHz"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim_band_combo.set("Band2")
    extension._on_victim_band_changed()

    assert extension._victim_band == "Band2"
    assert extension._victim_frequencies == ["2400MHz", "2450MHz"]
    assert extension._emi == []

    extension.root.destroy()


def test_on_aggressor_changed(mock_emit_environment):
    """Test handling aggressor radio selection change."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    mock_analyze.get_interferer_names.return_value = ["TxRadio1", "TxRadio2"]
    mock_analyze.get_receiver_names.return_value = ["RxRadio1"]
    mock_analyze.get_band_names.return_value = ["Band1", "Band2"]
    mock_analyze.get_active_frequencies.return_value = ["2400MHz", "2450MHz"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = EMIHeatmapExtension(withdraw=True)

    # Change aggressor selection
    extension._aggressor_combo.set("TxRadio2")
    extension._on_aggressor_changed()

    assert extension._aggressor == "TxRadio2"
    assert extension._aggressor_band_combo["values"] == ("Band1", "Band2")

    extension.root.destroy()


def test_extract_data(mock_emit_environment):
    """Test extracting EMI data for channel combinations."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()
    mock_domain = MagicMock()
    mock_interaction = MagicMock()
    mock_instance = MagicMock()

    # Setup mocks
    mock_analyze.get_interferer_names.return_value = ["TxRadio1"]
    mock_analyze.get_receiver_names.return_value = ["RxRadio1"]
    mock_analyze.get_band_names.return_value = ["Band1"]
    mock_analyze.get_active_frequencies.return_value = ["2400MHz", "2450MHz"]
    mock_analyze.run.return_value = mock_interaction
    mock_analyze.get_license_session.return_value.__enter__ = MagicMock()
    mock_analyze.get_license_session.return_value.__exit__ = MagicMock()

    mock_instance.has_valid_values.return_value = True
    mock_instance.get_value.side_effect = lambda x: -20.0  # EMI, power, etc.
    mock_interaction.get_instance.return_value = mock_instance

    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = mock_domain
    mock_aedt_app.results = mock_results

    extension = EMIHeatmapExtension(withdraw=True)

    # Set up frequencies
    extension._victim_frequencies = ["2400MHz", "2450MHz"]
    extension._aggressor_frequencies = ["2400MHz", "2450MHz"]
    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"

    extension._extract_data()

    # Verify data was extracted
    assert len(extension._emi) == 2  # 2 aggressor frequencies
    assert len(extension._emi[0]) == 2  # 2 victim frequencies
    assert len(extension._rx_power) == 2
    assert len(extension._desense) == 2
    assert len(extension._sensitivity) == 2

    extension.root.destroy()


def test_format_csv(mock_emit_environment):
    """Test CSV formatting."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Set up test data
    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz", "2450MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[-20.0, -25.0]]
    extension._rx_power = [[-50.0, -55.0]]
    extension._desense = [[5.0, 3.0]]
    extension._sensitivity = [[-100.0, -102.0]]

    # Create temp file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        temp_path = f.name

    try:
        extension._format_csv(temp_path)

        # Verify file contents
        with open(temp_path, "r") as f:
            content = f.read()
            assert "Aggressor_Radio" in content
            assert "RxRadio1" in content
            assert "TxRadio1" in content
            assert "-20.0" in content
    finally:
        import os

        os.unlink(temp_path)

    extension.root.destroy()


@patch("tkinter.filedialog.asksaveasfilename")
def test_on_export_csv(mock_filedialog, mock_emit_environment):
    """Test CSV export functionality."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    # Setup basic mocks
    mock_analyze.get_interferer_names.return_value = ["TxRadio1"]
    mock_analyze.get_receiver_names.return_value = ["RxRadio1"]
    mock_analyze.get_band_names.return_value = ["Band1"]
    mock_analyze.get_active_frequencies.return_value = ["2400MHz"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = EMIHeatmapExtension(withdraw=True)

    # Set up test data
    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[-20.0]]
    extension._rx_power = [[-50.0]]
    extension._desense = [[5.0]]
    extension._sensitivity = [[-100.0]]

    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        temp_path = f.name

    mock_filedialog.return_value = temp_path

    try:
        with patch("tkinter.messagebox.showinfo") as mock_info:
            extension._on_export_csv()
            assert mock_info.called
    finally:
        import os

        if os.path.exists(temp_path):
            os.unlink(temp_path)

    extension.root.destroy()


@patch("matplotlib.pyplot.get_current_fig_manager")
@patch("matplotlib.pyplot.show")
def test_plot_matrix_heatmap_normal_case(mock_show, mock_fig_manager, mock_emit_environment):
    """Test heatmap plotting with normal data spanning all three color ranges."""
    # Mock the figure manager to avoid backend-specific issues
    mock_manager = MagicMock()
    mock_fig_manager.return_value = mock_manager
    
    extension = EMIHeatmapExtension(withdraw=True)

    # Set up test data spanning all three ranges
    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz", "2450MHz"]
    extension._aggressor_frequencies = ["2400MHz", "2450MHz"]
    extension._emi = [[-15.0, -5.0], [-2.0, 5.0]]  # Spans green, yellow, red

    extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)

    # Function should complete without error
    assert mock_show.called

    extension.root.destroy()


@patch("matplotlib.pyplot.get_current_fig_manager")
@patch("matplotlib.pyplot.show")
def test_plot_matrix_heatmap_edge_cases(mock_show, mock_fig_manager, mock_emit_environment):
    """Test heatmap plotting with various edge cases: single color ranges and constant values."""
    # Mock the figure manager to avoid backend-specific issues
    mock_manager = MagicMock()
    mock_fig_manager.return_value = mock_manager
    
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz", "2450MHz"]
    extension._aggressor_frequencies = ["2400MHz"]

    # Test case 1: All values in green range
    extension._emi = [[-20.0, -25.0]]
    extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)
    assert mock_show.called
    mock_show.reset_mock()

    # Test case 2: All values in red range
    extension._emi = [[5.0, 10.0]]
    extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)
    assert mock_show.called
    mock_show.reset_mock()

    # Test case 3: All values are identical (constant)
    extension._emi = [[-5.0, -5.0]]
    extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)
    assert mock_show.called

    extension.root.destroy()


@patch("tkinter.messagebox.showerror")
def test_plot_matrix_heatmap_error_cases(mock_error, mock_emit_environment):
    """Test heatmap plotting with invalid inputs: empty data, NaN values, and invalid thresholds."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"

    # Test case 1: Empty data
    extension._victim_frequencies = []
    extension._aggressor_frequencies = []
    extension._emi = []
    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)
    assert mock_error.called
    assert result is None
    mock_error.reset_mock()

    # Test case 2: NaN values
    extension._victim_frequencies = ["2400MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[np.nan]]
    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)
    assert mock_error.called
    assert result is None
    mock_error.reset_mock()

    # Test case 3: Invalid threshold (NaN)
    extension._emi = [[-5.0]]
    result = extension._plot_matrix_heatmap(red_threshold=np.nan, yellow_threshold=-10)
    assert mock_error.called
    assert result is None
    mock_error.reset_mock()

    # Test case 4: Equal thresholds
    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=0)
    assert mock_error.called
    assert result is None

    extension.root.destroy()


@patch("matplotlib.pyplot.get_current_fig_manager")
@patch("matplotlib.pyplot.show")
def test_on_generate_heatmap(mock_show, mock_fig_manager, mock_emit_environment):
    """Test generating heatmap plot."""
    # Mock the figure manager to avoid backend-specific issues
    mock_manager = MagicMock()
    mock_fig_manager.return_value = mock_manager
    
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()
    mock_category_node = MagicMock()

    # Setup mocks
    mock_analyze.get_interferer_names.return_value = ["TxRadio1"]
    mock_analyze.get_receiver_names.return_value = ["RxRadio1"]
    mock_analyze.get_band_names.return_value = ["Band1"]
    mock_analyze.get_active_frequencies.return_value = ["2400MHz"]
    mock_category_node.properties = {"EmiThresholdList": "0.0;-10.0"}
    mock_analyze.get_result_categorization_node.return_value = mock_category_node
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = EMIHeatmapExtension(withdraw=True)

    # Set up test data
    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[-5.0]]

    extension._on_generate_heatmap()

    assert mock_show.called

    extension.root.destroy()
