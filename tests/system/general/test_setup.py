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

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.generic.aedt_constants import Setups
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.setup_templates import HFSS3DLayout_AdaptiveFrequencyData
from ansys.aedt.core.modules.solve_setup import Setup3DLayout

TEST_SUBFOLDER = "T11"
TEST_COAXIAL = "coax_setup_231"


@pytest.fixture
def aedtapp(add_app_example):
    app = add_app_example(application=Hfss, project=TEST_COAXIAL, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def circuit_app(add_app):
    app = add_app(application=Circuit)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def layout_app(add_app):
    app = add_app(application=Hfss3dLayout)
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


# HFSS 3D Layout setups
def test_create_setup_layout_hfss(layout_app) -> None:
    adaptive_props = HFSS3DLayout_AdaptiveFrequencyData("6GHz")
    adaptive_settings = {"SingleFrequencyDataList": {"AdaptiveFrequencyData": {}}}
    adaptive_settings["SingleFrequencyDataList"]["AdaptiveFrequencyData"] = adaptive_props

    props = {"MaxRatio": 1, "AdaptiveSettings": adaptive_settings}

    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayout, MeshSizeFactor=2, props=props)
    name = setup.name
    assert name in layout_app.setup_names
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == f"{name} : LastAdaptive"
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    assert setup.props["MaxRatio"] == 1
    assert setup.props["MeshSizeFactor"] == 2
    assert (
        setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"]
        == "6GHz"
    )

    assert "Freq" in setup.default_intrinsics
    assert not setup.is_solved
    assert setup.solver_type == "HFSS"

    # Edit setup
    setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"] = "1GHz"
    assert (
        setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"]
        == "1GHz"
    )

    setup2 = layout_app.create_setup(setup_type="HFSS3DLayout")
    name2 = setup2.name
    assert name2 in layout_app.setup_names
    assert len(layout_app.setups) == 2
    assert isinstance(setup2, Setup3DLayout)
    assert str(setup2) == f"{name2} : LastAdaptive"
    assert setup2.__repr__() == f"{name2} with 0 Sweeps"

    # Repeated name
    setup3 = layout_app.create_setup(name=setup.name)
    name3 = setup3.name
    assert name3 != name
    assert name3 in layout_app.setup_names
    assert len(layout_app.setups) == 3
    assert isinstance(setup3, Setup3DLayout)
    assert str(setup3) == f"{name3} : LastAdaptive"
    assert setup3.__repr__() == f"{name3} with 0 Sweeps"

    with pytest.raises(AEDTRuntimeError):
        layout_app.create_setup(setup_type=Setups.RaptorX)

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    # Delete
    assert layout_app.delete_setup(name=setup3.name)
    assert name3 not in layout_app.setup_names
    assert len(layout_app.setups) == 2
    assert not layout_app.delete_setup(name="invented")

    setup2.delete()
    assert name2 not in layout_app.setup_names
    assert len(layout_app.setups) == 1


