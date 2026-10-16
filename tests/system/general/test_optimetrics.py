# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
from ansys.aedt.core.generic.constants import Setups
from ansys.aedt.core.generic.props import Props
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.design_xploration import Optimetrics
from ansys.aedt.core.modules.design_xploration import Optimizations
from ansys.aedt.core.modules.design_xploration import OptimizationSetup
from ansys.aedt.core.modules.design_xploration import Parametrics
from ansys.aedt.core.modules.design_xploration import ParametricSetup

TEST_SUBFOLDER = "T11"
TEST_COAXIAL = "coax_setup_231"


@pytest.fixture
def aedtapp(add_app_example):
    app = add_app_example(application=Hfss, project=TEST_COAXIAL, subfolder=TEST_SUBFOLDER, design="HFSSDesign")
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def optimetrics_app(add_app_example):
    app = add_app_example(application=Hfss, project=TEST_COAXIAL, subfolder=TEST_SUBFOLDER, design="optimetrics_design")
    yield app
    app.close_project(app.project_name, save=False)


def test_optimetrics_init(optimetrics_app):
    assert isinstance(optimetrics_app.optimetrics, Optimetrics)
    assert isinstance(optimetrics_app.optimizations, Optimizations)
    assert isinstance(optimetrics_app.parametrics, Parametrics)

    assert isinstance(optimetrics_app.optimetrics.optimizations, Optimizations)
    assert isinstance(optimetrics_app.optimetrics.parametrics, Parametrics)

    assert len(optimetrics_app.optimizations.setups) == 1
    assert len(optimetrics_app.optimizations.setups_by_type) == 1
    assert optimetrics_app.optimizations.setups[0].setup_type == "optiSLang"

    assert optimetrics_app.optimizations.setups[0].properties
    assert optimetrics_app.optimizations.setups[0].public_dir

    assert len(optimetrics_app.parametrics.setups) == 1
    assert len(optimetrics_app.parametrics.setups_by_type) == 1
    assert optimetrics_app.parametrics.setups[0].setup_type == "OptiParametric"

    assert len(optimetrics_app.optimetrics.setups) == 2
    assert len(optimetrics_app.optimetrics.setup_names) == 2

    parametric_name = optimetrics_app.parametrics.setup_names[0]
    optimization_name = optimetrics_app.optimizations.setup_names[0]

    assert isinstance(optimetrics_app.optimizations[optimization_name], OptimizationSetup)
    assert not optimetrics_app.optimizations["invented"]

    assert isinstance(optimetrics_app.parametrics[parametric_name], ParametricSetup)
    assert not optimetrics_app.parametrics["invented"]

    assert isinstance(optimetrics_app.optimetrics[parametric_name], ParametricSetup)
    assert isinstance(optimetrics_app.optimetrics[optimization_name], OptimizationSetup)

    # Delete setup
    assert not optimetrics_app.optimetrics.delete_setup("invented")

    assert optimetrics_app.optimetrics.delete_setup(parametric_name)
    assert len(optimetrics_app.parametrics.setups) == 0
    assert parametric_name not in optimetrics_app.parametrics.setup_names
    assert parametric_name not in optimetrics_app.optimetrics.setups

    assert optimetrics_app.optimetrics.delete_setup(optimization_name)
    assert len(optimetrics_app.optimizations.setups) == 0
    assert optimization_name not in optimetrics_app.optimizations.setup_names
    assert optimization_name not in optimetrics_app.optimetrics.setups
    assert len(optimetrics_app.optimetrics.setups) == 0
    assert optimetrics_app.optimetrics.setup_names == []

    # No setups available
    assert not optimetrics_app.optimetrics.delete_setup(optimization_name)


