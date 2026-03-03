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

from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.post.fields_calculator import FieldsCalculator


@pytest.fixture
def mock_app(tmp_path_factory, request):
    app = MagicMock()
    app.aedt_version_id = getattr(request, "param", "2025.2")
    app.nominal_adaptive = "Setup1 : LastAdaptive"
    app.setup_names = ["Setup1"]
    app.logger = MagicMock()
    app.variable_manager.design_variables = {}
    app.variable_manager.project_variables = {}
    app.post._check_intrinsics([])
    app.working_directory = tmp_path_factory.mktemp("aedt_working_dir")
    return app


@pytest.fixture
def mock_app_array(tmp_path_factory, request):
    app = MagicMock()
    app.aedt_version_id = getattr(request, "param", "2025.2")
    app.nominal_adaptive = "Setup1 : LastAdaptive"
    app.setup_names = ["Setup1"]
    app.logger = MagicMock()
    v = MagicMock()
    v.evaluated_value = "[1,2,3]mm"
    app.variable_manager.design_variables = {"test_array": v}
    app.variable_manager.project_variables = {}
    app.post._check_intrinsics([])
    app.working_directory = tmp_path_factory.mktemp("aedt_working_dir")
    return app


def test_write_empty_design_variables(mock_app, test_tmp_dir) -> None:
    """Test the write method of FieldsCalculator class with no array variables."""
    fields_calculator = FieldsCalculator(mock_app)
    fields_calculator.ofieldsreporter = MagicMock()
    fields_calculator.is_expression_defined = MagicMock(return_value=True)
    output_file = test_tmp_dir / "expr.fld"

    result = fields_calculator.write(
        expression="my_expr",
        output_file=str(output_file),
        setup=mock_app.nominal_adaptive,
        intrinsics=None,
    )

    assert result is True


@pytest.mark.parametrize("mock_app", ["2026.1"], indirect=True)
def test_write_20261(mock_app, test_tmp_dir) -> None:
    """Test the write method of FieldsCalculator class with no array variables in AEDT 2026.1."""
    fields_calculator = FieldsCalculator(mock_app)
    fields_calculator.ofieldsreporter = MagicMock()
    fields_calculator.is_expression_defined = MagicMock(return_value=True)
    output_file = test_tmp_dir / "expr.fld"

    result = fields_calculator.write(
        expression="my_expr",
        output_file=str(output_file),
        setup=mock_app.nominal_adaptive,
        intrinsics=None,
    )

    assert result is True


def test_write_array_design_variables(mock_app_array, test_tmp_dir) -> None:
    """Test the write method of FieldsCalculator class with array variables."""
    fields_calculator = FieldsCalculator(mock_app_array)
    fields_calculator.ofieldsreporter = MagicMock()
    fields_calculator.is_expression_defined = MagicMock(return_value=True)
    output_file = test_tmp_dir / "expr.fld"

    with pytest.raises(AEDTRuntimeError):
        fields_calculator.write(
            expression="my_expr",
            output_file=str(output_file),
            setup=mock_app_array.nominal_adaptive,
            intrinsics=None,
        )


def test_write_failure_expression_not_defined(mock_app, test_tmp_dir) -> None:
    fields_calculator = FieldsCalculator(mock_app)

    with patch.object(fields_calculator, "is_expression_defined", return_value=False):
        output_file = test_tmp_dir / "expr.fld"
        result = fields_calculator.write(
            expression="my_expr",
            output_file=str(output_file),
            setup=mock_app.nominal_adaptive,
            intrinsics=None,
        )

    assert result is False


def test_write_failure_file_extension(mock_app, test_tmp_dir) -> None:
    fields_calculator = FieldsCalculator(mock_app)

    with patch.object(fields_calculator, "is_expression_defined", return_value=True):
        output_file = test_tmp_dir / "expr.txt"
        result = fields_calculator.write(
            expression="my_expr",
            output_file=str(output_file),
            setup=mock_app.nominal_adaptive,
            intrinsics=None,
        )

    assert result is False


@patch(
    "ansys.aedt.core.visualization.post.fields_calculator.open_file",
    mock_open(read_data="line1\nline2\nfinal_value\n"),
)
@patch("ansys.aedt.core.visualization.post.fields_calculator.Path.exists", return_value=True)
@patch("ansys.aedt.core.visualization.post.fields_calculator.Path.unlink")
@patch("ansys.aedt.core.visualization.post.fields_calculator.FieldsCalculator.write")
def test_evaluate(mock_fc_write, mock_path_unlink, mock_path_exists, mock_app) -> None:
    """Test the evaluate method of FieldsCalculator class."""
    fields_calculator = FieldsCalculator(mock_app)
    fields_calculator.is_expression_defined = MagicMock(return_value=True)
    fields_calculator.ofieldsreporter = MagicMock()

    value = fields_calculator.evaluate(expression="expr", setup=None, intrinsics=None)

    assert value is not None
    mock_fc_write.assert_called_once()


