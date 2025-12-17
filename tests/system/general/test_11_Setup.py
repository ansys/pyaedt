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

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss
from ansys.aedt.core.generic.constants import Setups
from tests.conftest import desktop_version

test_subfolder = "T11"
if desktop_version > "2022.2":
    test_project_name = "coax_setup_231"
else:
    test_project_name = "coax_setup"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss, project_name=test_project_name, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def circuit_app(add_app):
    app = add_app(application=Circuit, project_name="circuit_setup", subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


def test_create_hfss_setup(aedtapp):
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.name == "My_HFSS_Setup"
    assert aedtapp.setups[0].name == setup1.name
    assert "SaveRadFieldsOnly" in setup1.props
    assert "SaveRadFieldsOnly" in setup1.available_properties
    setup1["SaveRadFieldsonly"] = True
    assert setup1.props["SaveRadFieldsOnly"] == setup1["SaveRadFieldsonly"]
    assert setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
    assert setup1.props["MultipleAdaptiveFreqsSetup"]["1GHz"][0] == 0.02
    assert setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)
    assert setup1.props["MultipleAdaptiveFreqsSetup"]["Low"] == "1GHz"
    assert setup1.props["MaximumPasses"] == 10
    assert setup1.props["MaxDeltaS"] == 0.01
    assert setup1.enable_adaptive_setup_single(3.5)
    assert setup1.props["Frequency"] == "3.5GHz"
    assert setup1.props["MaximumPasses"] == 10
    assert setup1.props["MaxDeltaS"] == 0.01
    setup1.disable()
    setup1.enable()

    assert setup1.use_matrix_convergence(
        entry_selection=0,
        ignore_phase_when_mag_is_less_than=0.015,
        all_diagonal_entries=True,
        max_delta=0.03,
        max_delta_phase=8,
        custom_entries=None,
    )
    assert setup1.use_matrix_convergence(
        entry_selection=1,
        ignore_phase_when_mag_is_less_than=0.025,
        all_diagonal_entries=True,
        max_delta=0.023,
        max_delta_phase=18,
        custom_entries=None,
        all_offdiagonal_entries=False,
    )
    assert setup1.use_matrix_convergence(
        entry_selection=1,
        ignore_phase_when_mag_is_less_than=0.025,
        all_diagonal_entries=True,
        max_delta=0.023,
        max_delta_phase=18,
        custom_entries=None,
    )
    assert setup1.use_matrix_convergence(
        entry_selection=2,
        ignore_phase_when_mag_is_less_than=0.01,
        all_diagonal_entries=True,
        max_delta=0.01,
        max_delta_phase=8,
        custom_entries=[["1", "2", 0.03, 4]],
    )
    setup2 = aedtapp.create_setup("MulitFreqSetup", MultipleAdaptiveFreqsSetup=["1GHz", "2GHz"], MaximumPasses=3)
    assert setup2.props["SolveType"] == "MultiFrequency"
    assert setup2.props["MaximumPasses"] == 3

    setup3 = aedtapp.create_setup(Frequency=["1GHz", "2GHz"], MaximumPasses=3)
    assert setup3.props["SolveType"] == "MultiFrequency"
    assert setup3.props["MaximumPasses"] == 3