def test_create_parametrics(aedtapp, test_tmp_dir) -> None:
    aedtapp.set_active_design("HFSSDesign")
    aedtapp["w1"] = "10mm"
    aedtapp["w2"] = "2mm"
    setup = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    setup.props["Frequency"] == "3.5GHz"
    setup.enable_adaptive_setup_single(3.5)

    with pytest.raises(AEDTRuntimeError):
        aedtapp.parametrics.add("invalid", 0.1, 20, 0.2, "LinearStep")

    setup1 = aedtapp.optimetrics.add_parametric("w1", 0.1, 20, 0.2, "LinearStep")

    with pytest.raises(AEDTRuntimeError):
        aedtapp.optimetrics.add_parametric("w1", 0.1, 20, 0.2, "LinearStep", name=setup1.name)

    assert isinstance(setup1, ParametricSetup)
    assert setup1.name in aedtapp.parametrics.design_setups
    assert setup1.name in aedtapp.parametrics.setups
    assert setup1.name in aedtapp.optimetrics.setup_names
    assert setup1.props["Sweeps"]["SweepDefinition"]["Variable"] == "w1"
    assert setup1.props["Sweeps"]["SweepDefinition"]["Data"] == "LIN 0.1mm 20mm 0.2mm"

    with pytest.raises(AEDTRuntimeError):
        setup1.add_variation("invalid", "0.1mm", 10, 11)

    assert setup1.add_variation("w2", "0.1mm", 10, 11)
    assert len(setup1.props["Sweeps"]["SweepDefinition"]) == 2
    assert setup1.props["Sweeps"]["SweepDefinition"][1]["Data"] == "LINC 0.1mm 10mm 11"

    assert setup1.add_variation("w2", start_point="0.2mm", variation_type="SingleValue")
    assert setup1.props["Sweeps"]["SweepDefinition"][1]["Data"] == "LINC 0.1mm 10mm 11 0.2mm"

    assert setup1.add_variation("w1", start_point="0.3mm", end_point="0.5mm", step="0.2mm", variation_type="LinearStep")
    assert setup1.props["Sweeps"]["SweepDefinition"][0]["Data"] == "LIN 0.1mm 20mm 0.2mm LIN 0.3mm 0.5mm 0.2mm"

    assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="DecadeCount")
    assert (
        setup1.props["Sweeps"]["SweepDefinition"][0]["Data"]
        == "LIN 0.1mm 20mm 0.2mm LIN 0.3mm 0.5mm 0.2mm DEC 0.3mm 5mm 1"
    )

    assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="OctaveCount")
    assert (
        setup1.props["Sweeps"]["SweepDefinition"][0]["Data"]
        == "LIN 0.1mm 20mm 0.2mm LIN 0.3mm 0.5mm 0.2mm DEC 0.3mm 5mm 1 OCT 0.3mm 5mm 1"
    )

    assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="ExponentialCount")
    assert (
        setup1.props["Sweeps"]["SweepDefinition"][0]["Data"]
        == "LIN 0.1mm 20mm 0.2mm LIN 0.3mm 0.5mm 0.2mm DEC 0.3mm 5mm 1 OCT 0.3mm 5mm 1 ESTP 0.3mm 5mm 1"
    )

    assert setup1.add_calculation(
        calculation="dB(S(1,1))", ranges={"Freq": "3.5GHz"}, solution="My_HFSS_Setup : LastAdaptive"
    )
    assert setup1.props["Goals"]["Goal"]["Solution"] == "My_HFSS_Setup : LastAdaptive"
    assert setup1.props["Goals"]["Goal"]["Calculation"] == "dB(S(1,1))"

    assert setup1.export_to_csv(str(test_tmp_dir / "test.csv"))

    assert (test_tmp_dir / "test.csv").is_file()

    assert aedtapp.parametrics.export_to_csv(str(test_tmp_dir / "test1.csv"), setup1.name)

    assert (test_tmp_dir / "test1.csv").is_file()

    with pytest.raises(AEDTRuntimeError):
        aedtapp.parametrics.export_to_csv(str(test_tmp_dir / "test1.csv"), "invented")

    setup2 = aedtapp.parametrics.add_from_file(str(test_tmp_dir / "test.csv"), "ParametricsfromFile")
    assert setup2.name in aedtapp.parametrics.setup_names
    assert len(setup2.props["Sweep Operations"]["add"]) == 1391

    with pytest.raises(ValueError):
        aedtapp.parametrics.add_from_file("test.invalid", "ParametricsfromFile2")

    with pytest.raises(AEDTRuntimeError):
        aedtapp.parametrics.add_from_file(str(test_tmp_dir / "test.csv"), setup2.name)

    assert aedtapp.parametrics.delete("ParametricsfromFile")
    assert len(aedtapp.parametrics.setups) == 1


