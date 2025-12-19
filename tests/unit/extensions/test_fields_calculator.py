# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.aedt.core.visualization.post.fields_calculator import FieldsCalculator


@pytest.fixture
def mock_fields_calculator_class():
    """Create a MagicMock to replace the real class"""
    with patch("ansys.aedt.core.visualization.post.fields_calculator.FieldsCalculator.__init__", lambda x: None):
        fc = FieldsCalculator()
        yield fc


def test_fields_calculator_write(mock_fields_calculator_class, local_scratch):
    """Test the write method of FieldsCalculator via ExtensionCommon"""
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