def test_create_hfss_sweep(aedtapp):
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert aedtapp.get_setups()
    sweep1 = setup1.add_sweep("MyFrequencySweep")
    sweep1.props["RangeStart"] = "1Hz"
    sweep1.props["RangeEnd"] = "2GHz"
    assert sweep1.update()
    sweep1.props["Type"] = "Fast"
    sweep1.props["SaveFields"] = True
    assert sweep1.update()
    assert aedtapp.get_sweeps("My_HFSS_Setup")
    sweep2 = setup1.add_sweep(name="test_sweeptype", sweep_type="invalid")
    assert sweep2.props["Type"] == "Interpolating"
    sweep3 = setup1.create_frequency_sweep(start_frequency=1, stop_frequency="500MHz")
    assert sweep3.props["Type"] == "Discrete"
    sweep4 = setup1.create_frequency_sweep("GHz", 23, 25, 401, sweep_type="Fast")
    assert sweep4.props["Type"] == "Fast"
    range_start = "1GHz"
    range_end = "2GHz"
    range_step = "0.5GHz"
    sweep5 = setup1.add_sweep(
        "DiscSweep5",
        sweep_type="Discrete",
        RangeStart=range_start,
        RangeEnd=range_end,
        RangeStep=range_step,
        SaveFields=True,
    )
    assert sweep5.props["Type"] == "Discrete"
    assert sweep5.props["RangeStart"] == range_start
    assert sweep5.props["RangeEnd"] == range_end
    assert sweep5.props["RangeStep"] == range_step


def test_create_hfss_setup_auto_open(aedtapp):
    aedtapp.duplicate_design("auto_open")
    for setup in aedtapp.get_setups():
        aedtapp.delete_setup(setup)
        assert setup not in aedtapp.setups
    assert not aedtapp.setups
    aedtapp.set_auto_open()
    setup1 = aedtapp.get_setup("Auto1")
    setup1.enable_adaptive_setup_multifrequency([1.9, 2.4], 0.02)
    assert setup1.update({"MaximumPasses": 20})
    assert setup1.props["SolveType"] == "MultiFrequency"


def test_create_circuit_setup(circuit_app):
    setup1 = circuit_app.create_setup("circuit", Setups.NexximLNA)
    assert setup1.name == "circuit"
    setup1.props["SweepDefinition"]["Data"] = "LINC 0GHz 4GHz 501"
    setup1["SaveRadFieldsonly"] = True
    setup1["SweepDefinition/Data"] = "LINC 0GHz 4GHz 302"
    assert setup1.props["SweepDefinition"]["Data"] == "LINC 0GHz 4GHz 302"
    assert circuit_app.setups[0].props["SweepDefinition"]["Data"] == "LINC 0GHz 4GHz 302"
    assert "SweepDefinition" in setup1.available_properties
    setup1.update()
    setup1.disable()
    setup1.enable()


def test_non_valid_setup(aedtapp):
    aedtapp.set_active_design("HFSSDesign")
    aedtapp.duplicate_design("non_valid")
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    assert not setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
    assert not setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)
    assert not setup1.enable_adaptive_setup_single(3.5)
    sol = aedtapp.solution_type
    aedtapp.solution_type = "Transient"
    assert not setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
    assert not setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)
    assert not setup1.enable_adaptive_setup_single(3.5)
    aedtapp.solution_type = sol


def test_delete_setup(aedtapp):
    aedtapp.insert_design("delete_setups")
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    assert len(aedtapp.setups) == 1
    assert setup1.delete()
    assert len(aedtapp.setups) == 0
    assert not aedtapp.get_setups()


def test_sweep_auto(aedtapp):
    aedtapp.insert_design("sweep")
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    assert setup1.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
    assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)


def test_delete_sweep(aedtapp):
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    setup1.create_frequency_sweep("GHz", 24, 24.25, 26, "My_Sweep1", sweep_type="Fast")
    sweeps = setup1.get_sweep_names()
    assert len(sweeps) == 1
    assert "My_Sweep1" in sweeps
    setup1.delete_sweep("My_Sweep1")
    sweeps = setup1.get_sweep_names()
    assert len(sweeps) == 0


def test_sweep_sbr(aedtapp):
    aedtapp.insert_design("sweepsbr")
    aedtapp.solution_type = "SBR+"
    aedtapp.insert_infinite_sphere()
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSSBR)
    assert setup1.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
    assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)