def test_create_parametrics_sync(aedtapp) -> None:
    aedtapp["a1"] = "10mm"
    aedtapp["a2"] = "2mm"
    aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    setup1 = aedtapp.parametrics.add("a1", start_point=0.1, end_point=20, step=10, variation_type="LinearCount")
    assert setup1.add_variation("a2", start_point="0.3mm", end_point=5, step=10, variation_type="LinearCount")
    with pytest.raises(AEDTRuntimeError):
        setup1.sync_variables(["invalid"], sync_n=1)
    assert setup1.props["Sweeps"]["SweepDefinition"][0]["Synchronize"] == 0
    assert setup1.sync_variables(["a1", "a2"], sync_n=1)
    assert setup1.props["Sweeps"]["SweepDefinition"][0]["Synchronize"] == 1
    assert setup1.sync_variables(["a1", "a2"], sync_n=0)
    assert setup1.props["Sweeps"]["SweepDefinition"][0]["Synchronize"] == 0


def test_create_optimization(aedtapp) -> None:
    aedtapp["w1"] = "10mm"
    calculation = "db(S(1,1))"
    new_setup = aedtapp.create_setup("MyOptimSetup")
    new_setup.props["Frequency"] = "2.5GHz"
    sweep = new_setup.create_linear_step_sweep(start_frequency=2, stop_frequency=10, step_size=0.1)

    setup2 = aedtapp.optimetrics.add_optimization(
        calculation, ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )

    assert setup2.name in aedtapp.optimizations.design_setups
    assert setup2.name in aedtapp.optimizations.setups
    assert setup2.name in aedtapp.optimetrics.setup_names
    assert setup2.props["Goals"]["Goal"]["Calculation"] == calculation
    assert (setup2.props["Goals"]["Goal"]["Ranges"]["Range"]["DiscreteValues"]).lower() == "2.5ghz"
    assert not setup2.props["Variables"]

    assert setup2.add_variation("w1", 0.1, 10, 5)
    assert isinstance(setup2.props["Variables"]["w1"], Props)
    assert setup2.props["Variables"]["w1"]["Min"] == "0.1mm"

    assert setup2.add_goal(
        calculation=calculation, ranges={"Freq": "2.6GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    assert isinstance(setup2.props["Goals"]["Goal"], list)
    assert len(setup2.props["Goals"]["Goal"]) == 2
    assert (setup2.props["Goals"]["Goal"][1]["Ranges"]["Range"]["DiscreteValues"]).lower() == "2.6ghz"

    assert setup2.add_goal(
        calculation=calculation,
        ranges={"Freq": ("2.6GHz", "5GHZ")},
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert len(setup2.props["Goals"]["Goal"]) == 3
    assert (setup2.props["Goals"]["Goal"][2]["Ranges"]["Range"]["Start"]).lower() == "2.6ghz"
    assert (setup2.props["Goals"]["Goal"][2]["Ranges"]["Range"]["Stop"]).lower() == "5ghz"

    setup2.props["Goals"]["Goal"][0]["Ranges"]["Range"]["DiscreteValues"] = "2.7GHz"
    assert (setup2.props["Goals"]["Goal"][0]["Ranges"]["Range"]["DiscreteValues"]).lower() == "2.7ghz"

    name_to_delete = setup2.name
    assert aedtapp.optimizations.delete(name_to_delete)
    assert name_to_delete not in aedtapp.optimizations.setup_names

    # Change optimization algorithm
    setup3 = aedtapp.optimizations.add(
        calculation, ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    setup3.props["Optimizer"] = "Screening"
    setup3.add_variation("w1", 0.1, 10, 5, min_step=0.5, max_step=1, use_manufacturable=True, levels=[1, 20])
    assert setup3.props["Variables"]["w1"]["Level"] == "[1, 20] mm"


def test_create_doe(aedtapp) -> None:
    aedtapp["w1"] = "10mm"
    aedtapp["w2"] = "2mm"
    calculation = "db(S(1,1))"
    new_setup = aedtapp.create_setup("MyDOESetup")
    new_setup.props["Frequency"] = "2.5GHz"
    sweep = new_setup.create_linear_step_sweep(start_frequency=2, stop_frequency=10, step_size=0.1)

    setup2 = aedtapp.optimizations.add(
        calculation,
        ranges={"Freq": "2.5GHz"},
        optimization_type="DXDOE",
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert setup2.setup_type == "OptiDXDOE"
    assert setup2.name in aedtapp.optimizations.setup_names
    assert setup2.props["Sim. Setups"] == [new_setup.name]
    assert setup2.props["Variables"] == {}

    assert setup2.add_variation("w1", 0.1, 10)
    assert isinstance(setup2.props["Variables"], Props)
    assert "w1" in setup2.props["Variables"]
    assert setup2.props["Variables"]["w1"]["Max"] == "10mm"

    assert setup2.add_variation("w2", 0.1, 20)
    assert len(setup2.props["Variables"]) == 2
    assert "w2" in setup2.props["Variables"]
    assert setup2.props["Variables"]["w2"]["Max"] == "20mm"

    assert aedtapp.variable_manager.variables["w1"].optimization_min_value == "0.1mm"
    assert aedtapp.variable_manager.variables["w1"].optimization_max_value == "10mm"
    assert aedtapp.variable_manager.variables["w2"].optimization_min_value == "0.1mm"
    assert aedtapp.variable_manager.variables["w2"].optimization_max_value == "20mm"

    assert setup2.add_goal(
        calculation="dB(S(1,1))",
        ranges={"Freq": "2.5GHz"},
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert len(setup2.props["CostFunctionGoals"]["Goal"]) == 2
    assert setup2.props["CostFunctionGoals"]["Goal"][1]["Calculation"] == "dB(S(1,1))"
    assert setup2.props["CostFunctionGoals"]["Goal"][1]["Ranges"]["Range"]["DiscreteValues"] == "2.5GHz"
    setup2.props["CostFunctionGoals"]["Goal"][1]["Ranges"]["Range"]["DiscreteValues"] = "2.6GHz"
    assert (setup2.props["CostFunctionGoals"]["Goal"][1]["Ranges"]["Range"]["DiscreteValues"]).lower() == "2.6ghz"

    assert setup2.add_calculation(
        calculation="dB(S(1,1))",
        ranges={"Freq": "2.5GHz"},
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert len(setup2.props["Goals"]["Goal"]) == 2
    assert setup2.props["Goals"]["Goal"][1]["Calculation"] == "dB(S(1,1))"
    assert setup2.props["Goals"]["Goal"][1]["Ranges"]["Range"]["DiscreteValues"] == "2.5GHz"


def test_create_optislang(aedtapp) -> None:
    aedtapp["w1"] = "10mm"
    aedtapp["w2"] = "2mm"
    aedtapp["a1"] = "10mm"
    new_setup = aedtapp.create_setup("MyOptisSetup")
    new_setup.props["Frequency"] = "2.5GHz"
    sweep = new_setup.create_linear_step_sweep(start_frequency=2, stop_frequency=10, step_size=0.1)

    setup1 = aedtapp.optimizations.add(
        calculation=None,
        ranges=None,
        variables=None,
        optimization_type="optiSLang",
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert setup1.setup_type == "optiSLang"
    assert setup1.name in aedtapp.optimizations.setup_names

    assert setup1.add_variation("w1", 1, 20, 51)
    assert aedtapp.variable_manager.variables["w1"].optimization_max_value == "20mm"

    setup2 = aedtapp.optimizations.add(
        calculation=None,
        ranges=None,
        variables={"w1": "1mm", "w2": "2mm"},
        optimization_type="optiSLang",
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert setup2.setup_type == "optiSLang"
    assert setup2.name in aedtapp.optimizations.setup_names

    assert setup2.add_variation("a1", 1, 100, 51)
    assert aedtapp.variable_manager.variables["a1"].optimization_max_value == "100mm"
    assert "a1" in [pr["Variable"] for pr in setup2.props["Sweeps"]["SweepDefinition"]]

    with pytest.raises(AEDTRuntimeError):
        setup2.add_variation("w3", 0.1, 10, 5)

    assert setup2.add_goal(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    assert setup2.props["Goals"]["Goal"]["Calculation"] == "dB(S(1,1))"
    assert setup2.props["Goals"]["Goal"]["Ranges"]["Range"]["DiscreteValues"] == "2.5GHz"

    assert setup2.add_goal(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    assert setup2.props["Goals"]["Goal"][1]["Calculation"] == "dB(S(1,1))"


def test_create_dx(aedtapp) -> None:
    aedtapp["w1"] = "10mm"
    aedtapp["w2"] = "2mm"
    aedtapp["a1"] = "10mm"
    new_setup = aedtapp.create_setup("MyDXSetup")
    new_setup.props["Frequency"] = "2.5GHz"
    sweep = new_setup.create_linear_step_sweep(start_frequency=2, stop_frequency=10, step_size=0.1)

    setup1 = aedtapp.optimizations.add(
        None,
        ranges=None,
        variables=None,
        optimization_type="DesignExplorer",
        solution=f"{new_setup.name} : {sweep.name}",
    )

    assert setup1.setup_type == "OptiDesignExplorer"
    assert setup1.name in aedtapp.optimizations.setup_names
    assert setup1.props["Sim. Setups"] == [new_setup.name]

    assert setup1.add_variation("w1", 5, 100, 51)
    assert aedtapp.variable_manager.variables["w1"].optimization_max_value == "100mm"

    setup2 = aedtapp.optimizations.add(
        None,
        ranges=None,
        variables={"w1": "1mm", "w2": "2mm"},
        optimization_type="DesignExplorer",
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert setup2.setup_type == "OptiDesignExplorer"
    assert setup2.name in aedtapp.optimizations.setup_names

    assert setup2.add_variation("a1", 2, 10, 51)
    assert aedtapp.variable_manager.variables["a1"].optimization_min_value == "2mm"

    assert setup2.add_goal(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    assert setup2.props["CostFunctionGoals"]["Goal"]["Calculation"] == "dB(S(1,1))"
    assert setup2.props["CostFunctionGoals"]["Goal"]["Ranges"]["Range"]["DiscreteValues"] == "2.5GHz"


def test_create_sensitivity(aedtapp) -> None:
    aedtapp["w1"] = "10mm"
    calculation = "db(S(1,1))"
    new_setup = aedtapp.create_setup("MySensiSetup")
    new_setup.props["Frequency"] = "2.5GHz"
    sweep = new_setup.create_linear_step_sweep(start_frequency=2, stop_frequency=10, step_size=0.1)

    setup2 = aedtapp.optimizations.add(
        calculation,
        ranges={"Freq": "2.5GHz"},
        optimization_type="Sensitivity",
        solution=f"{new_setup.name} : {sweep.name}",
    )

    assert setup2.setup_type == "OptiSensitivity"
    assert setup2.name in aedtapp.optimizations.setup_names
    assert setup2.props["Sim. Setups"] == [new_setup.name]
    assert setup2.props["MaxIterations"] == 10
    assert not setup2.props["Variables"]

    assert setup2.add_variation("w1", 0.1, 10, "3.2mm")
    assert isinstance(setup2.props["Variables"], Props)
    assert "w1" in setup2.props["Variables"]
    assert setup2.props["Variables"]["w1"]["Max"] == "10mm"
    assert setup2.props["Variables"]["w1"]["IDisp"] == "3.2mm"

    assert setup2.add_variation("dim", 0.1, 20, 5)
    assert setup2.props["Variables"]["dim"]["IDisp"] == "5mm"

    assert setup2.add_calculation(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    assert isinstance(setup2.props["Goals"]["Goal"], list)
    assert len(setup2.props["Goals"]["Goal"]) == 2
    assert setup2.props["Goals"]["Goal"][0]["Calculation"] == calculation
    assert setup2.props["Goals"]["Goal"][1]["Calculation"] == "dB(S(1,1))"
    assert setup2.props["Goals"]["Goal"][1]["Ranges"]["Range"]["DiscreteValues"] == "2.5GHz"


def test_create_statistical(aedtapp) -> None:
    aedtapp["w1"] = "10mm"
    calculation = "db(S(1,1))"
    new_setup = aedtapp.create_setup("MyStatisticsetup")
    new_setup.props["Frequency"] = "2.5GHz"
    sweep = new_setup.create_linear_step_sweep(start_frequency=2, stop_frequency=10, step_size=0.1)
    setup2 = aedtapp.optimizations.add(
        calculation,
        ranges={"Freq": "2.5GHz"},
        optimization_type="Statistical",
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert setup2.setup_type == "OptiStatistical"
    assert setup2.name in aedtapp.optimizations.setup_names
    assert setup2.props["Sim. Setups"] == [new_setup.name]
    assert setup2.props["MaxIterations"] == 50
    assert setup2.props["SeedValue"] == 0
    assert setup2.props["Variables"] == {}
    assert setup2.add_variation("w1", 0.1, 10)
    assert setup2.props["Variables"]["w1"]

    assert setup2.add_variation("dim", 0.1, 10)
    assert setup2.props["Variables"]["dim"]

    assert setup2.add_calculation(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    assert isinstance(setup2.props["Goals"]["Goal"], list)
    assert len(setup2.props["Goals"]["Goal"]) == 2
    assert setup2.props["Goals"]["Goal"][0]["Calculation"] == calculation
    assert setup2.props["Goals"]["Goal"][1]["Calculation"] == "dB(S(1,1))"
    assert setup2.props["Goals"]["Goal"][1]["Ranges"]["Range"]["DiscreteValues"] == "2.5GHz"
