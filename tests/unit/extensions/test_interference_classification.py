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

import pytest

from ansys.aedt.core.extensions.emit.interference_classification import InterferenceClassificationExtension


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


def test_interference_classification_widgets_created(mock_emit_environment):
    """Test that UI widgets are correctly created."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Check that key widgets exist
    assert "canvas_prot" in extension._widgets
    assert "canvas_int" in extension._widgets
    assert "prot_legend_entries" in extension._widgets
    assert "radio_specific_toggle" in extension._widgets
    assert "radio_dropdown" in extension._widgets
    
    # Check that legend entries dictionary has all required keys
    legend_entries = extension._widgets["prot_legend_entries"]
    assert "Damage" in legend_entries
    assert "Overload" in legend_entries
    assert "Intermodulation" in legend_entries
    assert "Desensitization" in legend_entries

    # Check filter variables are initialized
    assert "in_in" in extension._filters_interf
    assert "out_in" in extension._filters_interf
    assert "in_out" in extension._filters_interf
    assert "out_out" in extension._filters_interf

    assert "damage" in extension._filters_prot
    assert "overload" in extension._filters_prot
    assert "intermodulation" in extension._filters_prot
    assert "desensitization" in extension._filters_prot

    # Check default values
    assert extension._filters_interf["in_in"].get() is True
    assert extension._filters_prot["damage"].get() is True
    assert extension._radio_specific_var.get() is False
    assert extension._global_protection_level is True

    extension.root.destroy()


def test_get_legend_values(mock_emit_environment):
    """Test retrieving protection level values from the legend."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Get legend values (default values from UI)
    values = extension._get_legend_values()

    # Should return 4 values (damage, overload, intermodulation, desensitization)
    assert len(values) == 4
    assert values[0] == 30.0  # Damage
    assert values[1] == -4.0  # Overload
    assert values[2] == -30.0  # Intermodulation
    assert values[3] == -104.0  # Desensitization

    extension.root.destroy()


def test_radio_specific_toggle(mock_emit_environment):
    """Test toggling radio-specific protection levels."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    # Mock receiver names
    mock_analyze.get_receiver_names.return_value = ["Radio1", "Radio2", "Radio3"]
    mock_results.analyze.return_value = mock_analyze
    mock_aedt_app.results = mock_results

    extension = InterferenceClassificationExtension(withdraw=True)

    # Initially should be global
    assert extension._global_protection_level is True
    assert str(extension._radio_dropdown.cget("state")) == "disabled"

    # Toggle to radio-specific
    extension._radio_specific_var.set(True)
    extension._on_radio_specific_toggle()

    assert extension._global_protection_level is False
    assert str(extension._radio_dropdown.cget("state")) == "readonly"
    assert "Radio1" in extension._protection_levels
    assert "Radio2" in extension._protection_levels
    assert "Radio3" in extension._protection_levels

    # Toggle back to global
    extension._radio_specific_var.set(False)
    extension._on_radio_specific_toggle()

    assert extension._global_protection_level is True
    assert str(extension._radio_dropdown.cget("state")) == "disabled"
    assert "Global" in extension._protection_levels

    extension.root.destroy()


def test_radio_dropdown_changed(mock_emit_environment):
    """Test changing selected radio updates legend values."""
    # Create a fresh extension instance to avoid Tk conflicts
    mock_aedt_app = MagicMock()
    mock_aedt_app.design_type = "EMIT"
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    mock_analyze.get_receiver_names.return_value = ["Radio1", "Radio2"]
    mock_results.analyze.return_value = mock_analyze
    mock_aedt_app.results = mock_results

    # Update the mock in the fixture
    mock_emit_environment["get_pyaedt_app"].return_value = mock_aedt_app

    extension = InterferenceClassificationExtension(withdraw=True)

    # Enable radio-specific mode (this initializes protection levels for both radios)
    extension._radio_specific_var.set(True)
    extension._on_radio_specific_toggle()

    # Manually update Entry widgets for Radio1 to simulate user input
    entries = extension._widgets["prot_legend_entries"]
    entries["Damage"].delete(0, "end")
    entries["Damage"].insert(0, "40.0")
    entries["Overload"].delete(0, "end")
    entries["Overload"].insert(0, "-5.0")
    entries["Intermodulation"].delete(0, "end")
    entries["Intermodulation"].insert(0, "-25.0")
    entries["Desensitization"].delete(0, "end")
    entries["Desensitization"].insert(0, "-100.0")

    # Switch to Radio2 and back to Radio1 to test value persistence
    extension._radio_dropdown.set("Radio2")
    extension._on_radio_dropdown_changed()
    
    extension._radio_dropdown.set("Radio1")
    extension._on_radio_dropdown_changed()

    # Verify legend Entry widgets were updated with Radio1's saved values
    values = extension._get_legend_values()
    assert values == [40.0, -5.0, -25.0, -100.0]

    extension.root.destroy()


def test_build_interf_filters(mock_emit_environment):
    """Test building interference filter list from UI selections."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # All filters enabled by default
    filters = extension._build_interf_filters()
    assert len(filters) == 4

    # Disable some filters
    extension._filters_interf["in_in"].set(False)
    extension._filters_interf["out_out"].set(False)

    filters = extension._build_interf_filters()
    assert len(filters) == 2

    extension.root.destroy()


