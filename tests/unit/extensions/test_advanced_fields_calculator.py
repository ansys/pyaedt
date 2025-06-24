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

import os
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest
import tomli

from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.project.advanced_fields_calculator import EXTENSION_TITLE
from ansys.aedt.core.extensions.project.advanced_fields_calculator import AdvancedFieldsCalculatorExtension
from ansys.aedt.core.extensions.project.advanced_fields_calculator import AdvancedFieldsCalculatorExtensionData

AEDT_APPLICATION_SETUP = "Setup1 : LastAdaptive"
AEDT_APPLICATION_SELECTIONS = ["Polyline1", "Polyline2"]
EXPRESSION_TAG = "Dummy tag"
EXPRESSION_DESCRIPTION = "Dummy description"
EXPRESSION_CONTENT = {
    "name": "Dummy name",
    "description": EXPRESSION_DESCRIPTION,
    "design_type": ["HFSS", "Q3D Extractor"],
    "fields_type": ["Fields", "CG Fields"],
    "solution_type": "Transient",
    "primary_sweep": "Freq",
    "assignment": "",
    "assignment_type": ["Line"],
    "operations": [
        "Fundamental_Quantity('E')",
        "Operation('Real')",
        "Operation('Tangent')",
        "Operation('Dot')",
        "EnterLine('assignment')",
        "Operation('LineValue')",
        "Operation('Integrate')",
        "Operation('CmplxR')",
    ],
    "report": ["Data Table", "Rectangular Plot"],
}
EXPRESSION_CATALOG = {EXPRESSION_TAG: EXPRESSION_CONTENT}


@pytest.fixture
def mock_aedt_app_with_expression_catalog():
    """Fixture to create a mock AEDT application with an expression catalog."""
    mock_fields_calculator = MagicMock()
    mock_fields_calculator.expression_catalog = EXPRESSION_CATALOG

    def load_expression_file_side_effect(toml_file):
        with open(toml_file, "rb") as f:
            toml_content = tomli.load(f)

        mock_fields_calculator.expression_catalog.update(toml_content)

    mock_fields_calculator.load_expression_file.side_effect = load_expression_file_side_effect
    # self.aedt_application.post.fields_calculator.load_expression_file(toml_file)

    mock_post = MagicMock()
    mock_post.fields_calculator = mock_fields_calculator

    mock_modeler = MagicMock()
    mock_modeler.convert_to_selections.return_value = AEDT_APPLICATION_SELECTIONS

    mock_aedt_application = MagicMock()
    mock_aedt_application.post = mock_post
    mock_aedt_application.modeler = mock_modeler
    mock_aedt_application.design_type = "HFSS"
    mock_aedt_application.solution_type = "Transient"
    mock_aedt_application.existing_analysis_sweeps = [AEDT_APPLICATION_SETUP]

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = mock_aedt_application
        yield mock_aedt_application


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_advanced_fields_calculator_extension_default(mock_desktop, mock_aedt_app_with_expression_catalog):
    """Test instantiation of the Advanced Fields Calculator extension."""
    mock_desktop.return_value = MagicMock()

    extension = AdvancedFieldsCalculatorExtension()

    assert EXTENSION_TITLE == extension.root.title()
    assert EXPRESSION_DESCRIPTION in extension.root.nametowidget("combo_calculation")["values"]
    assert AEDT_APPLICATION_SETUP in extension.root.nametowidget("combo_setup")["values"]
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_advanced_fields_calculator_extension_load_custom(
    mock_desktop, tmp_path, mock_aedt_app_with_expression_catalog
):
    """Test loading a custom expression catalog in the Advanced Fields Calculator extension."""
    import tomli_w

    mock_desktop.return_value = MagicMock()

    # Set the working directory to the temporary path to test loading local expression catalog
    os.chdir(tmp_path)
    expression_catalog_path = Path(tmp_path, "expression_catalog_custom.toml")
    other_content = EXPRESSION_CONTENT.copy()
    other_content["description"] = "Other description"
    other_catalog = {"Other tag": other_content}
    with expression_catalog_path.open("wb") as fp:
        tomli_w.dump(other_catalog, fp)

    extension = AdvancedFieldsCalculatorExtension()

    mock_aedt_app_with_expression_catalog.post.fields_calculator.load_expression_file.assert_called_once_with(
        expression_catalog_path
    )
    assert "Other description" in extension.root.nametowidget("combo_calculation")["values"]

    extension.root.destroy()
    os.remove(expression_catalog_path)


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_advanced_fields_calculator_extension_ok_button(mock_desktop, mock_aedt_app_with_expression_catalog):
    """Test instantiation of the Advanced Fields Calculator extension."""

    mock_desktop.return_value = MagicMock()

    extension = AdvancedFieldsCalculatorExtension()
    assert "Other description" in extension.root.nametowidget("combo_calculation")["values"]
    extension.root.nametowidget("ok_button").invoke()
    data: AdvancedFieldsCalculatorExtensionData = extension.data

    assert EXPRESSION_TAG == data.calculation
    assert AEDT_APPLICATION_SETUP == data.setup
    assert AEDT_APPLICATION_SELECTIONS == data.assignments


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_advanced_fields_calculator_extension_with_ui(mock_desktop, mock_aedt_app_with_expression_catalog):
    """Test that the default values of the UI are set correctly."""
    mock_desktop.return_value = MagicMock()

    extension = AdvancedFieldsCalculatorExtension(withdraw=False)
    extension.root.update()
    extension.root.destroy()

    assert extension.data is None
