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
    from ansys.aedt.core.extensions.emit.interference_classification import InterferenceClassificationExtension


@pytest.fixture
def emit_app_with_radios(add_app_example):
    """Load the interference example to test the extension."""
    app = add_app_example(project="interference", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def test_extension_initialization(emit_app_with_radios) -> None:
    """Test that extension initializes correctly with an active EMIT design."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Verify extension properties
    assert extension.root.title() == "EMIT Interference Classification"
    assert extension.active_design_name == emit_app_with_radios.design_name
    assert extension.active_project_name == emit_app_with_radios.project_name
    assert extension.aedt_application.design_type == "EMIT"

    extension.root.destroy()


def test_radio_specific_protection_levels(emit_app_with_radios) -> None:
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


def test_generate_interference_results(emit_app_with_radios) -> None:
    """Test generating interference type classification results."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Mock the render method
    extension._render_matrix = MagicMock()

    # Trigger the interference results generation
    extension._on_run_interference()

    # Verify that matrix data was populated
    assert extension._matrix["interference"] is not None
    assert len(extension._matrix["interference"].tx_radios) > 0
    assert len(extension._matrix["interference"].rx_radios) > 0
    assert len(extension._matrix["interference"].colors) > 0
    assert len(extension._matrix["interference"].values) > 0

    # Verify render was called
    assert extension._render_matrix.called
    extension._render_matrix.assert_called_once_with(tab="interference")

    extension.root.destroy()


def test_generate_protection_results(emit_app_with_radios) -> None:
    """Test generating protection level classification results."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Mock the render method
    extension._render_matrix = MagicMock()

    # Trigger the protection level results generation
    extension._on_run_protection()

    # Verify that matrix data was populated
    assert extension._matrix["protection"] is not None
    assert len(extension._matrix["protection"].tx_radios) > 0
    assert len(extension._matrix["protection"].rx_radios) > 0
    assert len(extension._matrix["protection"].colors) > 0
    assert len(extension._matrix["protection"].values) > 0

    # Verify render was called
    assert extension._render_matrix.called
    extension._render_matrix.assert_called_once_with(tab="protection")

    extension.root.destroy()


def test_export_to_excel(emit_app_with_radios, test_tmp_dir) -> None:
    """Test exporting results matrix to Excel file."""
    extension = InterferenceClassificationExtension(withdraw=True)

    # Generate results first
    extension._render_matrix = MagicMock()
    extension._on_run_interference()

    # Set up file path
    excel_path = test_tmp_dir / "interference_results.xlsx"

    # Mock notebook and filedialog
    with patch.object(extension.root, "nametowidget") as mock_nametowidget:
        mock_notebook = MagicMock()
        mock_notebook.select.return_value = "tab_id"
        mock_notebook.index.return_value = 1  # Interference tab
        mock_nametowidget.return_value = mock_notebook

        with patch("tkinter.filedialog.asksaveasfilename", return_value=str(excel_path)):
            # Trigger export
            extension._on_export_excel()

    # Verify file was created
    assert excel_path.exists()
    assert excel_path.suffix == ".xlsx"
    assert excel_path.stat().st_size > 0

    extension.root.destroy()