def test_create_setup_layout_hfss_sweep(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayout)

    assert not setup.get_sweeps()

    sweep = setup.add_sweep()

    sweep_1 = setup.get_sweeps()
    assert sweep_1.name == sweep.name
    sweep_2 = setup.get_sweeps(sweep.name)
    assert sweep_2.name == sweep.name
    assert not setup.get_sweeps("invented")

    assert not setup.get_sweeps()

    assert len(setup.sweeps) == 1
    assert sweep.name in setup.sweep_names
    assert sweep.sweep_type == "Interpolating"

    sweep2 = setup.add_sweep(name="my_sweep", sweep_type="discrete")
    assert len(setup.sweeps) == 2
    assert sweep2.name in setup.sweep_names
    assert sweep2.sweep_type == "Discrete"

    sweep3 = setup.add_sweep(name="my_sweep", sweep_type="Fast")
    assert len(setup.sweeps) == 3
    assert sweep3.name in setup.sweep_names
    assert sweep3.sweep_type == "BroadbandFast"

    sweep3.name = "new_sweep"
    assert "new_sweep" in setup.sweep_names
    assert "new_sweep" == sweep3.name
    assert sweep3.sweep_type == "BroadbandFast"

    with pytest.raises(ValueError):
        sweep3.name = "new_sweep"

    assert setup.delete_sweep(name=sweep3.name)
    assert len(setup.sweeps) == 2
    assert not setup.delete_sweep(name="invented")
    assert sweep2.delete()
    assert len(setup.sweeps) == 1

    assert not sweep.is_solved

    sweep.sweep_type = "Fast"
    assert sweep.sweep_type == "BroadbandFast"

    assert sweep.change_type("Discrete")
    assert sweep.sweep_type == "Discrete"

    assert sweep.change_type("Interpolating")
    assert sweep.sweep_type == "Interpolating"

    assert sweep.change_type("invented")
    assert sweep.sweep_type == "Interpolating"

    sweep.change_type("Discrete")
    sweep.props["GenerateSurfaceCurrent"] = True
    assert sweep.props["GenerateSurfaceCurrent"]
    assert sweep.set_save_fields(False, False)
    assert not sweep.props["GenerateSurfaceCurrent"]

    sweep.change_type("Interpolating")
    with pytest.raises(AttributeError):
        sweep.add_subrange(range_type="SinglePoint", start=2)

    with pytest.raises(AttributeError):
        sweep.add_subrange(range_type="LinearCount", start=2)

    assert sweep.add_subrange(range_type="LinearCount", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LINC 1GHz 5GHz 501 LINC 2GHz 4GHz 10"

    assert sweep.add_subrange(range_type="LinearStep", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LINC 1GHz 5GHz 501 LINC 2GHz 4GHz 10 LIN 2GHz 4GHz 10GHz"

    assert sweep.add_subrange(range_type="LogScale", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LINC 1GHz 5GHz 501 LINC 2GHz 4GHz 10 LIN 2GHz 4GHz 10GHz DEC 2GHz 4GHz 10"

    sweep.change_type("Discrete")
    assert sweep.add_subrange(range_type="SinglePoint", start=2)
    assert (
        sweep.props["Sweeps"]["Data"]
        == "LINC 1GHz 5GHz 501 LINC 2GHz 4GHz 10 LIN 2GHz 4GHz 10GHz DEC 2GHz 4GHz 10 2GHz"
    )

    with pytest.raises(AttributeError):
        sweep.add_subrange(range_type="invented", start=2)

    assert sweep.change_range(range_type="LinearCount", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LINC 2GHz 4GHz 10"

    assert sweep.change_range(range_type="LinearStep", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LIN 2GHz 4GHz 10GHz"

    assert sweep.change_range(range_type="LogScale", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "DEC 2GHz 4GHz 10"

    assert sweep.change_range(range_type="SinglePoint", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "2GHz"

    with pytest.raises(AttributeError):
        sweep.change_range(range_type="invented", start=2)


def test_create_setup_layout_raptorx(layout_app) -> None:
    layout_app.ic_mode = True
    layout_app.create_setup(name="setup1", setup_type="RaptorX")
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_setup_layout_hfss_auto(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_setup_layout_hfss_pi(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"
    # Add sweep


def test_create_setup_layout_emi(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_setup_layout_ami(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_setup_layout_lna(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_setup_layout_quickeye(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_setup_layout_siwave_syz(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"
    # Add sweep


def test_create_setup_layout_siwave_dcir(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_setup_layout_siwave_farfield(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"
    # Add sweep


def test_create_setup_layout_siwave_nearfield(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"
    # Add sweep


def test_create_setup_layout_siwave_transient(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_setup_layout_siwave_verify_eye(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_create_hfss_setup(aedtapp) -> None:
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.name == "My_HFSS_Setup"
    assert aedtapp.setups[0].name == setup1.name
    assert "SaveRadFieldsOnly" in setup1.props
    assert "SaveRadFieldsOnly" in setup1.available_properties
    setup1["SaveRadFieldsonly"] = True
    assert setup1.props["SaveRadFieldsOnly"] == setup1["SaveRadFieldsonly"]
    assert setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
    assert setup1.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Delta"] == 0.02
    assert setup1.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"] == "1GHz"
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


def test_create_hfss_sweep(aedtapp) -> None:
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


def test_create_hfss_setup_auto_open(aedtapp) -> None:
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


def test_create_circuit_setup(circuit_app) -> None:
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


def test_non_valid_setup(aedtapp) -> None:
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


def test_delete_setup(aedtapp) -> None:
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    assert len(aedtapp.setups) == 1
    assert setup1.delete()
    assert len(aedtapp.setups) == 0
    assert not aedtapp.get_setups()


def test_sweep_auto(aedtapp) -> None:
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    assert setup1.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
    assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)


def test_delete_sweep(aedtapp) -> None:
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    setup1.create_frequency_sweep("GHz", 24, 24.25, 26, "My_Sweep1", sweep_type="Fast")
    sweeps = setup1.get_sweep_names()
    assert len(sweeps) == 1
    assert "My_Sweep1" in sweeps
    setup1.delete_sweep("My_Sweep1")
    sweeps = setup1.get_sweep_names()
    assert len(sweeps) == 0


def test_sweep_sbr(aedtapp) -> None:
    aedtapp.solution_type = "SBR+"
    sph = aedtapp.insert_infinite_sphere()
    sph.props
    setup1 = aedtapp.create_setup("My_HFSS_Setup", Setups.HFSSSBR)
    assert setup1.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
    assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)
