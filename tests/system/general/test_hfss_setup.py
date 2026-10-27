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
from ansys.aedt.core.generic.aedt_constants import Setups
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.design_xploration import ParametricSetup
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import SetupHFSS
from ansys.aedt.core.modules.solve_setup import SetupHFSSAuto
from ansys.aedt.core.modules.solve_setup import SetupSBR
from ansys.aedt.core.modules.solve_sweeps import SweepHFSS

TEST_SUBFOLDER = "TSetup"
TEST_HFSS = "hfss_setup_test"


@pytest.fixture
def hfss_app(add_app):
    app = add_app(application=Hfss, solution_type="Modal")
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def hfss_setup_app(add_app_example):
    app = add_app_example(application=Hfss, project=TEST_HFSS, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def test_setup_hfss_init(hfss_setup_app):
    hfss_setup_app.set_active_design("HFSS")

    assert len(hfss_setup_app.setups) == 2
    assert isinstance(hfss_setup_app.setups[0], SetupHFSSAuto)
    assert str(hfss_setup_app.setups[0]) == f"{hfss_setup_app.setups[0].name} : Sweep"
    assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
    assert hfss_setup_app.setups[0].solver_type == SetupKeys.SetupNames[Setups.HFSSDrivenAuto]

    assert isinstance(hfss_setup_app.setups[1], SetupHFSS)
    assert str(hfss_setup_app.setups[1]) == f"{hfss_setup_app.setups[1].name} : LastAdaptive"
    assert hfss_setup_app.setups[1].__repr__() == hfss_setup_app.setups[1].name
    assert hfss_setup_app.setups[1].solver_type == SetupKeys.SetupNames[Setups.HFSSDrivenDefault]
    assert len(hfss_setup_app.setups[1].sweep_names) == 1

    hfss_setup_app.set_active_design("HFSSCMA")
    assert len(hfss_setup_app.setups) == 1
    assert isinstance(hfss_setup_app.setups[0], SetupHFSS)
    assert str(hfss_setup_app.setups[0]) == hfss_setup_app.setups[0].name
    assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
    assert hfss_setup_app.setups[0].solver_type == SetupKeys.SetupNames[Setups.HFSSCMA]

    hfss_setup_app.set_active_design("HFSSEigenmode")
    assert len(hfss_setup_app.setups) == 1
    assert isinstance(hfss_setup_app.setups[0], SetupHFSS)
    assert str(hfss_setup_app.setups[0]) == f"{hfss_setup_app.setups[0].name} : LastAdaptive"
    assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
    assert hfss_setup_app.setups[0].solver_type == SetupKeys.SetupNames[Setups.HFSSEigen]

    hfss_setup_app.set_active_design("HFSSTransient")
    assert len(hfss_setup_app.setups) == 1
    assert isinstance(hfss_setup_app.setups[0], SetupHFSS)
    assert str(hfss_setup_app.setups[0]) == f"{hfss_setup_app.setups[0].name} : Transient"
    assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
    assert hfss_setup_app.setups[0].solver_type == SetupKeys.SetupNames[Setups.HFSSTransient]

    hfss_setup_app.set_active_design("SBR")
    assert len(hfss_setup_app.setups) == 1
    assert isinstance(hfss_setup_app.setups[0], SetupSBR)
    assert str(hfss_setup_app.setups[0]) == f"{hfss_setup_app.setups[0].name} : Sweep"
    assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
    assert hfss_setup_app.setups[0].solver_type == SetupKeys.SetupNames[Setups.HFSSSBR]


def test_setup(hfss_app) -> None:
    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.name == "My_HFSS_Setup"
    assert hfss_app.setups[0].name == setup1.name
    assert setup1.name in hfss_app.setup_names
    assert isinstance(setup1, SetupHFSS)
    assert len(hfss_app.setup_names) == 1

    setup2 = hfss_app.create_setup(setup_type="HFSSDrivenDefault", Frequency="55GHz")
    assert setup2.name in hfss_app.setup_names
    assert setup2.props["Frequency"] == "55GHz"
    assert len(hfss_app.setup_names) == 2

    with pytest.raises(ValueError):
        hfss_app.active_setup = "invalid"
    assert hfss_app.active_setup is not None
    assert hfss_app.nominal_sweep is not None

    with pytest.raises(AEDTRuntimeError):
        hfss_app.create_setup(name=setup2.name, MultipleAdaptiveFreqsSetup=["2GHz", "5GHz"])
    assert len(hfss_app.setup_names) == 2

    with pytest.raises(AEDTRuntimeError):
        hfss_app.create_setup(Frequency=["85GHz", "90GHz"])
    assert len(hfss_app.setup_names) == 2

    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup3 = hfss_app.create_setup(name=setup2.name, MultipleAdaptiveFreqsSetup=["2GHz", "5GHz"], MaximumPasses=3)
    assert setup3.name in hfss_app.setup_names
    assert setup3.name != setup2.name
    assert len(hfss_app.setup_names) == 3
    assert len(setup3.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"]) == 2
    assert setup3.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"] == "2GHz"
    assert setup3["MaximumPasses"] == 3

    setup4 = hfss_app.create_setup(Frequency=["85GHz", "90GHz"], MaximumPasses=3)
    assert setup4.name in hfss_app.setup_names
    assert len(hfss_app.setup_names) == 4
    assert len(setup4.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"]) == 2
    assert setup4.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"] == "85GHz"
    assert setup4["MaximumPasses"] == 3

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in hfss_app.setup_names
    assert name not in hfss_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Sweep
    assert not setup1.sweep_names

    # Props
    assert "SaveRadFieldsOnly" in setup1.props
    assert not setup1["SaveRadFieldsOnly"]
    setup1["SaveRadFieldsOnly"] = True
    assert setup1["SaveRadFieldsOnly"]

    setup1.disable()
    assert not setup1["IsEnabled"]
    setup1.enable()
    assert setup1["IsEnabled"]

    # Delete
    assert hfss_app.delete_setup(name=setup1.name)
    assert "new_name" not in hfss_app.setup_names
    assert not hfss_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in hfss_app.setup_names


def test_enable_adaptive_single(hfss_app):
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup(setup_type=Setups.HFSSDrivenDefault)
    assert setup1.enable_adaptive_setup_single(3.5)
    assert setup1.props["Frequency"] == "3.5GHz"

    hfss_app.solution_type = "Transient"
    setup2 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    with pytest.raises(AEDTRuntimeError):
        setup2.enable_adaptive_setup_single(3.5)


def test_enable_adaptive_multi(hfss_app):
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
    assert setup1.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Delta"] == 0.02
    assert setup1["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"] == "1GHz"

    hfss_app.solution_type = "Transient"
    setup2 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    with pytest.raises(AEDTRuntimeError):
        setup2.enable_adaptive_setup_multifrequency([1, 2, 3])


def test_enable_adaptive_broad(hfss_app):
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)
    assert setup1.props["MultipleAdaptiveFreqsSetup"]["Low"] == "1GHz"
    assert setup1.props["MaximumPasses"] == 10
    assert setup1.props["MaxDeltaS"] == 0.01

    hfss_app.solution_type = "Transient"
    with pytest.raises(AEDTRuntimeError):
        setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)


def test_matrix_convergence(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    p1 = hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.use_matrix_convergence(
        entry_selection=0,
        ignore_phase_when_mag_is_less_than=0.015,
        all_diagonal_entries=True,
        max_delta=0.03,
        max_delta_phase=8,
        custom_entries=None,
    )
    assert str(setup1.props["Matrix Convergence"]["MagLimit"]) == "0.03"

    assert setup1.use_matrix_convergence(
        entry_selection=1,
        ignore_phase_when_mag_is_less_than=0.025,
        all_diagonal_entries=True,
        max_delta=0.023,
        max_delta_phase=18,
        custom_entries=None,
        all_offdiagonal_entries=False,
    )
    assert str(setup1.props["Matrix Convergence"]["DiagonalMag"]) == "0.023"

    assert setup1.use_matrix_convergence(
        entry_selection=1,
        ignore_phase_when_mag_is_less_than=0.025,
        all_diagonal_entries=True,
        max_delta=0.023,
        max_delta_phase=18,
        custom_entries=None,
    )
    assert str(setup1.props["Matrix Convergence"]["MagMinThreshold"]) == "0.025"

    assert setup1.use_matrix_convergence(
        entry_selection=2,
        ignore_phase_when_mag_is_less_than=0.01,
        all_diagonal_entries=True,
        max_delta=0.01,
        max_delta_phase=8,
        custom_entries=[[p1.name, p1.name, 0.03, 4]],
    )
    assert str(setup1.props["Matrix Convergence"]["Entries"]["Entry"]["MagLimit"]) == "0.03"
    assert str(setup1.props["Matrix Convergence"]["Entries"]["Entry"]["PhaseLimit"]) == "4deg"
    assert str(setup1.props["Matrix Convergence"]["Entries"]["Entry"]["Port1"]) == p1.name

    assert not setup1.use_matrix_convergence(
        entry_selection=3,
        ignore_phase_when_mag_is_less_than=0.01,
        all_diagonal_entries=True,
        max_delta=0.01,
        max_delta_phase=8,
        custom_entries=[[p1.name, p1.name, 0.03, 4]],
    )


def test_sweep(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert hfss_app.get_setups()

    sweep1 = setup1.add_sweep("MyFrequencySweep")
    assert isinstance(sweep1, SweepHFSS)
    assert sweep1.name in setup1.sweep_names
    assert len(setup1.sweeps) == 1
    assert sweep1.props["RangeType"] == "LinearCount"
    sweep1["RangeStart"] = "1GHz"
    assert sweep1["RangeStart"] == "1GHz"

    # Properties
    assert not sweep1.is_solved
    assert not sweep1.frequencies
    assert not sweep1.basis_frequencies

    sweep2 = setup1.add_sweep(RangeCount=101)
    assert sweep2.name in setup1.sweep_names
    assert sweep2.props["RangeCount"] == 101

    sweep3 = setup1.add_sweep(name=sweep2.name, RangeStep="0.001GHz")
    assert sweep3.name in setup1.sweep_names
    assert sweep3.name != sweep2.name
    assert sweep3["RangeStep"] == "0.001GHz"

    props = dict(sweep1.props)
    props["RangeStart"] = "1Hz"
    props["RangeEnd"] = "2GHz"
    assert sweep1.update(props)

    sweep1.props["Type"] = "Fast"
    assert sweep1["Type"] == "Fast"

    sweep1["SaveFields"] = True
    assert sweep1["SaveFields"]

    sweeps = hfss_app.get_sweeps("My_HFSS_Setup")
    assert len(sweeps) == len(setup1.sweeps)

    sweep2 = setup1.add_sweep(name="test_sweeptype", sweep_type="invalid")
    assert sweep2["Type"] == "Interpolating"

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

    # Rename
    name = sweep5.name
    sweep5.name = "new_name"
    assert "new_name" in setup1.sweep_names
    assert name not in setup1.sweep_names
    assert sweep5.name == "new_name"
    assert sweep5.child_object

    # Delete
    assert setup1.delete_sweep(name=sweep5.name)
    assert "new_name" not in hfss_app.setup_names
    assert not setup1.delete_sweep(name="invented")

    name2 = sweep3.name
    sweep3.delete()
    assert name2 not in setup1.sweep_names


def test_add_subrange(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    sweep1 = setup1.add_sweep("MyFrequencySweep")

    with pytest.raises(AttributeError):
        sweep1.add_subrange(range_type="LinearCount", start=2)

    # Appending subranges exercises each supported range type and the unit conversion paths.
    assert sweep1.add_subrange("LinearCount", 1, 2, 10, unit="MHz")
    assert sweep1.add_subrange("LinearStep", 2, 3, 0.25, unit="GHz")
    assert sweep1.add_subrange("LogScale", 1, 10, 5, unit="GHz")
    subranges = sweep1.props["SweepRanges"]["Subrange"]

    assert subranges[0] == {
        "RangeType": "LinearCount",
        "RangeStart": "1MHz",
        "RangeEnd": "2MHz",
        "RangeCount": 10,
    }
    assert subranges[1] == {
        "RangeType": "LinearStep",
        "RangeStart": "2GHz",
        "RangeEnd": "3GHz",
        "RangeStep": "0.25GHz",
    }
    assert subranges[2]["RangeType"] == "LogScale"

    with pytest.raises(AEDTRuntimeError):
        sweep1.add_subrange("SinglePoints", 2.4, unit="GHz", save_single_fields=True)

    sweep2 = setup1.add_sweep()
    sweep2.sweep_type = "Discrete"
    sweep2.add_subrange("SinglePoints", 2.4, unit="GHz", save_single_fields=True)
    subranges = sweep2.props["SweepRanges"]["Subrange"]

    assert subranges == {
        "RangeType": "SinglePoints",
        "RangeStart": "2.4GHz",
        "RangeEnd": "2.4GHz",
        "SaveSingleField": True,
    }

    # Clearing replaces the primary range and removes any appended subranges.
    assert sweep1.add_subrange("LinearCount", 1, 2, 10, clear=True)
    assert sweep1.props["RangeType"] == "LinearCount"
    assert sweep1.props["RangeStart"] == "1GHz"
    assert sweep1.props["RangeEnd"] == "2GHz"
    assert sweep1.props["RangeCount"] == 10

    assert sweep1.add_subrange("LinearStep", 2, 3, 0.5, clear=True)
    assert sweep1.props["RangeType"] == "LinearStep"
    assert sweep1.props["RangeStep"] == "0.5GHz"

    assert sweep1.add_subrange("LogScale", 1, 10, 8, clear=True)
    assert sweep1.props["RangeType"] == "LogScale"
    assert sweep1.props["RangeSamples"] == 8

    sweep1.sweep_type = "Discrete"
    assert sweep1.add_subrange("SinglePoints", 2.4, clear=True, save_single_fields=True)
    assert sweep1.props["RangeType"] == "SinglePoints"
    assert sweep1.props["RangeStart"] == "2.4GHz"
    assert sweep1.props["RangeEnd"] == "2.4GHz"
    assert sweep1.props["SaveSingleField"]


def test_frequency_sweep(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)

    with pytest.raises(ValueError):
        setup1.create_frequency_sweep(start_frequency=1, stop_frequency="500MHz", sweep_type="invented")

    discrete = setup1.create_frequency_sweep(unit="GHz", start_frequency=1, stop_frequency=2)
    assert discrete.name in setup1.sweep_names
    assert discrete.props["RangeType"] == "LinearCount"
    assert discrete.props["RangeStart"] == "1GHz"
    assert discrete.props["RangeEnd"] == "2GHz"
    assert discrete.props["RangeCount"] == 5
    assert discrete.props["Type"] == "Discrete"
    assert discrete.props["SaveFields"] is True
    assert discrete.props["SaveRadFields"] is False

    interpolating = setup1.create_frequency_sweep(
        unit="GHz",
        start_frequency=2,
        stop_frequency=4,
        sweep_type="Interpolating",
        interpolation_tol=0.25,
        interpolation_max_solutions=120,
        save_fields=False,
        save_rad_fields=True,
    )
    assert interpolating.props["RangeCount"] == 401
    assert interpolating.props["Type"] == "Interpolating"
    assert interpolating.props["InterpTolerance"] == 0.25
    assert interpolating.props["InterpMaxSolns"] == 120
    assert interpolating.props["InterpMinSolns"] == 0
    assert interpolating.props["InterpMinSubranges"] == 1
    assert interpolating.props["SaveFields"] is False
    assert interpolating.props["SaveRadFields"] is True

    fast = setup1.create_frequency_sweep(
        unit="GHz", start_frequency=3, stop_frequency=5, sweep_type="Fast", num_of_freq_points=50
    )
    assert fast.props["RangeCount"] == 50
    assert fast.props["Type"] == "Fast"

    named = setup1.create_frequency_sweep(unit="GHz", name="NamedSweep")
    duplicate_name = setup1.create_frequency_sweep(unit="GHz", name="NamedSweep")
    assert named.name == "NamedSweep"
    assert duplicate_name.name != named.name
    assert duplicate_name.name in setup1.sweep_names


def test_linear_step_sweep(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)

    with pytest.raises(AttributeError):
        setup.create_linear_step_sweep(sweep_type="invented")

    discrete = setup.create_linear_step_sweep(unit="MHz", start_frequency=100, stop_frequency=300, step_size=25)
    assert discrete.name in setup.sweep_names
    assert discrete.props["RangeType"] == "LinearStep"
    assert discrete.props["RangeStart"] == "100MHz"
    assert discrete.props["RangeEnd"] == "300MHz"
    assert discrete.props["RangeStep"] == "25MHz"
    assert discrete.props["Type"] == "Discrete"
    assert discrete.props["SaveFields"] is True
    assert discrete.props["SaveRadFields"] is False

    interpolating = setup.create_linear_step_sweep(
        unit="GHz",
        start_frequency=1,
        stop_frequency=3,
        step_size=0.5,
        name="InterpolatingStep",
        sweep_type="Interpolating",
        save_fields=False,
        save_rad_fields=True,
    )
    assert interpolating.props["Type"] == "Interpolating"
    assert interpolating.props["InterpTolerance"] == 0.5
    assert interpolating.props["InterpMaxSolns"] == 250
    assert interpolating.props["InterpMinSolns"] == 0
    assert interpolating.props["InterpMinSubranges"] == 1
    assert interpolating.props["SaveFields"] is False
    assert interpolating.props["SaveRadFields"] is True

    fast = setup.create_linear_step_sweep(
        unit="GHz", start_frequency=1, stop_frequency=2, step_size=0.1, name="FastStep", sweep_type="Fast"
    )
    assert fast.props["Type"] == "Fast"

    duplicate_name = setup.create_linear_step_sweep(
        unit="GHz", name="FastStep", start_frequency=1, stop_frequency=2, step_size=0.1
    )
    assert duplicate_name.name != fast.name
    assert duplicate_name.name in setup.sweep_names


def test_single_point_sweep(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)

    with pytest.raises(AttributeError):
        setup.create_single_point_sweep(freq=[1, 2], save_single_field=[True])
    with pytest.raises(AttributeError):
        setup.create_single_point_sweep(freq=[])

    single = setup.create_single_point_sweep(
        unit="MHz", freq=1200, name="SinglePoint", save_single_field=False, save_fields=True, save_rad_fields=True
    )
    assert single.name in setup.sweep_names
    assert single.props["RangeType"] == "SinglePoints"
    assert single.props["RangeStart"] == "1200MHz"
    assert single.props["RangeEnd"] == "1200MHz"
    assert single.props["SaveSingleField"] is False
    assert single.props["SaveFields"] is True
    assert single.props["SaveRadFields"] is True
    assert single.props["Type"] == "Discrete"

    duplicate_name = setup.create_single_point_sweep(unit="GHz", freq=2, name="SinglePoint")
    assert duplicate_name.name != single.name
    assert duplicate_name.name in setup.sweep_names

    multiple = setup.create_single_point_sweep(
        unit="GHz", freq=[1.1, 1.2, 1.3], name="MultiplePoints", save_single_field=[True, False, True]
    )
    assert multiple.props["RangeStart"] == "1.1GHz"
    assert multiple.props["RangeEnd"] == "1.1GHz"
    subranges = multiple.props["SweepRanges"]["Subrange"]
    assert [subrange["RangeStart"] for subrange in subranges] == ["1.2GHz", "1.3GHz"]
    assert [subrange["SaveSingleField"] for subrange in subranges] == [False, True]


def test_setup_auto_open(hfss_app) -> None:
    hfss_app.set_auto_open()
    setup1 = hfss_app.get_setup("Auto1")
    assert setup1.name in hfss_app.setup_names


def test_hfss_derivatives(hfss_app) -> None:
    hfss_app["der_var"] = "1mm"
    hfss_app["der_var2"] = "2mm"

    setup3 = hfss_app.create_setup("MySetup_3", setup_type=1)
    assert setup3.add_derivatives("der_var")
    assert setup3.props["VariablesForDerivatives"][0] == "der_var"
    assert "der_var" in setup3.get_derivative_variables()

    assert setup3.add_derivatives("der_var2")
    assert len(setup3.props["VariablesForDerivatives"]) == 2
    assert not hfss_app.post.set_tuning_offset(setup3.name, {"der_var": 0.05})
    assert "der_var2" in setup3.get_derivative_variables()
    assert "der_var" in setup3.get_derivative_variables()


def test_auto(hfss_app) -> None:
    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    assert isinstance(setup1, SetupHFSSAuto)
    assert not setup1.is_solved

    setup1.auto_solver_settings = "Balanced"
    assert setup1.props["AutoSolverSetting"] == "Balanced"
    setup1.auto_solver_settings = "Higher Accuracy"
    assert setup1.props["AutoSolverSetting"] == "Higher Accuracy"
    setup1.auto_solver_settings = "invented"
    assert setup1.props["AutoSolverSetting"] == "Higher Accuracy"

    setup1.disable()
    assert not setup1["IsEnabled"]
    setup1.enable()
    assert setup1["IsEnabled"]

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in hfss_app.setup_names
    assert name not in hfss_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Delete
    setup2 = hfss_app.create_setup(Setups.HFSSDrivenAuto)
    assert hfss_app.delete_setup(name=setup1.name)
    assert "new_name" not in hfss_app.setup_names
    assert not hfss_app.delete_setup(name="invented")

    name2 = setup1.name
    setup2.delete()
    assert name2 not in hfss_app.setup_names


def test_auto_subranges(hfss_app):
    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)

    assert setup1.add_subrange("LinearStep", 1, 10, 0.1, unit="GHz", clear=False)
    subranges = setup1.props["Sweeps"]["Sweep"]["SweepRanges"]["Subrange"]
    assert subranges["RangeType"] == "LinearStep"

    assert setup1.add_subrange("LogScale", 1, 10, 8, unit="GHz", clear=False)
    subranges = setup1.props["Sweeps"]["Sweep"]["SweepRanges"]["Subrange"]
    assert subranges[1]["RangeType"] == "LogScale"
    assert subranges[1]["RangeSamples"] == 8

    assert setup1.add_subrange("LinearCount", 10, 20, 10, unit="GHz", clear=False)
    subranges = setup1.props["Sweeps"]["Sweep"]["SweepRanges"]["Subrange"]
    assert subranges[2]["RangeType"] == "LinearCount"
    assert subranges[2]["RangeCount"] == 10

    assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)
    sweep_props = setup1.props["Sweeps"]["Sweep"]
    assert sweep_props["RangeType"] == "LinearCount"
    assert sweep_props["RangeStart"] == "10GHz"
    assert sweep_props["RangeEnd"] == "20GHz"
    assert sweep_props["RangeCount"] == 10

    assert setup1.add_subrange("LinearStep", 20, 30, 30, clear=True)
    sweep_props = setup1.props["Sweeps"]["Sweep"]
    assert sweep_props["RangeType"] == "LinearStep"
    assert sweep_props["RangeStart"] == "20GHz"
    assert sweep_props["RangeEnd"] == "30GHz"
    assert sweep_props["RangeStep"] == "30GHz"

    assert setup1.add_subrange("LogScale", 2, 200, 1, clear=True)
    sweep_props = setup1.props["Sweeps"]["Sweep"]
    assert sweep_props["RangeType"] == "LogScale"
    assert sweep_props["RangeStart"] == "2GHz"
    assert sweep_props["RangeEnd"] == "200GHz"
    assert sweep_props["RangeCount"] == 10


def test_auto_derivatives(hfss_app) -> None:
    hfss_app["der_var"] = "1mm"
    hfss_app["der_var2"] = "2mm"

    setup3 = hfss_app.create_setup(setup_type=0)
    assert setup3.add_derivatives("der_var")
    assert setup3.props["VariablesForDerivatives"][0] == "der_var"
    assert "der_var" in setup3.get_derivative_variables()

    assert setup3.add_derivatives("der_var2")
    assert len(setup3.props["VariablesForDerivatives"]) == 2
    assert not hfss_app.post.set_tuning_offset(setup3.name, {"der_var": 0.05})
    assert "der_var2" in setup3.get_derivative_variables()
    assert "der_var" in setup3.get_derivative_variables()


def test_sweep_sbr(hfss_app) -> None:
    hfss_app.solution_type = "SBR+"

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSSBR)
    assert setup1.name in hfss_app.setup_names
    assert not setup1.props["ComputeFields"]

    p1 = hfss_app.insert_infinite_sphere()
    setup2 = hfss_app.create_setup(name=setup1.name)
    assert setup2.name in hfss_app.setup_names
    assert setup2.props["ComputeFields"]
    assert setup2.props["RadiationSetup"] == p1.name

    # Edit
    setup2["RayDensityPerWavelength"] = 1
    assert setup2.props["RayDensityPerWavelength"] == 1

    # Add Subrange
    assert setup2.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
    assert setup2.props["Sweeps"]["Sweep"]["SweepRanges"]["Subrange"]["RangeStart"] == "1GHz"
    assert setup2.add_subrange("LinearCount", 10, 20, 10, clear=True)
    assert setup2.props["Sweeps"]["Sweep"]["RangeEnd"] == "20GHz"
    assert "SweepRanges" not in setup2.props["Sweeps"]["Sweep"]

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in hfss_app.setup_names
    assert name not in hfss_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Delete
    assert hfss_app.delete_setup(name=setup1.name)
    assert "new_name" not in hfss_app.setup_names

    hfss_app.solution_type = "Modal"
    hfss_app.hybrid = True
    box = hfss_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    hfss_app.assign_hybrid_region(box, hybrid_region="SBR+")

    with pytest.raises(AEDTRuntimeError):
        hfss_app.create_setup(setup_type=Setups.HFSSDrivenDefault)

    hfss_app.insert_infinite_sphere()
    setup3 = hfss_app.create_setup(setup_type=Setups.HFSSDrivenDefault)
    assert setup3.name in hfss_app.setup_names
    setup3["RayDensityPerWavelength"] = 1
    assert setup3.props["RayDensityPerWavelength"] == 1


def test_add_doppler_sweep(hfss_app) -> None:
    compfile = hfss_app.components3d["Male_Arm_Left"]
    hfss_app.modeler.insert_3d_component(compfile)

    with pytest.raises(AEDTRuntimeError):
        hfss_app.create_sbr_pulse_doppler_setup(sweep_time_duration=1e-5)

    hfss_app.solution_type = "SBR+"
    with pytest.raises(ValueError):
        hfss_app.create_sbr_pulse_doppler_setup(sweep_time_duration=1e-5)

    hfss_app["time_pyaedt"] = "500ms"

    setup, sweep = hfss_app.create_sbr_pulse_doppler_setup(sweep_time_duration=1e-5)
    assert setup.name in hfss_app.setup_names
    assert isinstance(setup, SetupSBR)
    assert sweep.name in hfss_app.parametrics.setup_names
    assert isinstance(sweep, ParametricSetup)

    assert setup.props["SbrRangeDopplerWaveformType"] == "PulseDoppler"
    assert sweep.props["Sim. Setups"] == [setup.name]

    setup2, sweep2 = hfss_app.create_sbr_pulse_doppler_setup(
        setup=setup.name, sweep_time_duration=1e-5, time_variable="time_pyaedt"
    )
    assert setup2.name in hfss_app.setup_names
    assert isinstance(setup2, SetupSBR)
    assert sweep2.name in hfss_app.parametrics.setup_names
    assert isinstance(sweep2, ParametricSetup)

    setup3, sweep3 = hfss_app.create_sbr_pulse_doppler_setup(
        setup="new", sweep_time_duration=0, time_variable="time_pyaedt"
    )
    assert setup3.name in hfss_app.setup_names
    assert isinstance(setup3, SetupSBR)
    assert not sweep3


def test_add_doppler_chirp_i(hfss_app) -> None:
    compfile = hfss_app.components3d["Male_Arm_Left"]
    hfss_app.modeler.insert_3d_component(compfile)

    with pytest.raises(AEDTRuntimeError):
        hfss_app.create_sbr_chirp_i_doppler_setup(sweep_time_duration=1e-5)

    hfss_app.solution_type = "SBR+"
    with pytest.raises(ValueError):
        hfss_app.create_sbr_chirp_i_doppler_setup(sweep_time_duration=1e-5)

    hfss_app["time_pyaedt"] = "500ms"

    setup, sweep = hfss_app.create_sbr_chirp_i_doppler_setup(sweep_time_duration=1e-5)
    assert setup.name in hfss_app.setup_names
    assert isinstance(setup, SetupSBR)
    assert sweep.name in hfss_app.parametrics.setup_names
    assert isinstance(sweep, ParametricSetup)

    assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
    assert setup.props["ChannelConfiguration"] == "IChannelOnly"
    assert sweep.props["Sim. Setups"] == [setup.name]

    setup2, sweep2 = hfss_app.create_sbr_chirp_i_doppler_setup(
        setup=setup.name, sweep_time_duration=1e-5, time_variable="time_pyaedt"
    )
    assert setup2.name in hfss_app.setup_names
    assert isinstance(setup2, SetupSBR)
    assert sweep2.name in hfss_app.parametrics.setup_names
    assert isinstance(sweep2, ParametricSetup)

    setup3, sweep3 = hfss_app.create_sbr_chirp_i_doppler_setup(
        setup="new", sweep_time_duration=0, time_variable="time_pyaedt"
    )
    assert setup3.name in hfss_app.setup_names
    assert isinstance(setup3, SetupSBR)
    assert not sweep3


def test_add_doppler_chirp_iq(hfss_app) -> None:
    compfile = hfss_app.components3d["Male_Arm_Left"]
    hfss_app.modeler.insert_3d_component(compfile)

    with pytest.raises(AEDTRuntimeError):
        hfss_app.create_sbr_chirp_iq_doppler_setup(sweep_time_duration=1e-5)

    hfss_app.solution_type = "SBR+"
    with pytest.raises(ValueError):
        hfss_app.create_sbr_chirp_iq_doppler_setup(sweep_time_duration=1e-5)

    hfss_app["time_pyaedt"] = "500ms"

    setup, sweep = hfss_app.create_sbr_chirp_iq_doppler_setup(sweep_time_duration=1e-5)
    assert setup.name in hfss_app.setup_names
    assert isinstance(setup, SetupSBR)
    assert sweep.name in hfss_app.parametrics.setup_names
    assert isinstance(sweep, ParametricSetup)

    assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
    assert setup.props["ChannelConfiguration"] == "IQChannels"
    assert sweep.props["Sim. Setups"] == [setup.name]

    setup2, sweep2 = hfss_app.create_sbr_chirp_iq_doppler_setup(
        setup=setup.name, sweep_time_duration=1e-5, time_variable="time_pyaedt"
    )
    assert setup2.name in hfss_app.setup_names
    assert isinstance(setup2, SetupSBR)
    assert sweep2.name in hfss_app.parametrics.setup_names
    assert isinstance(sweep2, ParametricSetup)

    setup3, sweep3 = hfss_app.create_sbr_chirp_iq_doppler_setup(
        setup="new", sweep_time_duration=0, time_variable="time_pyaedt"
    )
    assert setup3.name in hfss_app.setup_names
    assert isinstance(setup3, SetupSBR)
    assert not sweep3


def test_eigen(hfss_app) -> None:
    hfss_app.solution_type = "Eigenmode"

    setup1 = hfss_app.create_setup("My_HFSS_Setup")
    assert setup1.solver_type == SetupKeys.SetupNames[Setups.HFSSEigen]

    assert isinstance(setup1, SetupHFSS)

    assert not setup1.is_solved

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in hfss_app.setup_names
    assert name not in hfss_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Sweep
    assert not setup1.sweep_names

    # Props
    assert "NumModes" in setup1.props
    setup1["NumModes"] = 5
    assert setup1["NumModes"] == 5

    setup1.disable()
    assert not setup1["IsEnabled"]
    setup1.enable()
    assert setup1["IsEnabled"]

    # Delete
    assert hfss_app.delete_setup(name=setup1.name)
    assert "new_name" not in hfss_app.setup_names
    assert not hfss_app.delete_setup(name="invented")

    setup2 = hfss_app.create_setup(setup_type=Setups.HFSSEigen)
    name2 = setup2.name
    assert setup2.name in hfss_app.setup_names
    setup2.delete()
    assert name2 not in hfss_app.setup_names


def test_transient(hfss_app) -> None:
    hfss_app.solution_type = "Transient"

    setup1 = hfss_app.create_setup("My_HFSS_Setup")
    assert setup1.solver_type == SetupKeys.SetupNames[Setups.HFSSTransient]

    assert isinstance(setup1, SetupHFSS)

    assert not setup1.is_solved

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in hfss_app.setup_names
    assert name not in hfss_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Sweep
    assert len(setup1.sweep_names) == 1

    # Props
    assert "Transient" in setup1.props
    setup1["Transient"]["SweepMaxFreq"] = "2GHz"
    assert setup1.props["Transient"]["SweepMaxFreq"] == "2GHz"

    setup1.disable()
    assert not setup1["IsEnabled"]
    setup1.enable()
    assert setup1["IsEnabled"]

    # Delete
    assert hfss_app.delete_setup(name=setup1.name)
    assert "new_name" not in hfss_app.setup_names
    assert not hfss_app.delete_setup(name="invented")

    setup2 = hfss_app.create_setup(setup_type=Setups.HFSSTransient)
    name2 = setup2.name
    assert name2 in hfss_app.setup_names
    setup2.delete()
    assert name2 not in hfss_app.setup_names


def test_cma(hfss_app) -> None:
    hfss_app.solution_type = "Characteristic"

    setup1 = hfss_app.create_setup("My_HFSS_Setup")
    assert setup1.solver_type == SetupKeys.SetupNames[Setups.HFSSCMA]

    assert isinstance(setup1, SetupHFSS)

    assert not setup1.is_solved

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in hfss_app.setup_names
    assert name not in hfss_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Sweep
    assert not len(setup1.sweep_names)

    # Props
    assert "MaxDeltaE" in setup1.props
    setup1["MaxDeltaE"] = 1
    assert setup1.props["MaxDeltaE"] == 1

    setup1.disable()
    assert not setup1["IsEnabled"]
    setup1.enable()
    assert setup1["IsEnabled"]

    # Delete
    assert hfss_app.delete_setup(name=setup1.name)
    assert "new_name" not in hfss_app.setup_names
    assert not hfss_app.delete_setup(name="invented")

    setup2 = hfss_app.create_setup(setup_type=Setups.HFSSCMA)
    name2 = setup2.name
    assert name2 in hfss_app.setup_names
    setup2.delete()
    assert name2 not in hfss_app.setup_names
