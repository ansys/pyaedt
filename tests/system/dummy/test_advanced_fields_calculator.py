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

from unittest.mock import PropertyMock
from unittest.mock import patch

from ansys.aedt.core import Hfss
from ansys.aedt.core import Q3d
from ansys.aedt.core.extensions.common.advanced_fields_calculator import AdvancedFieldsCalculatorExtension
from ansys.aedt.core.extensions.common.advanced_fields_calculator import AdvancedFieldsCalculatorExtensionData
from ansys.aedt.core.extensions.common.advanced_fields_calculator import main
from ansys.aedt.core.modeler.modeler_3d import Modeler3D

TEST_SUBFOLDER = "T45"
FIELDS_CALCULATOR = "fields_calculator_solved"
HFSS_ASSIGNMENTS = ["Polyline1", "Polyline2"]


@patch.object(AdvancedFieldsCalculatorExtension, "check_design_type", return_value=None)
def test_advanced_fields_calculator_q3d_ok_button(mock_check, add_app_example):
    """Test the OK button in the Advanced Fields Calculator extension."""
    aedt_app = add_app_example(application=Q3d, project=FIELDS_CALCULATOR, subfolder=TEST_SUBFOLDER)

    DATA = AdvancedFieldsCalculatorExtensionData(
        setup="Setup1 : LastAdaptive",
        calculation="voltage_line",
        assignments=[],
    )

    extension = AdvancedFieldsCalculatorExtension(withdraw=True)
    extension.root.nametowidget("ok_button").invoke()

    assert 0 == len(aedt_app.post.all_report_names)
    assert DATA == extension.data
    assert main(extension.data)
    assert 2 == len(aedt_app.post.all_report_names)
    aedt_app.close_project(save=False)


@patch.object(Modeler3D, "selections", new_callable=PropertyMock)
def test_advanced_fields_calculator_hfss_ok_button(mock_selections, add_app_example):
    """Test the OK button in the Advanced Fields Calculator extension for HFSS."""
    mock_selections.return_value = HFSS_ASSIGNMENTS

    DATA = AdvancedFieldsCalculatorExtensionData(
        setup="Setup1 : LastAdaptive",
        calculation="voltage_line",
        assignments=HFSS_ASSIGNMENTS,
    )
    aedt_app = add_app_example(application=Hfss, project=FIELDS_CALCULATOR, subfolder=TEST_SUBFOLDER)

    extension = AdvancedFieldsCalculatorExtension(withdraw=True)
    extension.root.nametowidget("ok_button").invoke()

    assert 2 == len(aedt_app.post.all_report_names)
    assert DATA == extension.data
    assert main(extension.data)
    assert 4 == len(aedt_app.post.all_report_names)
    aedt_app.close_project(save=False)
