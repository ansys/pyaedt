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
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from ansys.aedt.core.visualization.post.fields_calculator import FieldsCalculator


@pytest.fixture
def mock_fields_calculator_class():
    """Create a MagicMock to replace the real class"""
    with patch("ansys.aedt.core.visualization.post.fields_calculator.FieldsCalculator.__init__", lambda x: None):
        fc = FieldsCalculator()
        yield fc


def test_write(mock_fields_calculator_class, local_scratch):
    """Test the write method of FieldsCalculator class."""
    mock_fields_calculator_class._FieldsCalculator__app = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.nominal_adaptive = "Setup1 : LastAdaptive"
    mock_fields_calculator_class._FieldsCalculator__app.setup_names = ["Setup1"]
    mock_fields_calculator_class._FieldsCalculator__app.logger = MagicMock()
    mock_fields_calculator_class.is_expression_defined = MagicMock(return_value=True)
    output_file = local_scratch.path / "expr.fld"
    mock_fields_calculator_class.ofieldsreporter = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.variable_manager.design_variables = {}
    mock_fields_calculator_class._FieldsCalculator__app.post._check_intrinsics([])

    result = mock_fields_calculator_class.write(
        expression="my_expr",
        output_file=str(output_file),
        setup=mock_fields_calculator_class._FieldsCalculator__app.nominal_adaptive,
        intrinsics=None,
    )

    assert result is True


def test_evaluate(mock_fields_calculator_class, local_scratch):
    """Test the evaluate method of FieldsCalculator class."""
    mock_fields_calculator_class._FieldsCalculator__app = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.nominal_adaptive = "Setup1 : LastAdaptive"
    mock_fields_calculator_class._FieldsCalculator__app.setup_names = ["Setup1"]
    mock_fields_calculator_class._FieldsCalculator__app.logger = MagicMock()
    mock_fields_calculator_class.is_expression_defined = MagicMock(return_value=True)
    mock_fields_calculator_class.ofieldsreporter = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.post._check_intrinsics([])
    mock_fields_calculator_class._FieldsCalculator__app.working_directory = local_scratch.path

    with (
        patch("ansys.aedt.core.visualization.post.fields_calculator.generate_unique_name", return_value="testfile"),
        patch("ansys.aedt.core.visualization.post.fields_calculator.Path.exists", return_value=True),
        patch(
            "ansys.aedt.core.visualization.post.fields_calculator.open_file",
            mock_open(read_data="line1\nline2\nfinal_value\n"),
        ),
        patch("ansys.aedt.core.visualization.post.fields_calculator.Path.unlink"),
        patch.object(mock_fields_calculator_class, "write"),
    ):
        value = mock_fields_calculator_class.evaluate(expression="expr", setup=None, intrinsics=None)
    assert value is not None


def test_export_with_sample_points_string(mock_fields_calculator_class):
    """Test the export method of FieldsCalculator class with sample points as a path."""
    mock_fields_calculator_class._FieldsCalculator__app = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.post.export_field_file = MagicMock(
        return_value="fake_output.fld"
    )
    mock_fields_calculator_class._FieldsCalculator__app.logger = MagicMock()

    with patch("ansys.aedt.core.visualization.post.fields_calculator.Path.exists", return_value=True):
        output = mock_fields_calculator_class.export(
            quantity="Mag_E",
            output_file="fake_output.fld",
            solution="Setup1 : LastAdaptive",
            sample_points="points.csv",
        )
    assert output == "fake_output.fld"


def test_export_with_sample_points_list(mock_fields_calculator_class, local_scratch):
    """Test the export method of FieldsCalculator class with sample points as a list."""
    mock_fields_calculator_class._FieldsCalculator__app = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.post.export_field_file = MagicMock(
        return_value="fake_output.fld"
    )
    mock_fields_calculator_class._FieldsCalculator__app.logger = MagicMock()

    sample_points = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]

    with patch("ansys.aedt.core.visualization.post.fields_calculator.Path.exists", return_value=True):
        output = mock_fields_calculator_class.export(
            quantity="Mag_E",
            output_file="fake_output.fld",
            solution="Setup1 : LastAdaptive",
            sample_points=sample_points,
        )
    assert output == "fake_output.fld"


def test_export_with_invalid_sample_points(mock_fields_calculator_class):
    """Test the export method of FieldsCalculator class with invalid sample points."""
    mock_fields_calculator_class._FieldsCalculator__app = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.logger = MagicMock()

    sample_points = 1

    assert not mock_fields_calculator_class.export(
        quantity="Mag_E", output_file="fake_output.fld", solution="Setup1 : LastAdaptive", sample_points=sample_points
    )


def test_export_grid_type(mock_fields_calculator_class):
    """Test the export method of FieldsCalculator class with different grid types."""
    mock_fields_calculator_class._FieldsCalculator__app = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.post.export_field_file_on_grid = MagicMock(
        return_value="fake_output.fld"
    )
    mock_fields_calculator_class._FieldsCalculator__app.logger = MagicMock()

    grid_types = ["Cartesian", "Cylindrical", "Spherical"]

    for grid_type in grid_types:
        with patch("ansys.aedt.core.visualization.post.fields_calculator.Path.exists", return_value=True):
            output = mock_fields_calculator_class.export(
                quantity="Mag_E", output_file="fake_output.fld", solution="Setup1 : LastAdaptive", grid_type=grid_type
            )
        assert output == "fake_output.fld"


def test_export_invalid_grid_type(mock_fields_calculator_class):
    """Test the export method of FieldsCalculator class with an invalid grid type."""
    mock_fields_calculator_class._FieldsCalculator__app = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.post.export_field_file_on_grid = MagicMock(
        return_value="fake_output.fld"
    )
    mock_fields_calculator_class._FieldsCalculator__app.logger = MagicMock()

    grid_type = "invalid"

    assert not mock_fields_calculator_class.export(
        quantity="Mag_E", output_file="fake_output.fld", solution="Setup1 : LastAdaptive", grid_type=grid_type
    )


def test_export_failure(mock_fields_calculator_class):
    """Test the export method of FieldsCalculator class when export fails."""
    mock_fields_calculator_class._FieldsCalculator__app = MagicMock()
    mock_fields_calculator_class._FieldsCalculator__app.logger = MagicMock()

    assert not mock_fields_calculator_class.export(
        quantity="Mag_E", output_file="fake_output.fld", solution="Setup1 : LastAdaptive"
    )