def test_compute_interference(mock_emit_environment):
    """Test computing interference type classification matrix."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_modeler = MagicMock()
    mock_components = MagicMock()
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    # Mock radios
    mock_components.get_radios.return_value = ["Radio1", "Radio2", "Radio3"]
    mock_modeler.components = mock_components
    mock_aedt_app.modeler = mock_modeler

    # Mock results
    mock_analyze.interference_type_classification.return_value = (
        [["red", "green"], ["yellow", "orange"], ["white", "red"]],
        [["IB/IB", "OOB/IB"], ["IB/OOB", "IB/IB"], ["OOB/OOB", "IB/IB"]],
    )
    mock_analyze.get_interferer_names.return_value = ["Tx1", "Tx2", "Tx3"]
    mock_analyze.get_receiver_names.return_value = ["Rx1", "Rx2"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = InterferenceClassificationExtension(withdraw=True)

    filters = ["TxFundamental:In-band"]
    tx, rx, colors, values = extension._compute_interference(filters)

    assert tx == ["Tx1", "Tx2", "Tx3"]
    assert rx == ["Rx1", "Rx2"]
    assert len(colors) == 3
    assert len(values) == 3

    extension.root.destroy()


def test_compute_interference_insufficient_radios(mock_emit_environment):
    """Test that compute_interference raises error with insufficient radios."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_modeler = MagicMock()
    mock_components = MagicMock()

    # Mock only one radio (insufficient)
    mock_components.get_radios.return_value = ["Radio1"]
    mock_modeler.components = mock_components
    mock_aedt_app.modeler = mock_modeler

    extension = InterferenceClassificationExtension(withdraw=True)

    with pytest.raises(RuntimeError, match="At least two radios are required"):
        extension._compute_interference([])

    extension.root.destroy()


