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
from ansys.aedt.core.generic.aedt_constants import Setups
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import SetupQ3D
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


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_setup_q3d_init(q3d_setup_app):
    assert len(q3d_setup_app.setups) == 1
    assert isinstance(q3d_setup_app.setups[0], SetupQ3D)
    assert str(q3d_setup_app.setups[0]) == f"{q3d_setup_app.setups[0].name} : LastAdaptive"
    assert q3d_setup_app.setups[0].__repr__() == q3d_setup_app.setups[0].name
    assert q3d_setup_app.setups[0].solver_type == "Matrix"

    assert len(q3d_setup_app.setups[0].sweep_names) == 1
    assert len(q3d_setup_app.setups[0].sweeps) == 1


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_setup_q2d_init(q2d_setup_app):
    assert len(q2d_setup_app.setups) == 2
    assert isinstance(q2d_setup_app.setups[0], SetupQ3D)
    assert str(q2d_setup_app.setups[0]) == f"{q2d_setup_app.setups[0].name} : Sweep"
    assert q2d_setup_app.setups[0].__repr__() == q2d_setup_app.setups[0].name
    assert q2d_setup_app.setups[0].solver_type == SetupKeys.SetupNames[Setups.HFSSDrivenAuto]


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


def test_create_discrete_sweep(aedt_app) -> None:
    setup = aedt_app.create_setup()
    setup.props["SaveFields"] = True
    assert setup.update()
    assert setup.dc_enabled
    setup.dc_resistance_only = True
    assert setup.dc_resistance_only
    setup.dc_enabled = False
    setup.dc_enabled = True
    sweep = setup.create_frequency_sweep(name="mysweep", start_frequency=1, unit="GHz")
    assert sweep
    assert sweep.props["RangeStart"] == "1GHz"
    assert setup.children[sweep.name].properties["Start"] == "1GHz"
    sweep2 = setup.create_linear_step_sweep(
        name="StepFast",
        unit="GHz",
        start_frequency=1,
        stop_frequency=20,
        step_size=0.1,
        sweep_type="Interpolating",
    )
    assert setup.children[sweep2.name].properties["Start"] == "1GHz"
    assert setup.children[sweep2.name].properties["Stop"] == "20GHz"


def test_create_linear_sweep(aedt_app) -> None:
    setup = aedt_app.create_setup()
    assert setup.create_linear_step_sweep(
        unit="GHz",
        start_frequency=1,
        stop_frequency=20,
        step_size=0.1,
        sweep_type="Interpolating",
    )
    with pytest.raises(AttributeError) as execinfo:
        setup.create_linear_step_sweep(
            name="invalid_sweep",
            unit="GHz",
            start_frequency=1,
            stop_frequency=20,
            step_size=0.1,
            sweep_type="Invalid",
        )
        assert execinfo.args[0] == "Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'"


def test_create_single_point_sweep(aedt_app) -> None:
    setup = aedt_app.create_setup()
    setup.props["SaveFields"] = True

    sweep = setup.create_single_point_sweep(save_fields=True, freq=5, unit="GHz")
    assert setup.children[sweep.name].properties["Start"] == "5GHz"

    sweep2 = setup.create_single_point_sweep(save_single_field=[True, False, False], freq=[6, 10, 12], unit="GHz")
    assert setup.children[sweep2.name].properties["Start"] == "6GHz"
    assert setup.children[sweep2.name].properties["Stop"] == "12GHz"


def test_create_frequency_sweep(aedt_app) -> None:
    setup = aedt_app.create_setup()
    setup.props["SaveFields"] = True
    assert setup.update()
    assert setup.create_frequency_sweep(
        unit="GHz",
        name="Sweep1",
        start_frequency=9.5,
        stop_frequency="10.5GHz",
        sweep_type="Interpolating",
    )
    sweep2 = setup.create_frequency_sweep(name="mysweep2", unit="GHz", start_frequency=1, stop_frequency=4)
    assert sweep2
    sweep2_1 = setup.create_frequency_sweep(name="mysweep2", unit="GHz", start_frequency=1, stop_frequency=4)
    assert sweep2_1
    assert sweep2.name != sweep2_1.name
    assert sweep2.props["RangeEnd"] == "4GHz"
    sweep3 = setup.create_frequency_sweep(unit="GHz", start_frequency=1, stop_frequency=4)
    assert sweep3
    with pytest.raises(AttributeError) as execinfo:
        setup.create_frequency_sweep(
            name="mysweep4", unit="GHz", start_frequency=1, stop_frequency=4, sweep_type="Invalid"
        )
        assert execinfo.args[0] == "Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'"