def test_create_parametrics(aedtapp, local_scratch):
    aedtapp.set_active_design("HFSSDesign")
    aedtapp["w1"] = "10mm"
    aedtapp["w2"] = "2mm"
    setup = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    setup.props["Frequency"] == "3.5GHz"
    setup.enable_adaptive_setup_single(3.5)
    assert not aedtapp.parametrics.add("invalid", 0.1, 20, 0.2, "LinearStep")
    setup1 = aedtapp.parametrics.add("w1", 0.1, 20, 0.2, "LinearStep")
    assert setup1.name in aedtapp.parametrics.design_setups
    assert setup1
    assert not setup1.add_variation("invalid", "0.1mm", 10, 11)
    assert setup1.add_variation("w2", "0.1mm", 10, 11)
    assert setup1.add_variation("w2", start_point="0.2mm", variation_type="SingleValue")
    assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=0.2, variation_type="LinearStep")
    assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="DecadeCount")
    assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="OctaveCount")
    assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="ExponentialCount")
    assert setup1.add_calculation(
        calculation="dB(S(1,1))", ranges={"Freq": "3.5GHz"}, solution="My_HFSS_Setup : LastAdaptive"
    )
    assert setup1.name in aedtapp.get_oo_name(aedtapp.odesign, "Optimetrics")
    oo = aedtapp.get_oo_object(aedtapp.odesign, f"Optimetrics\\{setup1.name}")
    oo_calculation = oo.GetCalculationInfo()[0]
    assert "Modal Solution Data" in oo_calculation
    assert setup1.export_to_csv(os.path.join(local_scratch.path, "test.csv"))
    assert os.path.exists(os.path.join(local_scratch.path, "test.csv"))
    assert aedtapp.parametrics.add_from_file(os.path.join(local_scratch.path, "test.csv"), "ParametricsfromFile")
    with pytest.raises(ValueError):
        aedtapp.parametrics.add_from_file("test.invalid", "ParametricsfromFile")
    oo = aedtapp.get_oo_object(aedtapp.odesign, r"Optimetrics\ParametricsfromFile")
    assert oo
    assert aedtapp.parametrics.delete("ParametricsfromFile")


def test_create_parametrics_sync(aedtapp):
    aedtapp["a1"] = "10mm"
    aedtapp["a2"] = "2mm"
    aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    setup1 = aedtapp.parametrics.add("a1", start_point=0.1, end_point=20, step=10, variation_type="LinearCount")
    assert setup1
    assert setup1.add_variation("a2", start_point="0.3mm", end_point=5, step=10, variation_type="LinearCount")
    assert not setup1.sync_variables(["invalid"], sync_n=1)
    assert setup1.sync_variables(["a1", "a2"], sync_n=1)
    assert setup1.sync_variables(["a1", "a2"], sync_n=0)
    setup1.add_variation("a1", start_point="13mm", variation_type="SingleValue")


