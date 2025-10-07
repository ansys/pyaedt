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

import math

import pytest

import ansys.aedt.core as pyaedt
from ansys.aedt.core.generic.numbers_utils import is_close
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators


@pytest.fixture(
    params=[
        pyaedt.Circuit,
        pyaedt.Hfss,
        pyaedt.Icepak,
        pyaedt.Mechanical,
        pyaedt.Maxwell3d,
        pyaedt.Maxwell2d,
        pyaedt.Q3d,
        pyaedt.Q2d,
        pyaedt.Hfss3dLayout,
        pyaedt.Rmxprt,
        pyaedt.TwinBuilder,
    ],
    ids=[
        "circuit",
        "hfss",
        "icepak",
        "mechanical",
        "maxwell_3d",
        "maxwell_2d",
        "q3d",
        "q2d",
        "hfss3d_layout",
        "rmxprt",
        "twin_builder",
    ],
)
def app(request, add_app):
    app = add_app(application=request.param)
    yield app
    app.close_project(app.project_name)


@pytest.fixture
def hfss_app(add_app):
    app = add_app(application=pyaedt.Hfss)
    yield app
    app.close_project(app.project_name)


@pytest.fixture
def maxwell_circuit_app(add_app):
    app = add_app(application=pyaedt.MaxwellCircuit)
    yield app
    app.close_project(app.project_name)


