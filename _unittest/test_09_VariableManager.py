# Setup paths for module imports
from __future__ import division  # noreorder

import math

from _unittest.conftest import BasisTest
from pyaedt import MaxwellCircuit
from pyaedt.application.Variables import Variable
from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.general_methods import isclose
from pyaedt.modeler.GeometryOperators import GeometryOperators

# Import required modules

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, "Test_09")

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_set_globals(self):
        var = self.aedtapp.variable_manager
        self.aedtapp["$Test_Global1"] = "5rad"
        self.aedtapp["$Test_Global2"] = -1.0
        self.aedtapp["$Test_Global3"] = "0"
        self.aedtapp["$Test_Global4"] = "$Test_Global2*$Test_Global1"
        independent = self.aedtapp._variable_manager.independent_variable_names
        dependent = self.aedtapp._variable_manager.dependent_variable_names
        val = var["$Test_Global4"]
        assert val.numeric_value == -5.0
        assert "$Test_Global1" in independent
        assert "$Test_Global2" in independent
        assert "$Test_Global3" in independent
        assert "$Test_Global4" in dependent
        pass

    def test_01_set_var_simple(self):
        var = self.aedtapp.variable_manager
        self.aedtapp["Var1"] = "1rpm"
        var_1 = self.aedtapp["Var1"]
        var_2 = var["Var1"].expression
        assert var_1 == var_2
        assert isclose(var["Var1"].numeric_value, 1.0)
        pass

    def test_02_test_formula(self):
        self.aedtapp["Var1"] = 3
        self.aedtapp["Var2"] = "12deg"
        self.aedtapp["Var3"] = "Var1 * Var2"

        self.aedtapp["$PrjVar1"] = "2*pi"
        self.aedtapp["$PrjVar2"] = 45
        self.aedtapp["$PrjVar3"] = "sqrt(34 * $PrjVar2/$PrjVar1 )"

        v = self.aedtapp.variable_manager
        for var_name in v.variable_names:
            print("{} = {}".format(var_name, self.aedtapp[var_name]))
        pass
        tol = 1e-9
        c2pi = math.pi * 2.0
        assert abs(v["$PrjVar1"].numeric_value - c2pi) < tol
        assert abs(v["$PrjVar3"].numeric_value - math.sqrt(34 * 45.0 / c2pi)) < tol
        assert abs(v["Var3"].numeric_value - 3.0 * 12.0) < tol
        assert v["Var3"].units == "deg"

    def test_03_test_evaluated_value(self):

        self.aedtapp["p1"] = "10mm"
        self.aedtapp["p2"] = "20mm"
        self.aedtapp["p3"] = "p1 * p2"
        v = self.aedtapp.variable_manager

        eval_p3_nom = v._app.get_evaluated_value("p3")
        assert isclose(eval_p3_nom, 0.0002)
        v_app = self.aedtapp.variable_manager
        assert v_app["p1"].read_only == False
        v_app["p1"].read_only = True
        assert v_app["p1"].read_only == True
        assert v_app["p1"].hidden == False
        v_app["p1"].hidden = True
        assert v_app["p1"].hidden == True
        assert v_app["p2"].description == ""
        v_app["p2"].description = "myvar"
        assert v_app["p2"].description == "myvar"
        assert v_app["p2"].expression == "20mm"
        v_app["p2"].expression = "5rad"
        assert v_app["p2"].expression == "5rad"

    def test_04_set_variable(self):

        assert self.aedtapp.variable_manager.set_variable("p1", expression="10mm")
        assert self.aedtapp["p1"] == "10mm"
        assert self.aedtapp.variable_manager.set_variable("p1", expression="20mm", overwrite=False)
        assert self.aedtapp["p1"] == "10mm"
        assert self.aedtapp.variable_manager.set_variable("p1", expression="30mm")
        assert self.aedtapp["p1"] == "30mm"
        assert self.aedtapp.variable_manager.set_variable(
            variable_name="p2",
            expression="10mm",
            readonly=True,
            hidden=True,
            description="This is a description of this variable",
        )
        assert self.aedtapp.variable_manager.set_variable("$p1", expression="10mm")

    def test_05_variable_class(self):

        v = Variable("4mm")
        num_value = v.numeric_value
        assert num_value == 4.0

        v = v.rescale_to("meter")
        test = v.evaluated_value
        assert v.numeric_value == 0.004

        v = Variable("100cel")
        v.rescale_to("fah")
        assert v.numeric_value == 212.0
        pass

    def test_06_multiplication(self):

        v1 = Variable("10mm")
        v2 = Variable(3)
        v3 = Variable("3mA")
        v4 = Variable("40V")
        v5 = Variable("100NewtonMeter")
        v6 = Variable("1000rpm")
        tol = 1e-4
        result_1 = v1 * v2
        result_2 = v2 * v3
        result_3 = v3 * v4
        result_4 = v4 * v3
        result_5 = v4 * 24.0 * v3
        result_6 = v5 * v6
        result_7 = v6 * v5
        result_8 = (v5 * v6).rescale_to("kW")
        assert result_1.numeric_value == 30.0
        assert result_1.unit_system == "Length"

        assert result_2.numeric_value == 9.0
        assert result_2.units == "mA"
        assert result_2.unit_system == "Current"

        assert result_3.numeric_value == 0.12
        assert result_3.units == "W"
        assert result_3.unit_system == "Power"

        assert result_4.numeric_value == 0.12
        assert result_4.units == "W"
        assert result_4.unit_system == "Power"

        assert result_5.numeric_value == 2.88
        assert result_5.units == "W"
        assert result_5.unit_system == "Power"

        assert abs(result_6.numeric_value - 10471.9755) / result_6.numeric_value < tol
        assert result_6.units == "W"
        assert result_6.unit_system == "Power"

        assert abs(result_7.numeric_value - 10471.9755) / result_4.numeric_value < tol
        assert result_7.units == "W"
        assert result_7.unit_system == "Power"

        assert abs(result_8.numeric_value - 10.4719755) / result_8.numeric_value < tol
        assert result_8.units == "kW"
        assert result_8.unit_system == "Power"

    def test_07_addition(self):

        v1 = Variable("10mm")
        v2 = Variable(3)
        v3 = Variable("3mA")
        v4 = Variable("10A")

        try:
            v1 + v2
            assert False
        except AssertionError:
            pass

        try:
            v2 + v1
            assert False
        except AssertionError:
            pass
        result_1 = v2 + v2
        result_2 = v3 + v4
        result_3 = v3 + v3

        assert result_1.numeric_value == 6.0
        assert result_1.unit_system == "None"

        assert result_2.numeric_value == 10.003
        assert result_2.units == "A"
        assert result_2.unit_system == "Current"

        assert result_3.numeric_value == 6.0
        assert result_3.units == "mA"
        assert result_3.unit_system == "Current"

    def test_08_subtraction(self):

        v1 = Variable("10mm")
        v2 = Variable(3)
        v3 = Variable("3mA")
        v4 = Variable("10A")

        try:
            v1 - v2
            assert False
        except AssertionError:
            pass

        try:
            v2 - v1
            assert False
        except AssertionError:
            pass

        result_1 = v2 - v2
        result_2 = v3 - v4
        result_3 = v3 - v3

        assert result_1.numeric_value == 0.0
        assert result_1.unit_system == "None"

        assert result_2.numeric_value == -9.997
        assert result_2.units == "A"
        assert result_2.unit_system == "Current"

        assert result_3.numeric_value == 0.0
        assert result_3.units == "mA"
        assert result_3.unit_system == "Current"

    def test_09_specify_units(self):

        # Scaling of the unit system "Angle"
        angle = Variable("1rad")
        angle.rescale_to("deg")
        assert isclose(angle.numeric_value, 57.29577951308232)
        angle.rescale_to("degmin")
        assert isclose(angle.numeric_value, 57.29577951308232 * 60.0)
        angle.rescale_to("degsec")
        assert isclose(angle.numeric_value, 57.29577951308232 * 3600.0)

        # Convert 200Hz to Angular speed numerically
        omega = Variable(200 * math.pi * 2, "rad_per_sec")
        assert omega.unit_system == "AngularSpeed"
        assert isclose(omega.value, 1256.6370614359173)
        omega.rescale_to("rpm")
        assert isclose(omega.numeric_value, 12000.0)
        omega.rescale_to("rev_per_sec")
        assert isclose(omega.numeric_value, 200.0)

        # test speed times time equals diestance
        v = Variable("100m_per_sec")
        assert v.unit_system == "Speed"
        v.rescale_to("feet_per_sec")
        assert isclose(v.numeric_value, 328.08398950131)
        v.rescale_to("feet_per_min")
        assert isclose(v.numeric_value, 328.08398950131 * 60)
        v.rescale_to("miles_per_sec")
        assert isclose(v.numeric_value, 0.06213711723534)
        v.rescale_to("miles_per_minute")
        assert isclose(v.numeric_value, 3.72822703412)
        v.rescale_to("miles_per_hour")
        assert isclose(v.numeric_value, 223.69362204724)

        t = Variable("20s")
        distance = v * t
        assert distance.unit_system == "Length"
        assert distance.evaluated_value == "2000.0meter"
        distance.rescale_to("in")
        assert isclose(distance.numeric_value, 2000 / 0.0254)

    def test_10_division(self):
        """
        'Power_divide_Voltage': 'Current',
        'Power_divide_Current': 'Voltage',
        'Power_divide_AngularSpeed': 'Torque',
        'Power_divide_Torque': 'Angular_Speed',
        'Angle_divide_AngularSpeed': 'Time',
        'Angle_divide_Time': 'AngularSpeed',
        'Voltage_divide_Current': 'Resistance',
        'Voltage_divide_Resistance': 'Current',
        'Resistance_divide_AngularSpeed': 'Inductance',
        'Resistance_divide_Inductance': 'AngularSpeed',
        'None_divide_Freq': 'Time',
        'None_divide_Time': 'Freq',
        'Length_divide_Time': 'Speed',
        'Length_divide_Speed': 'Time'
        """

        v1 = Variable("10W")
        v2 = Variable("40V")
        v3 = Variable("1s")
        v4 = Variable("5mA")
        v5 = Variable("100NewtonMeter")
        v6 = Variable("1000rpm")
        tol = 1e-4

        result_1 = v1 / v2
        assert result_1.numeric_value == 0.25
        assert result_1.units == "A"
        assert result_1.unit_system == "Current"

        result_2 = v2 / result_1
        assert result_2.numeric_value == 160.0
        assert result_2.units == "ohm"
        assert result_2.unit_system == "Resistance"

        result_3 = 3 / v3
        assert result_3.numeric_value == 3.0
        assert result_3.units == "Hz"
        assert result_3.unit_system == "Freq"

        result_4 = v3 / 2
        assert abs(result_4.numeric_value - 0.5) < tol
        assert result_4.units == "s"
        assert result_4.unit_system == "Time"

        result_5 = v4 / v5
        assert abs(result_5.numeric_value - 0.00005) < tol
        assert result_5.units == ""
        assert result_5.unit_system == "None"

        result_6 = v1 / v5 + v6
        assert abs(result_6.numeric_value - 104.8198) / result_6.numeric_value < tol
        assert result_6.units == "rad_per_sec"
        assert result_6.unit_system == "AngularSpeed"

    def test_11_delete_variable(self):
        assert self.aedtapp.variable_manager.delete_variable("Var1")

    def test_12_decompose_variable_value(self):
        assert decompose_variable_value("3.123456m") == (3.123456, "m")
        assert decompose_variable_value("3m") == (3, "m")
        assert decompose_variable_value("3") == (3, "")
        assert decompose_variable_value("3.") == (3.0, "")
        assert decompose_variable_value("3.123456m2") == (3.123456, "m2")
        assert decompose_variable_value("3.123456Nm-2") == (3.123456, "Nm-2")
        assert decompose_variable_value("3.123456kg2m2") == (3.123456, "kg2m2")
        assert decompose_variable_value("3.123456kgm2") == (3.123456, "kgm2")

    def test_13_postprocessing(self):
        v1 = self.aedtapp.variable_manager.set_variable("test_post1", 10, postprocessing=True)
        assert v1
        assert not self.aedtapp.variable_manager.set_variable("test2", "v1+1")
        assert self.aedtapp.variable_manager.set_variable("test2", "test_post1+1", postprocessing=True)
        x1 = GeometryOperators.parse_dim_arg(
            self.aedtapp.variable_manager["test2"].evaluated_value, variable_manager=self.aedtapp.variable_manager
        )
        assert x1 == 11

    def test_14_intrinsics(self):
        self.aedtapp["fc"] = "Freq"
        assert self.aedtapp["fc"] == "Freq"
        assert self.aedtapp.variable_manager.dependent_variables["fc"].numeric_value == 1e9

    def test_15_arrays(self):
        self.aedtapp["arr_index"] = 0
        self.aedtapp["arr1"] = "[1, 2, 3]"
        self.aedtapp["arr2"] = [1, 2, 3]
        self.aedtapp["getvalue1"] = "arr1[arr_index]"
        self.aedtapp["getvalue2"] = "arr2[arr_index]"
        assert self.aedtapp.variable_manager["getvalue1"].numeric_value == 1.0
        assert self.aedtapp.variable_manager["getvalue2"].numeric_value == 1.0

    def test_16_maxwell_circuit_variables(self):
        mc = MaxwellCircuit()
        mc["var2"] = "10mm"
        assert mc["var2"] == "10mm"
        v_circuit = mc.variable_manager
        var_circuit = v_circuit.variable_names
        assert "var2" in var_circuit
        assert v_circuit.independent_variables["var2"].units == "mm"
        mc["var3"] = "10deg"
        mc["var4"] = "10rad"
        assert mc["var3"] == "10deg"
        assert mc["var4"] == "10rad"

    def test_17_project_sweep_variable(self):
        self.aedtapp["$my_proj_test"] = "1mm"
        self.aedtapp["$my_proj_test2"] = 2
        self.aedtapp["$my_proj_test3"] = "$my_proj_test*$my_proj_test2"
        assert self.aedtapp.variable_manager["$my_proj_test3"].units == "mm"
        assert self.aedtapp.variable_manager["$my_proj_test3"].numeric_value == 2.0
        self.aedtapp.materials.add_material_sweep(["copper", "aluminum"], "sweep_alu")
        assert "$sweep_alupermittivity" in self.aedtapp.variable_manager.dependent_variables

    def test_18_test_optimization_properties(self):
        var = "v1"
        self.aedtapp[var] = "10mm"

        v = self.aedtapp.variable_manager
        assert not v[var].is_optimization_enabled
        v[var].is_optimization_enabled = True
        assert v[var].is_optimization_enabled
        assert v[var].optimization_min_value == "5mm"
        v[var].optimization_min_value = "4mm"
        assert v[var].optimization_min_value == "4mm"
        assert v[var].optimization_max_value == "15mm"
        v[var].optimization_max_value = "14mm"
        assert v[var].optimization_max_value == "14mm"
        assert not v[var].is_tuning_enabled
        v[var].is_tuning_enabled = True
        assert v[var].is_tuning_enabled
        assert v[var].tuning_min_value == "5mm"
        v[var].tuning_min_value = "4mm"
        assert v[var].tuning_min_value == "4mm"
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
        assert v[var].sensitivity_min_value == "4mm"
        assert v[var].sensitivity_max_value == "15mm"
        v[var].sensitivity_max_value = "14mm"
        assert v[var].sensitivity_max_value == "14mm"
        assert v[var].sensitivity_initial_disp == "1mm"
        v[var].sensitivity_initial_disp = "0.5mm"
        assert v[var].sensitivity_initial_disp == "0.5mm"

    def test_19_test_optimization_global_properties(self):

        var = "$v1"
        self.aedtapp[var] = "10mm"
        v = self.aedtapp.variable_manager
        assert not v[var].is_optimization_enabled
        v[var].is_optimization_enabled = True
        assert v[var].is_optimization_enabled
        assert v[var].optimization_min_value == "5mm"
        v[var].optimization_min_value = "4mm"
        assert v[var].optimization_min_value == "4mm"
        assert v[var].optimization_max_value == "15mm"
        v[var].optimization_max_value = "14mm"
        assert v[var].optimization_max_value == "14mm"
        assert not v[var].is_tuning_enabled
        v[var].is_tuning_enabled = True
        assert v[var].is_tuning_enabled
        assert v[var].tuning_min_value == "5mm"
        v[var].tuning_min_value = "4mm"
        assert v[var].tuning_min_value == "4mm"
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
        assert v[var].sensitivity_min_value == "4mm"
        assert v[var].sensitivity_max_value == "15mm"
        v[var].sensitivity_max_value = "14mm"
        assert v[var].sensitivity_max_value == "14mm"
        assert v[var].sensitivity_initial_disp == "1mm"
        v[var].sensitivity_initial_disp = "0.5mm"
        assert v[var].sensitivity_initial_disp == "0.5mm"
