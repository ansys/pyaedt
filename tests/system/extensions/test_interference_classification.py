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
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.generic.general_methods import is_linux
from tests import TESTS_EMIT_PATH
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"

# Prior to 2025R1, the Emit API supported Python 3.8,3.9,3.10,3.11
# Starting with 2025R1, the Emit API supports Python 3.10,3.11,3.12
if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and DESKTOP_VERSION < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and DESKTOP_VERSION > "2024.2"
):
    from ansys.aedt.core import Emit
    from ansys.aedt.core.extensions.emit.interference_classification import InterferenceClassificationExtension
    from ansys.aedt.core.extensions.emit.interference_classification import InterferenceClassificationExtension


@pytest.fixture
def emit_app_with_radios(add_app_example):
    """Load the interference example to test the extension."""
    app = add_app_example(project="interference", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_extension_initialization(emit_app_with_radios):
    """Test that extension initializes correctly with an active EMIT design."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Verify extension properties
    assert extension.root.title() == "EMIT Interference Classification"
    assert extension.active_design_name == emit_app_with_radios.design_name
    assert extension.active_project_name == emit_app_with_radios.project_name
    assert extension.aedt_application.design_type == "EMIT"

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_protection_level_defaults(emit_app_with_radios):
    """Test that protection level legend contains correct default values."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Get default legend values
    values = extension._get_legend_values()

    # Verify default protection levels
    assert len(values) == 4
    assert values[0] == 30.0  # Damage
    assert values[1] == -4.0  # Overload
    assert values[2] == -30.0  # Intermodulation
    assert values[3] == -104.0  # Desensitization

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_radio_specific_protection_levels(emit_app_with_radios):
    """Test enabling radio-specific protection levels."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Initially should use global protection levels
    assert extension._global_protection_level is True

    # Enable radio-specific mode
    extension._radio_specific_var.set(True)
    extension._on_radio_specific_toggle()

    # Verify radio-specific mode is enabled
    assert extension._global_protection_level is False

    # Verify that protection levels were created for each receiver
    rx_names = emit_app_with_radios.results.analyze().get_receiver_names()
    for rx_name in rx_names:
        assert rx_name in extension._protection_levels

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_interference_filters(emit_app_with_radios):
    """Test building interference type filters from UI selections."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # All filters should be enabled by default
    filters = extension._build_interf_filters()
    assert len(filters) == 4

    # Disable some filters
    extension._filters_interf["in_in"].set(False)
    extension._filters_interf["out_out"].set(False)

    # Verify filter list is updated
    filters = extension._build_interf_filters()
    assert len(filters) == 2

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_compute_interference_classification(emit_app_with_radios):
    """Test computing interference type classification matrix."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Get radios
    radios = emit_app_with_radios.modeler.components.get_radios()
    assert len(radios) >= 2

    # Build filters
    filters = extension._build_interf_filters()

    # Compute interference classification
    tx_radios, rx_radios, colors, values = extension._compute_interference(filters)

    # Verify results structure
    assert len(tx_radios) > 0
    assert len(rx_radios) > 0
    assert len(colors) == len(tx_radios)
    assert len(values) == len(tx_radios)

    # Verify matrix dimensions
    for col_colors in colors:
        assert len(col_colors) == len(rx_radios)
    for col_values in values:
        assert len(col_values) == len(rx_radios)

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_compute_protection_classification(emit_app_with_radios):
    """Test computing protection level classification matrix."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Get radios
    radios = emit_app_with_radios.modeler.components.get_radios()
    assert len(radios) >= 2

    # Use all protection level filters
    filters = ["damage", "overload", "intermodulation", "desensitization"]

    # Compute protection level classification
    tx_radios, rx_radios, colors, values = extension._compute_protection(filters)

    # Verify results structure
    assert len(tx_radios) > 0
    assert len(rx_radios) > 0
    assert len(colors) == len(tx_radios)
    assert len(values) == len(tx_radios)

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_generate_interference_results(emit_app_with_radios):
    """Test generating interference type classification results."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Mock the render method
    extension._render_matrix = MagicMock()

    # Trigger the interference results generation
    extension._on_run_interference()

    # Verify that matrix data was populated
    assert extension._matrix is not None
    assert len(extension._matrix.tx_radios) > 0
    assert len(extension._matrix.rx_radios) > 0
    assert len(extension._matrix.colors) > 0
    assert len(extension._matrix.values) > 0

    # Verify render was called
    assert extension._render_matrix.called
    extension._render_matrix.assert_called_once_with(tab="interference")

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_generate_protection_results(emit_app_with_radios):
    """Test generating protection level classification results."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Mock the render method
    extension._render_matrix = MagicMock()

    # Trigger the protection level results generation
    extension._on_run_protection()

    # Verify that matrix data was populated
    assert extension._matrix is not None
    assert len(extension._matrix.tx_radios) > 0
    assert len(extension._matrix.rx_radios) > 0
    assert len(extension._matrix.colors) > 0
    assert len(extension._matrix.values) > 0

    # Verify render was called
    assert extension._render_matrix.called
    extension._render_matrix.assert_called_once_with(tab="protection")

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
@patch("tkinter.filedialog.asksaveasfilename")
def test_export_to_excel(mock_save_dialog, emit_app_with_radios, test_tmp_dir):
    """Test exporting results matrix to Excel file."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Generate results first
    extension._render_matrix = MagicMock()
    extension._on_run_interference()

    # Set up mock to return a file path
    excel_path = test_tmp_dir / "interference_results.xlsx"
    mock_save_dialog.return_value = str(excel_path)

    # Trigger export
    extension._on_export_excel()

    # Verify file dialog was called
    assert mock_save_dialog.called

    # Verify file was created (if path was provided)
    if excel_path.exists():
        assert excel_path.suffix == ".xlsx"
        assert excel_path.stat().st_size > 0

    extension.root.destroy()


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_insufficient_radios_error(add_app):
    """Test that extension raises error with insufficient radios."""
    app = add_app(application=Emit)

    # Create only one radio (insufficient)
    rad1 = app.modeler.components.create_component("UE - Handheld")
    ant1 = app.modeler.components.create_component("Antenna")
    ant1.move_and_connect_to(rad1)

    extension = InterferenceClassificationExtension(withdraw=True)

    # Attempting to compute interference should fail
    with pytest.raises(RuntimeError, match="At least two radios are required"):
        extension._compute_interference([])

    extension.root.destroy()
    app.close_project(app.project_name, save=False)
