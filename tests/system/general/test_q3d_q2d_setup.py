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

from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core.modules.solve_setup import SetupQ3D
from ansys.aedt.core.modules.solve_sweeps import SweepMatrix
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "TSetup"
TEST_Q3D_Q2D = "q3d_q2d_setup_test"


@pytest.fixture
def q3d_app(add_app):
    app = add_app(application=Q3d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def q2d_app(add_app):
    app = add_app(application=Q2d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def q3d_setup_app(add_app_example):
    app = add_app_example(application=Q3d, project=TEST_Q3D_Q2D, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def q2d_setup_app(add_app_example):
    app = add_app_example(application=Q2d, project=TEST_Q3D_Q2D, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Skipped on versions earlier than 2023.1")
def test_setup_q3d_init(q3d_setup_app):
    assert len(q3d_setup_app.setups) == 1
    assert isinstance(q3d_setup_app.setups[0], SetupQ3D)
    assert str(q3d_setup_app.setups[0]) == f"{q3d_setup_app.setups[0].name} : LastAdaptive"
    assert q3d_setup_app.setups[0].__repr__() == q3d_setup_app.setups[0].name
    assert q3d_setup_app.setups[0].solver_type == "Matrix"

    assert len(q3d_setup_app.setups[0].sweep_names) == 1
    assert len(q3d_setup_app.setups[0].sweeps) == 1
    assert isinstance(q3d_setup_app.setups[0].sweeps[0], SweepMatrix)

    assert q3d_setup_app.setups[0].sweeps[0].is_solved
    assert len(q3d_setup_app.setups[0].sweeps[0].frequencies) == 1
    assert q3d_setup_app.setups[0].sweeps[0].sweep_type == "Discrete"
    assert q3d_setup_app.setups[0].sweeps[0].setup_name == q3d_setup_app.setups[0].name


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Skipped on versions earlier than 2026.1")
def test_setup_q2d_init(q2d_setup_app):
    assert len(q2d_setup_app.setups) == 1
    assert isinstance(q2d_setup_app.setups[0], SetupQ3D)
    assert str(q2d_setup_app.setups[0]) == f"{q2d_setup_app.setups[0].name} : LastAdaptive"
    assert q2d_setup_app.setups[0].__repr__() == q2d_setup_app.setups[0].name
    assert q2d_setup_app.setups[0].solver_type == "2DMatrix"

    assert len(q2d_setup_app.setups[0].sweep_names) == 1
    assert len(q2d_setup_app.setups[0].sweeps) == 1
    assert isinstance(q2d_setup_app.setups[0].sweeps[0], SweepMatrix)

    assert q2d_setup_app.setups[0].sweeps[0].is_solved
    assert q2d_setup_app.setups[0].sweeps[0].frequencies
    assert q2d_setup_app.setups[0].sweeps[0].sweep_type == "Discrete"
    assert q2d_setup_app.setups[0].sweeps[0].setup_name == q2d_setup_app.setups[0].name


def test_setup_q3d(q3d_app) -> None:
    props = {"AdaptiveFreq": "1GHz"}

    setup1 = q3d_app.create_setup(SaveFields=True, props=props)

    assert setup1.name == "MySetupAuto"
    assert q3d_app.setups[0].name == setup1.name
    assert setup1.name in q3d_app.setup_names
    assert isinstance(setup1, SetupQ3D)
    assert len(q3d_app.setup_names) == 1
    assert setup1.solver_type == "Matrix"
    assert not setup1.sweeps
    assert len(setup1.sweep_names) == 0
    assert setup1["AdaptiveFreq"] == "1GHz"
    assert setup1["SaveFields"]

    # Properties
    # Q3D enables capacitance, DC, and AC/RL by default.
    assert setup1.capacitance_enabled
    assert setup1.dc_enabled
    assert setup1.ac_rl_enabled
    assert not setup1.dc_resistance_only

    # Setting an already-enabled solution keeps its current state.
    setup1.capacitance_enabled = True
    setup1.dc_enabled = True
    setup1.ac_rl_enabled = True
    assert setup1.capacitance_enabled
    assert setup1.dc_enabled
    assert setup1.ac_rl_enabled

    # Turn AC/RL off while capacitance and DC remain active, then turn it back on.
    setup1.ac_rl_enabled = False
    assert not setup1.ac_rl_enabled
    setup1.ac_rl_enabled = True
    assert setup1.ac_rl_enabled

    # Capacitance can be disabled and re-enabled while AC/RL or DC remains active.
    setup1.capacitance_enabled = False
    assert not setup1.capacitance_enabled
    setup1.capacitance_enabled = True
    assert setup1.capacitance_enabled

    # DC can be disabled and re-enabled while AC/RL or capacitance remains active.
    setup1.dc_enabled = False
    assert not setup1.dc_enabled
    setup1.dc_enabled = True
    assert setup1.dc_enabled

    # DC resistance-only can be toggled, including repeated assignments.
    setup1.dc_resistance_only = True
    assert setup1.dc_resistance_only
    setup1.dc_resistance_only = True
    assert setup1.dc_resistance_only
    setup1.dc_resistance_only = False
    assert not setup1.dc_resistance_only
    setup1.dc_resistance_only = False
    assert not setup1.dc_resistance_only

    # With DC disabled, resistance-only remains false and cannot be enabled.
    setup1.dc_enabled = False
    assert not setup1.dc_enabled
    setup1.dc_resistance_only = True
    assert not setup1.dc_resistance_only

    # DC can remain as the only solution while capacitance is disabled.
    setup1.dc_enabled = True
    setup1.ac_rl_enabled = False
    setup1.capacitance_enabled = False
    assert not setup1.ac_rl_enabled
    assert not setup1.capacitance_enabled
    assert setup1.dc_enabled
    setup1.capacitance_enabled = True
    assert setup1.capacitance_enabled
    setup1.capacitance_enabled = False
    assert not setup1.capacitance_enabled

    # With DC as the only solution, AC/RL can be enabled as an alternative.
    setup1.ac_rl_enabled = True
    assert setup1.ac_rl_enabled

    # With capacitance as the only solution, disabling DC and enabling AC/RL are valid.
    setup1.capacitance_enabled = True
    setup1.ac_rl_enabled = False
    assert setup1.capacitance_enabled
    assert not setup1.ac_rl_enabled
    setup1.dc_enabled = False
    assert not setup1.dc_enabled
    setup1.ac_rl_enabled = True
    assert setup1.ac_rl_enabled

    # AC/RL can then be the only solution, allowing capacitance and DC to be enabled.
    setup1.capacitance_enabled = False
    assert not setup1.capacitance_enabled
    setup1.dc_enabled = True
    assert setup1.dc_enabled

    setup2 = q3d_app.create_setup()
    assert setup2.name in q3d_app.setup_names
    assert len(q3d_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in q3d_app.setup_names
    assert name not in q3d_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Edit
    setup1["AdaptiveFreq"] = "10GHz"
    assert setup1["AdaptiveFreq"] == "10GHz"

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert q3d_app.delete_setup(name=setup1.name)
    assert "new_name" not in q3d_app.setup_names
    assert not q3d_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in q3d_app.setup_names


def test_setup_q2d(q2d_app) -> None:
    props = {"AdaptiveFreq": "1GHz"}

    setup1 = q2d_app.create_setup(SaveFields=True, props=props)

    assert setup1.name == "MySetupAuto"
    assert q2d_app.setups[0].name == setup1.name
    assert setup1.name in q2d_app.setup_names
    assert isinstance(setup1, SetupQ3D)
    assert len(q2d_app.setup_names) == 1
    assert setup1.solver_type == "2DMatrix"
    assert not setup1.sweeps
    assert len(setup1.sweep_names) == 0
    assert setup1["AdaptiveFreq"] == "1GHz"
    assert setup1["SaveFields"]

    # Properties
    # AC/RL can be toggled while the default capacitance solution stays enabled.
    setup1.ac_rl_enabled = True
    assert setup1.ac_rl_enabled
    setup1.ac_rl_enabled = False
    assert not setup1.ac_rl_enabled

    # Disabling the last active solution is ignored because ac_rl_enabled is disabled.
    setup1.capacitance_enabled = False
    assert setup1.capacitance_enabled

    # Capacitance can be disabled when AC/RL is active.
    setup1.ac_rl_enabled = True
    assert setup1.ac_rl_enabled
    setup1.capacitance_enabled = False
    assert not setup1.capacitance_enabled

    # Repeating the current value is a no-op; enabling capacitance is allowed again.
    setup1.capacitance_enabled = False
    assert not setup1.capacitance_enabled
    setup1.capacitance_enabled = True
    assert setup1.capacitance_enabled
    setup1.capacitance_enabled = True
    assert setup1.capacitance_enabled

    # Q2D does not support DC properties; setters leave their getters as None.
    setup1.dc_enabled = True
    assert setup1.dc_enabled is None
    setup1.dc_enabled = False
    assert setup1.dc_enabled is None
    setup1.dc_resistance_only = True
    assert setup1.dc_resistance_only is None
    setup1.dc_resistance_only = False
    assert setup1.dc_resistance_only is None

    setup2 = q2d_app.create_setup()
    assert setup2.name in q2d_app.setup_names
    assert len(q2d_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in q2d_app.setup_names
    assert name not in q2d_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Edit
    setup1["AdaptiveFreq"] = "10GHz"
    assert setup1["AdaptiveFreq"] == "10GHz"

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert q2d_app.delete_setup(name=setup1.name)
    assert "new_name" not in q2d_app.setup_names
    assert not q2d_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in q2d_app.setup_names


@pytest.mark.parametrize("app_fixture", ["q3d_app", "q2d_app"])
def test_add_subrange(request, app_fixture) -> None:
    app = request.getfixturevalue(app_fixture)
    setup = app.create_setup("SweepSetup")
    sweep = setup.add_sweep("SubrangeSweep")
    assert isinstance(sweep, SweepMatrix)

    with pytest.raises(AttributeError):
        sweep.add_subrange(range_type="LinearCount", start=1)

    assert sweep.add_subrange("LinearCount", 1, 2, 10, unit="MHz")
    assert sweep.add_subrange("LinearStep", 2, 3, 0.25, unit="GHz")
    assert sweep.add_subrange("LogScale", 1, 10, 5, unit="GHz")
    subranges = sweep.props["SweepRanges"]["Subrange"]
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

    assert sweep.add_subrange("LinearCount", 1, 2, 10, clear=True)
    assert sweep.props["RangeType"] == "LinearCount"
    assert sweep.props["RangeStart"] == "1GHz"
    assert sweep.props["RangeEnd"] == "2GHz"
    assert sweep.props["RangeCount"] == 10

    sweep.sweep_type = "Discrete"
    assert sweep.add_subrange("SinglePoints", start=2.4, clear=True, save_single_fields=True)
    assert sweep.props["RangeType"] == "SinglePoints"
    assert sweep.props["RangeStart"] == "2.4GHz"
    assert sweep.props["RangeEnd"] == "2.4GHz"


@pytest.mark.parametrize("app_fixture", ["q3d_app", "q2d_app"])
def test_frequency_sweep(request, app_fixture) -> None:
    app = request.getfixturevalue(app_fixture)
    setup = app.create_setup("FrequencySweepSetup")

    with pytest.raises(AttributeError):
        setup.create_frequency_sweep(start_frequency=1, stop_frequency=2, sweep_type="invented")

    discrete = setup.create_frequency_sweep(unit="GHz", start_frequency=1, stop_frequency=2)
    assert discrete.name in setup.sweep_names
    assert discrete.props["RangeType"] == "LinearCount"
    assert discrete.props["RangeStart"] == "1GHz"
    assert discrete.props["RangeEnd"] == "2GHz"
    assert discrete.props["RangeCount"] == 5
    assert discrete.props["Type"] == "Discrete"

    interpolating = setup.create_frequency_sweep(
        unit="GHz",
        start_frequency=2,
        stop_frequency=4,
        sweep_type="Interpolating",
        interpolation_tol=0.25,
        interpolation_max_solutions=120,
    )
    assert interpolating.props["RangeCount"] == 401
    assert interpolating.props["Type"] == "Interpolating"
    assert interpolating.props["InterpTolerance"] == 0.25
    assert interpolating.props["InterpMaxSolns"] == 120
    assert interpolating.props["InterpMinSolns"] == 0
    assert interpolating.props["InterpMinSubranges"] == 1

    fast = setup.create_frequency_sweep(
        unit="GHz", start_frequency=3, stop_frequency=5, sweep_type="Fast", num_of_freq_points=50
    )
    assert fast.props["RangeCount"] == 50
    assert fast.props["Type"] == "Fast"

    named = setup.create_frequency_sweep(unit="GHz", name="NamedSweep")
    duplicate_name = setup.create_frequency_sweep(unit="GHz", name="NamedSweep")
    assert named.name == "NamedSweep"
    assert duplicate_name.name != named.name
    assert duplicate_name.name in setup.sweep_names


@pytest.mark.parametrize("app_fixture", ["q3d_app", "q2d_app"])
def test_linear_step_sweep(request, app_fixture) -> None:
    app = request.getfixturevalue(app_fixture)
    setup = app.create_setup("LinearStepSetup")

    with pytest.raises(AttributeError):
        setup.create_linear_step_sweep(sweep_type="invented")

    discrete = setup.create_linear_step_sweep(unit="MHz", start_frequency=100, stop_frequency=300, step_size=25)
    assert discrete.name in setup.sweep_names
    assert discrete.props["RangeType"] == "LinearStep"
    assert discrete.props["RangeStart"] == "100MHz"
    assert discrete.props["RangeEnd"] == "300MHz"
    assert discrete.props["RangeStep"] == "25MHz"
    assert discrete.props["Type"] == "Discrete"
    assert discrete.props["SaveFields"]
    assert not discrete.props["SaveRadFields"]

    interpolating = setup.create_linear_step_sweep(
        unit="GHz",
        start_frequency=1,
        stop_frequency=3,
        step_size=0.5,
        name="InterpolatingStep",
        sweep_type="Interpolating",
        save_fields=False,
    )
    assert interpolating.props["Type"] == "Interpolating"
    assert interpolating.props["InterpTolerance"] == 0.5
    assert interpolating.props["InterpMaxSolns"] == 250
    assert interpolating.props["InterpMinSolns"] == 0
    assert interpolating.props["InterpMinSubranges"] == 1
    assert not interpolating.props["SaveFields"]

    duplicate_name = setup.create_linear_step_sweep(
        unit="GHz", name="InterpolatingStep", start_frequency=1, stop_frequency=2, step_size=0.1
    )
    assert duplicate_name.name != interpolating.name
    assert duplicate_name.name in setup.sweep_names


@pytest.mark.parametrize("app_fixture", ["q3d_app", "q2d_app"])
def test_single_point_sweep(request, app_fixture) -> None:
    app = request.getfixturevalue(app_fixture)
    setup = app.create_setup("SinglePointSetup")

    with pytest.raises(AttributeError):
        setup.create_single_point_sweep(freq=[1, 2], save_single_field=[True])
    with pytest.raises(AttributeError):
        setup.create_single_point_sweep(freq=[])

    single = setup.create_single_point_sweep(
        unit="MHz", freq=1200, name="SinglePoint", save_single_field=False, save_fields=True
    )
    assert single.name in setup.sweep_names
    assert single.props["RangeType"] == "SinglePoints"
    assert single.props["RangeStart"] == "1200MHz"
    assert single.props["RangeEnd"] == "1200MHz"
    assert not single.props["SaveSingleField"]
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
