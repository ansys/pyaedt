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

from ansys.aedt.core import Mechanical
from ansys.aedt.core.modules.solve_setup import SetupIcepakFEA
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "TSetup"
TEST_MECHANICAL = "mechanical_setup_test"


@pytest.fixture
def mechanical_app(add_app):
    app = add_app(application=Mechanical)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def mechanical_setup_app(add_app_example):
    app = add_app_example(application=Mechanical, project=TEST_MECHANICAL, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_setup_mechanical_init(mechanical_setup_app):
    mechanical_setup_app.set_active_design("IcepakFEAModal")
    assert len(mechanical_setup_app.setups) == 1
    assert isinstance(mechanical_setup_app.setups[0], SetupIcepakFEA)
    assert str(mechanical_setup_app.setups[0]) == mechanical_setup_app.setups[0].name
    assert mechanical_setup_app.setups[0].__repr__() == mechanical_setup_app.setups[0].name
    assert mechanical_setup_app.setups[0].solver_type == "MechModal"
    assert mechanical_setup_app.setups[0]["Max Modes"]

    mechanical_setup_app.set_active_design("IcepakFEASteadyThermal")
    assert len(mechanical_setup_app.setups) == 1
    assert isinstance(mechanical_setup_app.setups[0], SetupIcepakFEA)
    assert str(mechanical_setup_app.setups[0]) == f"{mechanical_setup_app.setups[0].name} : Solution"
    assert mechanical_setup_app.setups[0].__repr__() == mechanical_setup_app.setups[0].name
    assert mechanical_setup_app.setups[0].solver_type == "MechSteadyStateThermal"
    assert "HeatConvergenceMinRef" in mechanical_setup_app.setups[0].props

    mechanical_setup_app.set_active_design("IcepakFEAStructural")
    assert len(mechanical_setup_app.setups) == 1
    assert isinstance(mechanical_setup_app.setups[0], SetupIcepakFEA)
    assert str(mechanical_setup_app.setups[0]) == f"{mechanical_setup_app.setups[0].name} : Solution"
    assert mechanical_setup_app.setups[0].__repr__() == mechanical_setup_app.setups[0].name
    assert mechanical_setup_app.setups[0].solver_type == "MechStructural"
    assert "Solver" in mechanical_setup_app.setups[0].props

    mechanical_setup_app.set_active_design("IcepakFEATransientThermal")
    assert len(mechanical_setup_app.setups) == 1
    assert isinstance(mechanical_setup_app.setups[0], SetupIcepakFEA)
    assert str(mechanical_setup_app.setups[0]) == f"{mechanical_setup_app.setups[0].name} : Solution"
    assert mechanical_setup_app.setups[0].__repr__() == mechanical_setup_app.setups[0].name
    assert mechanical_setup_app.setups[0].solver_type == "MechTransientThermal"
    assert "Start Time" in mechanical_setup_app.setups[0].props


def test_setup_modal(mechanical_app) -> None:
    mechanical_app.solution_type = "Modal"

    props = {"Limit Search": False}

    setup1 = mechanical_app.create_setup(props=props)

    assert setup1.name == "MySetupAuto"
    assert mechanical_app.setups[0].name == setup1.name
    assert setup1.name in mechanical_app.setup_names
    assert isinstance(setup1, SetupIcepakFEA)
    assert len(mechanical_app.setup_names) == 1
    assert setup1.solver_type == "MechModal"
    assert not setup1["Limit Search"]

    # Properties
    setup2 = mechanical_app.create_setup(name=setup1.name)
    assert setup2.name in mechanical_app.setup_names
    assert len(mechanical_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in mechanical_app.setup_names
    assert name not in mechanical_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Edit
    setup1["Limit Search"] = True
    assert setup1["Limit Search"]

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert mechanical_app.delete_setup(name=setup1.name)
    assert "new_name" not in mechanical_app.setup_names
    assert not mechanical_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in mechanical_app.setup_names


def test_setup_thermal(mechanical_app) -> None:
    mechanical_app.solution_type = "Thermal"

    setup1 = mechanical_app.create_setup()

    assert setup1.name == "MySetupAuto"
    assert mechanical_app.setups[0].name == setup1.name
    assert setup1.name in mechanical_app.setup_names
    assert isinstance(setup1, SetupIcepakFEA)
    assert len(mechanical_app.setup_names) == 1
    assert setup1.solver_type == "MechSteadyStateThermal"

    setup2 = mechanical_app.create_setup(name=setup1.name)
    assert setup2.name in mechanical_app.setup_names
    assert len(mechanical_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in mechanical_app.setup_names
    assert name not in mechanical_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert mechanical_app.delete_setup(name=setup1.name)
    assert "new_name" not in mechanical_app.setup_names
    assert not mechanical_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in mechanical_app.setup_names


def test_setup_transient_thermal(mechanical_app) -> None:
    mechanical_app.solution_type = "Transient Thermal"

    props = {"Start Time": "0.1s"}

    setup1 = mechanical_app.create_setup(props=props)

    assert setup1.name == "MySetupAuto"
    assert mechanical_app.setups[0].name == setup1.name
    assert setup1.name in mechanical_app.setup_names
    assert isinstance(setup1, SetupIcepakFEA)
    assert len(mechanical_app.setup_names) == 1
    assert setup1.solver_type == "MechTransientThermal"
    assert setup1["Start Time"] == "0.1s"

    # Properties
    setup2 = mechanical_app.create_setup(name=setup1.name)
    assert setup2.name in mechanical_app.setup_names
    assert len(mechanical_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in mechanical_app.setup_names
    assert name not in mechanical_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Edit
    setup1["Start Time"] = "0.2s"
    assert setup1["Start Time"] == "0.2s"

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert mechanical_app.delete_setup(name=setup1.name)
    assert "new_name" not in mechanical_app.setup_names
    assert not mechanical_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in mechanical_app.setup_names


def test_setup_structural(mechanical_app) -> None:
    mechanical_app.solution_type = "Structural"

    setup1 = mechanical_app.create_setup()

    assert setup1.name == "MySetupAuto"
    assert mechanical_app.setups[0].name == setup1.name
    assert setup1.name in mechanical_app.setup_names
    assert isinstance(setup1, SetupIcepakFEA)
    assert len(mechanical_app.setup_names) == 1
    assert setup1.solver_type == "MechStructural"

    setup2 = mechanical_app.create_setup(name=setup1.name)
    assert setup2.name in mechanical_app.setup_names
    assert len(mechanical_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in mechanical_app.setup_names
    assert name not in mechanical_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert mechanical_app.delete_setup(name=setup1.name)
    assert "new_name" not in mechanical_app.setup_names
    assert not mechanical_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in mechanical_app.setup_names