def test_compute_protection(mock_emit_environment):
    """Test computing protection level classification matrix."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_modeler = MagicMock()
    mock_components = MagicMock()
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    # Mock radios
    mock_components.get_radios.return_value = ["Radio1", "Radio2"]
    mock_modeler.components = mock_components
    mock_aedt_app.modeler = mock_modeler

    # Mock results
    mock_analyze.protection_level_classification.return_value = (
        [["green", "red"], ["yellow", "orange"]],
        [["Safe", "Damage"], ["Overload", "Intermod"]],
    )
    mock_analyze.get_interferer_names.return_value = ["Tx1", "Tx2"]
    mock_analyze.get_receiver_names.return_value = ["Rx1", "Rx2"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = InterferenceClassificationExtension(withdraw=True)

    filters = ["damage", "overload"]
    tx, rx, colors, values = extension._compute_protection(filters)

    assert tx == ["Tx1", "Tx2"]
    assert rx == ["Rx1", "Rx2"]
    assert len(colors) == 2
    assert len(values) == 2

    extension.root.destroy()


def test_on_run_interference(mock_emit_environment):
    """Test the interference results generation button handler."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_modeler = MagicMock()
    mock_components = MagicMock()
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    mock_components.get_radios.return_value = ["Radio1", "Radio2"]
    mock_modeler.components = mock_components
    mock_aedt_app.modeler = mock_modeler

    mock_analyze.interference_type_classification.return_value = (
        [["red", "green"]],
        [["IB/IB", "OOB/IB"]],
    )
    mock_analyze.get_interferer_names.return_value = ["Tx1"]
    mock_analyze.get_receiver_names.return_value = ["Rx1", "Rx2"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = InterferenceClassificationExtension(withdraw=True)

    # Mock the render method to avoid canvas drawing issues
    extension._render_matrix = MagicMock()

    extension._on_run_interference()

    # Verify matrix data was populated
    assert extension._matrix is not None
    assert extension._matrix.tx_radios == ["Tx1"]
    assert extension._matrix.rx_radios == ["Rx1", "Rx2"]
    assert extension._render_matrix.called

    extension.root.destroy()


@patch("tkinter.messagebox.showerror")
def test_on_run_interference_error_handling(mock_showerror, mock_emit_environment):
    """Test error handling in interference results generation."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_modeler = MagicMock()
    mock_components = MagicMock()

    # Mock insufficient radios to trigger error
    mock_components.get_radios.return_value = ["Radio1"]
    mock_modeler.components = mock_components
    mock_aedt_app.modeler = mock_modeler

    extension = InterferenceClassificationExtension(withdraw=True)

    extension._on_run_interference()

    # Verify error dialog was shown
    assert mock_showerror.called

    extension.root.destroy()


def test_on_run_protection(mock_emit_environment):
    """Test the protection level results generation button handler."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_modeler = MagicMock()
    mock_components = MagicMock()
    mock_results = MagicMock()
    mock_analyze = MagicMock()

    mock_components.get_radios.return_value = ["Radio1", "Radio2"]
    mock_modeler.components = mock_components
    mock_aedt_app.modeler = mock_modeler

    mock_analyze.protection_level_classification.return_value = (
        [["green", "red"]],
        [["Safe", "Damage"]],
    )
    mock_analyze.get_interferer_names.return_value = ["Tx1"]
    mock_analyze.get_receiver_names.return_value = ["Rx1", "Rx2"]
    mock_results.analyze.return_value = mock_analyze
    mock_results.interaction_domain.return_value = MagicMock()
    mock_aedt_app.results = mock_results

    extension = InterferenceClassificationExtension(withdraw=True)

    # Mock the render method
    extension._render_matrix = MagicMock()

    extension._on_run_protection()

    # Verify matrix data was populated
    assert extension._matrix is not None
    assert extension._render_matrix.called

    extension.root.destroy()


@patch("tkinter.messagebox.showwarning")
def test_export_excel_no_data(mock_showwarning, mock_emit_environment):
    """Test export to Excel with no data shows warning."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # No matrix data
    extension._matrix = None

    extension._on_export_excel()

    # Verify warning was shown
    assert mock_showwarning.called

    extension.root.destroy()


@patch("tkinter.filedialog.asksaveasfilename")
def test_export_excel_with_data(mock_asksaveasfilename, mock_emit_environment):
    """Test export to Excel with valid data."""
    from ansys.aedt.core.extensions.emit.interference_classification import _MatrixData

    mock_asksaveasfilename.return_value = ""  # User cancels

    extension = InterferenceClassificationExtension(withdraw=True)

    # Create mock matrix data
    extension._matrix = _MatrixData(
        tx_radios=["Tx1", "Tx2"],
        rx_radios=["Rx1", "Rx2"],
        colors=[["red", "green"], ["yellow", "orange"]],
        values=[["IB/IB", "OOB/IB"], ["IB/OOB", "OOB/OOB"]],
    )

    extension._on_export_excel()

    # Verify file dialog was shown
    assert mock_asksaveasfilename.called

    extension.root.destroy()


@patch("tkinter.messagebox.showerror")
def test_on_run_protection_error_handling(mock_showerror, mock_emit_environment):
    """Test error handling in protection level results generation."""
    mock_aedt_app = mock_emit_environment["emit_app"]
    mock_modeler = MagicMock()
    mock_components = MagicMock()

    # Mock insufficient radios to trigger error
    mock_components.get_radios.return_value = ["Radio1"]
    mock_modeler.components = mock_components
    mock_aedt_app.modeler = mock_modeler

    extension = InterferenceClassificationExtension(withdraw=True)

    extension._on_run_protection()

    # Verify error dialog was shown
    assert mock_showerror.called

    extension.root.destroy()


def test_render_matrix(mock_emit_environment):
    """Test rendering matrix on canvas."""
    from ansys.aedt.core.extensions.emit.interference_classification import _MatrixData

    extension = InterferenceClassificationExtension(withdraw=True)

    # Create mock matrix data
    extension._matrix = _MatrixData(
        tx_radios=["Tx1"],
        rx_radios=["Rx1"],
        colors=[["red"]],
        values=[["IB/IB"]],
    )

    # Test rendering for both tabs
    extension._render_matrix(tab="interference")
    extension._render_matrix(tab="protection")

    # Verify canvases exist
    assert extension._widgets["canvas_int"] is not None
    assert extension._widgets["canvas_prot"] is not None

    extension.root.destroy()