@patch("ansys.aedt.core.visualization.post.fields_calculator.Path.exists", return_value=True)
def test_export_with_sample_points_string(mock_path_exists, mock_app) -> None:
    """Test the export method of FieldsCalculator class with sample points as a path."""
    fields_calculator = FieldsCalculator(mock_app)
    mock_app.post.export_field_file = MagicMock(return_value="fake_output.fld")

    output = fields_calculator.export(
        quantity="Mag_E",
        output_file="fake_output.fld",
        solution="Setup1 : LastAdaptive",
        sample_points="points.csv",
    )

    assert output == "fake_output.fld"


@patch("ansys.aedt.core.visualization.post.fields_calculator.Path.exists", return_value=True)
def test_export_with_sample_points_list(mock_path_exists, mock_app) -> None:
    """Test the export method of FieldsCalculator class with sample points as a list."""
    fields_calculator = FieldsCalculator(mock_app)
    mock_app.post.export_field_file = MagicMock(return_value="fake_output.fld")
    sample_points = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]

    output = fields_calculator.export(
        quantity="Mag_E",
        output_file="fake_output.fld",
        solution="Setup1 : LastAdaptive",
        sample_points=sample_points,
    )

    assert output == "fake_output.fld"


def test_export_with_invalid_sample_points(mock_app) -> None:
    """Test the export method of FieldsCalculator class with invalid sample points."""
    fields_calculator = FieldsCalculator(mock_app)
    sample_points = 1

    res = fields_calculator.export(
        quantity="Mag_E", output_file="fake_output.fld", solution="Setup1 : LastAdaptive", sample_points=sample_points
    )

    assert not res


@patch("ansys.aedt.core.visualization.post.fields_calculator.Path.exists", return_value=True)
def test_export_grid_type(mock_path_exists, mock_app) -> None:
    """Test the export method of FieldsCalculator class with different grid types."""
    fields_calculator = FieldsCalculator(mock_app)
    mock_app.post.export_field_file_on_grid = MagicMock(return_value="fake_output.fld")

    grid_types = ["Cartesian", "Cylindrical", "Spherical"]

    for grid_type in grid_types:
        output = fields_calculator.export(
            quantity="Mag_E", output_file="fake_output.fld", solution="Setup1 : LastAdaptive", grid_type=grid_type
        )
        assert output == "fake_output.fld"


def test_export_invalid_grid_type(mock_app) -> None:
    """Test the export method of FieldsCalculator class with an invalid grid type."""
    fields_calculator = FieldsCalculator(mock_app)
    mock_app._FieldsCalculator__app.post.export_field_file_on_grid = MagicMock(return_value="fake_output.fld")
    grid_type = "invalid"

    res = fields_calculator.export(
        quantity="Mag_E", output_file="fake_output.fld", solution="Setup1 : LastAdaptive", grid_type=grid_type
    )

    assert not res


def test_export_failure(mock_app) -> None:
    """Test the export method of FieldsCalculator class when export fails."""
    fields_calculator = FieldsCalculator(mock_app)

    res = fields_calculator.export(quantity="Mag_E", output_file="fake_output.fld", solution="Setup1 : LastAdaptive")

    assert not res


@patch("ansys.aedt.core.visualization.post.fields_calculator.Path.is_file", return_value=False)
def test_load_expression_file_failure(mock_is_file, mock_app, test_tmp_dir) -> None:
    """Test the failure of load_expression method of FieldsCalculator class."""
    fields_calculator = FieldsCalculator(mock_app)
    input_file = test_tmp_dir / "expr_load.fld"

    assert not fields_calculator.load_expression_file(input_file)


@patch(
    "ansys.aedt.core.visualization.post.fields_calculator.read_configuration_file",
    return_value={"expr1": {"unit": "V"}},
)
@patch("ansys.aedt.core.visualization.post.fields_calculator.Path.is_file", return_value=True)
def test_load_expression_file_success(mock_read_config, mock_app, test_tmp_dir) -> None:
    """Test the success of load_expression method of FieldsCalculator class."""
    fields_calculator = FieldsCalculator(mock_app)
    with patch.object(fields_calculator, "validate_expression", return_value=True):
        result = fields_calculator.load_expression_file("fake.toml")

    assert "expr1" in result
