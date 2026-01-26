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

from ansys.aedt.core.extensions.emit.emi_heatmap import EMIHeatmapExtension
from ansys.aedt.core.extensions.emit.emi_heatmap import EMIHeatmapExtensionData


@pytest.fixture
def mock_emit_environment():
    """Mock the EMIT environment for testing."""
    with patch("ansys.aedt.core.extensions.misc.get_pyaedt_app") as mock_get_app:
        mock_aedt_app = MagicMock()
        mock_aedt_app.design_type = "EMIT"
        mock_aedt_app.project_name = "TestProject"
        mock_aedt_app.design_name = "TestDesign"
        mock_aedt_app.project_path = "C:/test/project.aedt"
        mock_get_app.return_value = mock_aedt_app
        yield {"emit_app": mock_aedt_app, "get_pyaedt_app": mock_get_app}


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
    assert extension.root.title() == "EMIT EMI Heatmap"
    assert extension.active_design_name == "TestDesign"
    assert extension.active_project_name == "TestProject"
    assert extension.aedt_application.design_type == "EMIT"

    # Verify internal state initialization
    assert extension._domain is None
    assert extension._revision is None
    assert extension._emi is None
    assert extension._victims is None
    assert extension._aggressors is None

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


@patch("matplotlib.pyplot.show")
def test_plot_matrix_heatmap_normal_case(mock_show, mock_emit_environment):
    """Test heatmap plotting with normal data spanning all three color ranges."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Set up test data spanning all three ranges
    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz", "2450MHz"]
    extension._aggressor_frequencies = ["2400MHz", "2450MHz"]
    extension._emi = [[-15.0, -5.0], [-2.0, 5.0]]  # Spans green, yellow, red
    extension.active_project_name = "TestProject"

    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)

    # Function should complete without error
    assert mock_show.called

    extension.root.destroy()


@patch("matplotlib.pyplot.show")
def test_plot_matrix_heatmap_single_color_green(mock_show, mock_emit_environment):
    """Test heatmap plotting when all values are in green range."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz", "2450MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[-20.0, -25.0]]  # All below yellow threshold
    extension.active_project_name = "TestProject"

    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)

    assert mock_show.called

    extension.root.destroy()


@patch("matplotlib.pyplot.show")
def test_plot_matrix_heatmap_single_color_red(mock_show, mock_emit_environment):
    """Test heatmap plotting when all values are in red range."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz", "2450MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[5.0, 10.0]]  # All above red threshold
    extension.active_project_name = "TestProject"

    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)

    assert mock_show.called

    extension.root.destroy()


@patch("matplotlib.pyplot.show")
def test_plot_matrix_heatmap_constant_values(mock_show, mock_emit_environment):
    """Test heatmap plotting when all values are identical."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz", "2450MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[-5.0, -5.0]]  # All same value
    extension.active_project_name = "TestProject"

    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)

    assert mock_show.called

    extension.root.destroy()


@patch("tkinter.messagebox.showerror")
def test_plot_matrix_heatmap_empty_data(mock_error, mock_emit_environment):
    """Test heatmap plotting with empty data."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = []
    extension._aggressor_frequencies = []
    extension._emi = []
    extension.active_project_name = "TestProject"

    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)

    assert mock_error.called
    assert result is None

    extension.root.destroy()


@patch("tkinter.messagebox.showerror")
def test_plot_matrix_heatmap_nan_values(mock_error, mock_emit_environment):
    """Test heatmap plotting with NaN values."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[np.nan]]
    extension.active_project_name = "TestProject"

    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=-10)

    assert mock_error.called
    assert result is None

    extension.root.destroy()


@patch("tkinter.messagebox.showerror")
def test_plot_matrix_heatmap_invalid_thresholds(mock_error, mock_emit_environment):
    """Test heatmap plotting with invalid threshold values."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[-5.0]]
    extension.active_project_name = "TestProject"

    # Test with NaN threshold
    result = extension._plot_matrix_heatmap(red_threshold=np.nan, yellow_threshold=-10)
    assert mock_error.called
    assert result is None

    extension.root.destroy()


@patch("tkinter.messagebox.showerror")
def test_plot_matrix_heatmap_equal_thresholds(mock_error, mock_emit_environment):
    """Test heatmap plotting with equal threshold values."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim = "RxRadio1"
    extension._victim_band = "Band1"
    extension._aggressor = "TxRadio1"
    extension._aggressor_band = "Band1"
    extension._victim_frequencies = ["2400MHz"]
    extension._aggressor_frequencies = ["2400MHz"]
    extension._emi = [[-5.0]]
    extension.active_project_name = "TestProject"

    result = extension._plot_matrix_heatmap(red_threshold=0, yellow_threshold=0)

    assert mock_error.called
    assert result is None

    extension.root.destroy()


@patch("matplotlib.pyplot.show")
def test_on_generate_heatmap(mock_show, mock_emit_environment):
    """Test generating heatmap plot."""
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
    extension.active_project_name = "TestProject"

    extension._on_generate_heatmap()

    assert mock_show.called

    extension.root.destroy()
