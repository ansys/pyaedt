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


import pytest

from ansys.aedt.core import Hfss

test_subfolder = "fields_calculator"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name)


class TestClass:
    def test_add_expressions(self, aedtapp):
        """Test adding custom field calculator expressions."""
        poly = aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        my_expression = {
            "name": "test",
            "description": "Voltage drop along a line",
            "design_type": ["HFSS", "Q3D Extractor"],
            "fields_type": ["Fields", "CG Fields"],
            "solution_type": "",
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
        expr_name = aedtapp.post.fields_calculator.add_expression(my_expression, poly.name)
        assert isinstance(expr_name, str)
        assert expr_name == "test"

    def test_expression_plot(self, aedtapp):
        """Test creating plots from field calculator expressions."""
        aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        aedtapp.create_setup()
        expr_name = aedtapp.post.fields_calculator.add_expression("voltage_line", "Polyline1")
        reports = aedtapp.post.fields_calculator.expression_plot("voltage_line", "Polyline1", [expr_name])
        assert reports
        assert aedtapp.post.plots
        assert reports == aedtapp.post.plots
        assert reports[0].expressions == ["Voltage_Line"]

    def test_delete_expression(self, aedtapp):
        """Test deleting named expressions from the fields calculator."""
        poly = aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        expressions = aedtapp.post.fields_calculator.get_expressions()
        assert "Voltage_Line" not in list(expressions.keys())
        expr_name = aedtapp.post.fields_calculator.add_expression("voltage_line", poly.name)
        expressions = aedtapp.post.fields_calculator.get_expressions()
        assert "Voltage_Line" in list(expressions.keys())
        aedtapp.post.fields_calculator.delete_expression(expr_name)
        expressions = aedtapp.post.fields_calculator.get_expressions()
        assert "Voltage_Line" not in list(expressions.keys())

    def test_is_expression_defined(self, aedtapp):
        """Test checking if a named expression exists in the fields calculator."""
        aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        aedtapp.create_setup()
        assert not aedtapp.post.fields_calculator.is_expression_defined("Voltage_Line")
        expr_name = aedtapp.post.fields_calculator.add_expression("voltage_line", "Polyline1")
        assert aedtapp.post.fields_calculator.is_expression_defined(expr_name)

    def test_is_general_expression(self, aedtapp):
        """Test identifying general vs. assignment-specific expressions."""
        aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="Polyline1")
        aedtapp.create_setup()
        assert not aedtapp.post.fields_calculator.is_general_expression("invalid")
        assert not aedtapp.post.fields_calculator.is_general_expression("voltage_line")
        assert aedtapp.post.fields_calculator.is_general_expression("voltage_drop")

    def test_validate_expression(self, aedtapp):
        """Test expression validation against the schema."""
        assert not aedtapp.post.fields_calculator.validate_expression("invalid")
