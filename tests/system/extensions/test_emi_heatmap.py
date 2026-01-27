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

"""System tests for EMI Heatmap extension - integration tests with real EMIT projects."""

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


@pytest.fixture
def emit_app_with_radios(add_app_example):
    """Load the interference example to test the extension."""
    app = add_app_example(project="interference", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def test_extract_emi_data(emit_app_with_radios):
    """Test extracting EMI data from real EMIT project."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim_combo.current(1)
    extension._on_victim_changed()
    extension._victim_band_combo.current(0)
    extension._on_victim_band_changed()
    extension._aggressor_combo.current(1)
    extension._on_aggressor_changed()
    extension._aggressor_band_combo.current(0)
    extension._on_aggressor_band_changed()

    # Extract data from real EMIT project
    extension._extract_data()

    # Verify data was extracted
    assert extension._emi is not None
    assert extension._rx_power is not None
    assert extension._desense is not None
    assert extension._sensitivity is not None

    assert len(extension._emi) > 0
    assert len(extension._rx_power) > 0
    assert len(extension._desense) > 0
    assert len(extension._sensitivity) > 0

    assert len(extension._emi) == len(extension._rx_power) == len(extension._desense) == len(extension._sensitivity)

    extension.root.destroy()


def test_export_to_csv(emit_app_with_radios, test_tmp_dir):
    """Test exporting real EMIT data to CSV file."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim_combo.current(1)
    extension._on_victim_changed()
    extension._victim_band_combo.current(0)
    extension._on_victim_band_changed()
    extension._aggressor_combo.current(1)
    extension._on_aggressor_changed()
    extension._aggressor_band_combo.current(0)
    extension._on_aggressor_band_changed()

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

    # Verify CSV content has proper structure and real data
    with open(csv_path, "r") as f:
        content = f.read()
        assert "Aggressor_Radio" in content
        assert "Victim_Radio" in content
        assert "EMI" in content
        assert "RX_Power" in content
        assert "Desense" in content
        assert "Sensitivity" in content
        # Should have actual data rows, not just headers
        lines = content.strip().split("\n")
        assert len(lines) > 1

    extension.root.destroy()


@patch("matplotlib.pyplot.show")
def test_generate_heatmap(mock_show, emit_app_with_radios):
    """Test end-to-end heatmap generation with real EMIT project data."""
    extension = EMIHeatmapExtension(withdraw=True)

    extension._victim_combo.current(1)
    extension._on_victim_changed()
    extension._victim_band_combo.current(0)
    extension._on_victim_band_changed()
    extension._aggressor_combo.current(1)
    extension._on_aggressor_changed()
    extension._aggressor_band_combo.current(0)
    extension._on_aggressor_band_changed()

    # Extract data
    extension._extract_data()

    # Generate heatmap - should complete without errors
    extension._on_generate_heatmap()

    # Verify plot was created
    assert mock_show.called

    extension.root.destroy()


def test_full_workflow_integration(emit_app_with_radios, test_tmp_dir):
    """Test complete workflow: initialize -> select radios -> extract -> export."""
    extension = EMIHeatmapExtension(withdraw=True)

    # Verify extension initialized with real project
    assert extension.active_design_name == emit_app_with_radios.design_name
    assert extension.active_project_name == emit_app_with_radios.project_name

    # Verify radios were loaded from project
    assert len(extension._victims) > 0
    assert len(extension._aggressors) > 0

    # Select victim and aggressor
    extension._victim_combo.current(1)
    extension._on_victim_changed()
    assert extension._victim_band_combo["values"]

    extension._victim_band_combo.current(0)
    extension._on_victim_band_changed()
    assert len(extension._victim_frequencies) > 0

    extension._aggressor_combo.current(1)
    extension._on_aggressor_changed()
    assert extension._aggressor_band_combo["values"]

    extension._aggressor_band_combo.current(0)
    extension._on_aggressor_band_changed()
    assert len(extension._aggressor_frequencies) > 0

    # Extract real data
    extension._extract_data()
    assert len(extension._emi) > 0

    # Export to CSV
    csv_path = test_tmp_dir / "workflow_test.csv"
    extension._format_csv(str(csv_path))
    assert csv_path.exists()

    extension.root.destroy()