def test_create_optimization(aedtapp):
    aedtapp["w1"] = "10mm"
    calculation = "db(S(1,1))"
    new_setup = aedtapp.create_setup("MyOptimSetup")
    new_setup.props["Frequency"] = "2.5GHz"
    sweep = new_setup.create_linear_step_sweep(start_frequency=2, stop_frequency=10, step_size=0.1)
    setup2 = aedtapp.optimizations.add(
        calculation, ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    assert setup2.name in aedtapp.optimizations.design_setups
    assert setup2
    assert setup2.name in aedtapp.get_oo_name(aedtapp.odesign, "Optimetrics")
    oo = aedtapp.get_oo_object(aedtapp.odesign, f"Optimetrics\\{setup2.name}")
    oo_calculation = oo.GetCalculationInfo()[0]
    assert calculation in oo_calculation
    assert f"{new_setup.name} : {sweep.name}" in oo_calculation
    for el in oo_calculation:
        if "NAME:Ranges" in el:
            break
    assert len(el) == 3
    assert setup2.add_variation("w1", 0.1, 10, 5)
    assert setup2.add_goal(
        calculation=calculation, ranges={"Freq": "2.6GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
    oo_calculation = oo.GetCalculationInfo()[0]
    for el in reversed(oo_calculation):
        if "NAME:Ranges" in el:
            break
    assert "2.6GHz" in el[2]
    assert setup2.add_goal(
        calculation=calculation,
        ranges={"Freq": ("2.6GHz", "5GHZ")},
        solution=f"{new_setup.name} : {sweep.name}",
    )
    oo = aedtapp.get_oo_object(aedtapp.odesign, f"Optimetrics\\{setup2.name}")
    oo_calculation = oo.GetCalculationInfo()[0]
    for el in reversed(oo_calculation):
        if "NAME:Ranges" in el:
            break
    assert "rd" in el[2]

    assert setup2.props["Goals"]["Goal"][0]["Ranges"]["Range"][0]["DiscreteValues"] == "2.5GHz"

    setup2.props["Goals"]["Goal"][0]["Ranges"]["Range"][0]["DiscreteValues"] = "2.7GHz"

    oo = aedtapp.get_oo_object(aedtapp.odesign, f"Optimetrics\\{setup2.name}")
    oo_calculation = oo.GetCalculationInfo()[0]
    for el in oo_calculation:
        if "NAME:Ranges" in el:
            break
    assert el[2][5] == "2.7GHz"

    assert aedtapp.optimizations.delete(setup2.name)

    assert not aedtapp.get_oo_object(aedtapp.odesign, f"Optimetrics\\{setup2.name}")

    setup3 = aedtapp.optimizations.add(
        calculation, ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )

    setup3.props["Optimizer"] = "Screening"
    setup3.add_variation("w1", 0.1, 10, 5, min_step=0.5, max_step=1, use_manufacturable=True, levels=[1, 20])
    assert setup3.props["Variables"]["w1"][19] == "[1, 20] mm"
    assert aedtapp.optimizations.delete(setup3.name)


def test_create_doe(aedtapp):
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
    assert setup2.add_variation("w1", 0.1, 10)
    assert setup2.add_variation("w2", 0.1, 10)
    assert setup2
    if desktop_version < "2024.1":
        assert setup2.add_goal(
            calculation="dB(S(1,1))",
            ranges={"Freq": "2.5GHz"},
            solution=f"{new_setup.name} : {sweep.name}",
        )
        assert setup2.add_calculation(
            calculation="dB(S(1,1))",
            ranges={"Freq": "2.5GHz"},
            solution=f"{new_setup.name} : {sweep.name}",
        )
    assert setup2.delete()


def test_create_optislang(aedtapp):
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
    assert setup1.add_variation("w1", 1, 10, 51)
    setup2 = aedtapp.optimizations.add(
        calculation=None,
        ranges=None,
        variables={"w1": "1mm", "w2": "2mm"},
        optimization_type="optiSLang",
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert setup2.add_variation("a1", 1, 10, 51)
    assert not setup2.add_variation("w3", 0.1, 10, 5)
    assert setup2
    assert setup2.add_goal(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )


def test_create_dx(aedtapp):
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
    assert setup1.add_variation("w1", 5, 10, 51)
    setup2 = aedtapp.optimizations.add(
        None,
        ranges=None,
        variables={"w1": "1mm", "w2": "2mm"},
        optimization_type="DesignExplorer",
        solution=f"{new_setup.name} : {sweep.name}",
    )
    assert setup2.add_variation("a1", 1, 10, 51)
    assert setup2
    assert setup2.add_goal(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )


def test_create_sensitivity(aedtapp):
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
    assert setup2.add_variation("w1", 0.1, 10, 3.2)
    assert setup2
    assert setup2.add_calculation(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )


def test_create_statistical(aedtapp):
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
    assert setup2.add_variation("w1", 0.1, 10, 0.3)
    assert setup2
    assert setup2.add_calculation(
        calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution=f"{new_setup.name} : {sweep.name}"
    )