class TestClass:
    def test_set_project_variables(self, hfss_app):
        hfss_app["$Test_Global1"] = "5rad"
        hfss_app["$Test_Global2"] = -1.0
        hfss_app["$Test_Global3"] = "0"
        hfss_app["$Test_Global4"] = "$Test_Global2*$Test_Global1"
        independent = hfss_app._variable_manager.independent_variable_names
        dependent = hfss_app._variable_manager.dependent_variable_names
        assert hfss_app.variable_manager.variables["$Test_Global4"].numeric_value == -5.0
        assert "$Test_Global1" in independent
        assert "$Test_Global2" in independent
        assert "$Test_Global3" in independent
        assert "$Test_Global4" in dependent

        hfss_app["$test"] = "1mm"
        hfss_app["$test2"] = "$test"
        assert "$test2" in hfss_app.variable_manager.dependent_project_variable_names
        assert "$test" in hfss_app.variable_manager.independent_project_variable_names
        del hfss_app["$test2"]
        assert "$test2" not in hfss_app.variable_manager.variables
        del hfss_app["$test"]
        assert "$test" not in hfss_app.variable_manager.variables

    def test_set_var_simple(self, app):
        var = app.variable_manager
        app["Var1"] = "1rpm"
        var_1 = app["Var1"]
        var_2 = var["Var1"].expression
        assert var_1 == var_2
        assert is_close(var["Var1"].numeric_value, 1.0)

        # Test all properties
        assert var["Var1"].evaluated_value == "1.0rpm"

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            assert var["Var1"].description is None
        else:
            assert var["Var1"].description == ""

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            assert var["Var1"].hidden is None
        else:
            assert not var["Var1"].hidden

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            assert var["Var1"].read_only is None
        else:
            assert not var["Var1"].read_only

        assert is_close(var["Var1"].value, 0.104719, relative_tolerance=1e-4)

        assert var["Var1"].expression == "1rpm"

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            assert var["Var1"].is_optimization_enabled is None
        else:
            assert not var["Var1"].is_optimization_enabled

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            assert var["Var1"].is_sensitivity_enabled is None
        else:
            assert not var["Var1"].is_sensitivity_enabled

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            assert var["Var1"].is_statistical_enabled is None
        else:
            assert not var["Var1"].is_statistical_enabled

        assert not var["Var1"].post_processing

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            assert var["Var1"].sweep is None
        else:
            assert var["Var1"].sweep

        assert var["Var1"].units == "rpm"

        app["test"] = "1mm"
        app["test2"] = "test"
        assert "test2" in app.variable_manager.dependent_design_variable_names
        del app["test2"]
        assert "test2" not in app.variable_manager.variables
        del app["test"]
        assert "test" not in app.variable_manager.variables

    def test_test_formula(self, app):
        app["Var1"] = 3
        app["Var2"] = "12deg"
        app["Var3"] = "Var1 * Var2"

        assert app.variable_manager.variables["Var3"].numeric_value == 36.0
        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            assert app.variable_manager.variables["Var3"].circuit_parameter
        else:
            assert not app.variable_manager.variables["Var3"].circuit_parameter

        assert app.variable_manager.variables["Var3"].units == "deg"

        app["$PrjVar1"] = "2*pi"
        app["$PrjVar2"] = 45
        app["$PrjVar3"] = "sqrt(34 * $PrjVar2/$PrjVar1 )"

        tol = 1e-9
        c2pi = math.pi * 2.0
        assert abs(app.variable_manager.variables["$PrjVar1"].numeric_value - c2pi) < tol
        assert abs(app.variable_manager.variables["$PrjVar3"].numeric_value - math.sqrt(34 * 45.0 / c2pi)) < tol
        assert abs(app.variable_manager.variables["Var3"].numeric_value - 3.0 * 12.0) < tol
        assert app.variable_manager.variables["Var3"].units == "deg"

    def test_evaluated_value(self, app):
        app["p1"] = "10mm"
        app.variable_manager.set_variable("p2", "20mm", circuit_parameter=False)
        app["p3"] = "p1 * p2"
        v = app.variable_manager

        eval_p3_nom = v._app.get_evaluated_value("p3")
        assert is_close(eval_p3_nom, 0.0002)

        eval_p3_nom_mm = v._app.get_evaluated_value("p3", "mm")
        assert is_close(eval_p3_nom_mm, 0.2)

        v_app = app.variable_manager
        assert v_app["p2"].sweep
        v_app["p2"].sweep = False
        assert not v_app["p2"].sweep

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            # Circuit parameter
            assert v_app["p1"].sweep is None
            v_app["p1"].sweep = False
            assert v_app["p1"] is not None

        assert not v_app["p2"].read_only
        v_app["p2"].read_only = True
        assert v_app["p2"].read_only

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            # Circuit parameter
            assert v_app["p1"].read_only is None
            v_app["p1"].read_only = True
            assert v_app["p1"] is not None

        assert not v_app["p2"].hidden
        v_app["p2"].hidden = True
        assert v_app["p2"].hidden

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            # Circuit parameter
            assert v_app["p1"].hidden is None
            v_app["p1"].hidden = False
            assert v_app["p1"] is not None

        assert v_app["p2"].description == ""
        v_app["p2"].description = "myvar"
        assert v_app["p2"].description == "myvar"

        if app.design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design"]:
            # Circuit parameter
            assert v_app["p1"].description is None
            v_app["p1"].description = False
            assert v_app["p1"] is not None

        assert v_app["p2"].expression == "20mm"
        v_app["p2"].expression = "5rad"
        assert v_app["p2"].expression == "5rad"

        assert v_app["p1"].expression == "10mm"
        v_app["p1"].expression = "5mm"
        assert v_app["p1"].expression == "5mm"

    def test_set_variable(self, app):
        assert app.variable_manager.set_variable("p1", expression="10mm", circuit_parameter=False)
        assert app["p1"] == "10mm"
        assert not app.variable_manager.variables["p1"].circuit_parameter
        assert app.variable_manager.variables["p1"].numeric_value == 10.0
        assert app.variable_manager.set_variable("p1", expression="20mm", overwrite=False)
        assert app["p1"] == "10mm"
        assert app.variable_manager.set_variable("p1", expression="30mm")
        assert app["p1"] == "30mm"

        assert app.variable_manager.set_variable(
            name="p2",
            expression="10mm",
            read_only=True,
            hidden=True,
            description="This is a description of this variable",
        )
        assert app.variable_manager.set_variable("$p1", expression="10mm")
        assert app.variable_manager.set_variable("$p1", expression="12mm")

    def test_delete_variable(self, app):
        app["Var1"] = 1
        assert app.variable_manager.delete_variable("Var1")

    def test_postprocessing(self, app):
        if app.design_type == "Twin Builder":
            pytest.skip("Twin Builder is crashing for this test.")

        v1 = app.variable_manager.set_variable("test_post1", 10, is_post_processing=True, circuit_parameter=False)
        assert v1
        assert not app.variable_manager.set_variable("test2", "v1+1")
        assert app.variable_manager.set_variable(
            "test2", "test_post1+1", is_post_processing=True, circuit_parameter=False
        )
        x1 = GeometryOperators.parse_dim_arg(
            app.variable_manager["test2"].evaluated_value, variable_manager=app.variable_manager
        )
        assert x1 == 11.0

    def test_intrinsics(self, app):
        app["fc"] = "Freq"
        assert app["fc"] == "Freq"
        assert app.variable_manager.dependent_variables["fc"].units == app.units.frequency

    def test_arrays(self, app):
        app["arr_index"] = 0
        app["arr1"] = "[1, 2, 3]"
        app["arr2"] = [1, 2, 3]
        app["getvalue1"] = "arr1[arr_index]"
        app["getvalue2"] = "arr2[arr_index]"
        assert app.variable_manager["getvalue1"].numeric_value == 1.0
        assert app.variable_manager["getvalue2"].numeric_value == 1.0

    def test_maxwell_circuit_variables(self, maxwell_circuit_app):
        maxwell_circuit_app["var2"] = "10mm"
        assert maxwell_circuit_app["var2"] == "10mm"
        v_circuit = maxwell_circuit_app.variable_manager
        var_circuit = v_circuit.variable_names
        assert "var2" in var_circuit
        assert v_circuit.independent_variables["var2"].units == "mm"
        maxwell_circuit_app["var3"] = "10deg"
        maxwell_circuit_app["var4"] = "10rad"
        assert maxwell_circuit_app["var3"] == "10deg"
        assert maxwell_circuit_app["var4"] == "10rad"

    def test_project_variable_operation(self, app):
        app["$my_proj_test"] = "1mm"
        app["$my_proj_test2"] = 2
        app["$my_proj_test3"] = "$my_proj_test*$my_proj_test2"
        assert app.variable_manager["$my_proj_test3"].units == "mm"
        assert app.variable_manager["$my_proj_test3"].numeric_value == 2.0

    def test_test_optimization_properties(self, app):
        var = "v1"
        app[var] = "10mm"
        v = app.variable_manager
        assert not v[var].is_optimization_enabled
        v[var].is_optimization_enabled = True
        assert v[var].is_optimization_enabled
        assert v[var].optimization_min_value == "5mm"
        v[var].optimization_min_value = "1m"
        assert v[var].optimization_max_value == "15mm"
        v[var].optimization_max_value = "14mm"
        assert v[var].optimization_max_value == "14mm"
        assert not v[var].is_tuning_enabled
        v[var].is_tuning_enabled = True
        assert v[var].is_tuning_enabled
        assert v[var].tuning_min_value == "5mm"
        v[var].tuning_min_value = "4mm"
        assert v[var].tuning_max_value == "15mm"
        v[var].tuning_max_value = "14mm"
        assert v[var].tuning_max_value == "14mm"
        assert v[var].tuning_step_value == "1mm"
        v[var].tuning_step_value = "0.5mm"
        assert v[var].tuning_step_value == "0.5mm"
        assert not v[var].is_statistical_enabled
        v[var].is_statistical_enabled = True
        assert v[var].is_statistical_enabled
        assert not v[var].is_sensitivity_enabled
        v[var].is_sensitivity_enabled = True
        assert v[var].is_sensitivity_enabled
        assert v[var].sensitivity_min_value == "5mm"
        v[var].sensitivity_min_value = "4mm"
        assert v[var].sensitivity_max_value == "15mm"
        v[var].sensitivity_max_value = "14mm"
        assert v[var].sensitivity_max_value == "14mm"
        assert v[var].sensitivity_initial_disp == "1mm"
        v[var].sensitivity_initial_disp = "0.5mm"
        assert v[var].sensitivity_initial_disp == "0.5mm"

    def test_test_optimization_global_properties(self, app):
        var = "$v1"
        app[var] = "10mm"
        v = app.variable_manager
        assert not v[var].is_optimization_enabled
        v[var].is_optimization_enabled = True
        assert v[var].is_optimization_enabled
        assert v[var].optimization_min_value == "5mm"
        v[var].optimization_min_value = "4mm"
        assert v[var].optimization_max_value == "15mm"
        v[var].optimization_max_value = "14mm"
        assert v[var].optimization_max_value == "14mm"
        assert not v[var].is_tuning_enabled
        v[var].is_tuning_enabled = True
        assert v[var].is_tuning_enabled
        assert v[var].tuning_min_value == "5mm"
        v[var].tuning_min_value = "4mm"
        assert v[var].tuning_max_value == "15mm"
        v[var].tuning_max_value = "14mm"
        assert v[var].tuning_max_value == "14mm"
        assert v[var].tuning_step_value == "1mm"
        v[var].tuning_step_value = "0.5mm"
        assert v[var].tuning_step_value == "0.5mm"
        assert not v[var].is_statistical_enabled
        v[var].is_statistical_enabled = True
        assert v[var].is_statistical_enabled
        assert not v[var].is_sensitivity_enabled
        v[var].is_sensitivity_enabled = True
        assert v[var].is_sensitivity_enabled
        assert v[var].sensitivity_min_value == "5mm"
        v[var].sensitivity_min_value = "4mm"
        assert v[var].sensitivity_max_value == "15mm"
        v[var].sensitivity_max_value = "14mm"
        assert v[var].sensitivity_max_value == "14mm"
        assert v[var].sensitivity_initial_disp == "1mm"
        v[var].sensitivity_initial_disp = "0.5mm"
        assert v[var].sensitivity_initial_disp == "0.5mm"

    def test_variable_with_units(self, app):
        app["v1"] = "3mm"
        app["v2"] = "2*v1"
        assert app.variable_manager.decompose("v1") == (3.0, "mm")
        assert app.variable_manager.decompose("v2") == (6.0, "mm")
        assert app.variable_manager["v2"].decompose() == (6.0, "mm")
        assert app.variable_manager.decompose("5mm") == (5.0, "mm")

    def test_delete_unused_variables(self, app):
        app.insert_design("used_variables")
        app["used_var"] = "1mm"
        app["unused_var"] = "1mm"
        app["$project_used_var"] = "1"
        app.modeler.create_rectangle(0, ["used_var", "used_var", "used_var"], [10, 20])
        mat1 = app.materials.add_material("new_copper2")
        mat1.permittivity = "$project_used_var"
        assert app.variable_manager.is_used("used_var")
        assert not app.variable_manager.is_used("unused_var")
        assert app.variable_manager.delete_variable("unused_var")
        app["unused_var"] = "1mm"
        number_of_variables = len(app.variable_manager.variable_names)
        assert app.variable_manager.delete_unused_variables()
        new_number_of_variables = len(app.variable_manager.variable_names)
        assert number_of_variables != new_number_of_variables

    def test_value_with_units(self, app):
        assert app.value_with_units("10mm") == "10mm"
        assert app.value_with_units("10") == "10mm"
        assert app.value_with_units("10", units_system="Angle") == "10deg"
        assert app.value_with_units("10", units_system="invalid") == "10"
        assert app.value_with_units("A + Bmm") == "A + Bmm"
