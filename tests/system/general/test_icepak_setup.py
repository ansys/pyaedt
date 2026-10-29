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

from pathlib import Path

import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import SetupIcepak
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "TSetup"
TEST_ICEPAK = "icepak_setup_test"


@pytest.fixture
def icepak_app(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def icepak_setup_app(add_app_example):
    app = add_app_example(application=Icepak, project=TEST_ICEPAK, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Skipped on versions earlier than 2023.1")
def test_setup_icepak_init(icepak_setup_app):
    icepak_setup_app.set_active_design("IcepakSteady")
    assert len(icepak_setup_app.setups) == 1
    assert isinstance(icepak_setup_app.setups[0], SetupIcepak)
    assert str(icepak_setup_app.setups[0]) == f"{icepak_setup_app.setups[0].name} : SteadyState"
    assert icepak_setup_app.setups[0].__repr__() == icepak_setup_app.setups[0].name
    assert icepak_setup_app.setups[0].solver_type == "IcepakSteadyState"
    assert icepak_setup_app.setups[0]["Include Temperature"]
    assert icepak_setup_app.setups[0]["Include Flow"]

    icepak_setup_app.set_active_design("IcepakSteadyFlow")
    assert len(icepak_setup_app.setups) == 1
    assert isinstance(icepak_setup_app.setups[0], SetupIcepak)
    assert str(icepak_setup_app.setups[0]) == f"{icepak_setup_app.setups[0].name} : SteadyState"
    assert icepak_setup_app.setups[0].__repr__() == icepak_setup_app.setups[0].name
    assert icepak_setup_app.setups[0].solver_type == "IcepakSteadyState"
    assert "Include Temperature" in icepak_setup_app.setups[0].props
    assert "Include Flow" not in icepak_setup_app.setups[0].props

    icepak_setup_app.set_active_design("IcepakTransient")
    assert len(icepak_setup_app.setups) == 1
    assert isinstance(icepak_setup_app.setups[0], SetupIcepak)
    assert str(icepak_setup_app.setups[0]) == f"{icepak_setup_app.setups[0].name} : Transient"
    assert icepak_setup_app.setups[0].__repr__() == icepak_setup_app.setups[0].name
    assert icepak_setup_app.setups[0].solver_type == "IcepakTransient"
    assert "Include Temperature" in icepak_setup_app.setups[0].props
    assert "Include Flow" in icepak_setup_app.setups[0].props


def test_setup_icepak(icepak_app) -> None:
    props = {"Include Flow": False}

    setup1 = icepak_app.create_setup(setup_type="SteadyTemperatureOnly", props=props)

    assert setup1.name == "MySetupAuto"
    assert icepak_app.setups[0].name == setup1.name
    assert setup1.name in icepak_app.setup_names
    assert isinstance(setup1, SetupIcepak)
    assert len(icepak_app.setup_names) == 1
    assert setup1.solver_type == "IcepakSteadyState"
    assert setup1["Flow Regime"] == "Laminar"
    assert not setup1["Include Flow"]

    # Properties
    setup2 = icepak_app.create_setup()
    assert setup2.name in icepak_app.setup_names
    assert len(icepak_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in icepak_app.setup_names
    assert name not in icepak_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Edit
    setup1["Include Flow"] = True
    assert setup1["Include Flow"]

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert icepak_app.delete_setup(name=setup1.name)
    assert "new_name" not in icepak_app.setup_names
    assert not icepak_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in icepak_app.setup_names


def test_setup_transient(icepak_app) -> None:
    icepak_app.solution_type = "Transient"
    props = {"Include Flow": False}

    setup1 = icepak_app.create_setup(setup_type="TransientTemperatureOnly", props=props)

    assert setup1.name == "MySetupAuto"
    assert icepak_app.setups[0].name == setup1.name
    assert setup1.name in icepak_app.setup_names
    assert isinstance(setup1, SetupIcepak)
    assert len(icepak_app.setup_names) == 1
    assert setup1.solver_type == "IcepakTransient"
    assert setup1["Flow Regime"] == "Laminar"
    assert not setup1["Include Flow"]

    # Properties
    setup2 = icepak_app.create_setup()
    assert setup2.name in icepak_app.setup_names
    assert len(icepak_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in icepak_app.setup_names
    assert name not in icepak_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Edit
    setup1["Include Flow"] = True
    assert setup1["Include Flow"]

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert icepak_app.delete_setup(name=setup1.name)
    assert "new_name" not in icepak_app.setup_names
    assert not icepak_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in icepak_app.setup_names


def test_icepak_setup_templates(icepak_app) -> None:
    setup = icepak_app.create_setup(setup_type="SteadyTemperatureOnly")
    templates = SetupKeys().get_default_icepak_template(default_type="Natural Convection")
    assert templates
    assert setup["Include Temperature"]
    setup.props = templates["IcepakSteadyState"]
    assert not setup["Include Temperature"]

    assert SetupKeys().get_default_icepak_template(default_type="Default")
    assert SetupKeys().get_default_icepak_template(default_type="Forced Convection")

    with pytest.raises(AttributeError):
        SetupKeys().get_default_icepak_template(default_type="Default Convection")


def test_restart_solution(icepak_app, tmp_path) -> None:
    icepak_app["a"] = "1mm"
    icepak_app["b"] = "2mm"
    setup = icepak_app.create_setup()
    solution = str(setup)

    # By-name mapping takes precedence over explicitly passed values.
    assert setup.start_continue_from_previous_setup(
        design=icepak_app.design_name, solution=solution, parameters={"a": "9mm"}
    )
    restart = setup.props["RestartSoln"]
    assert restart["Project"] == "This Project*"
    assert restart["Design"] == icepak_app.design_name
    assert restart["Soln"] == solution
    assert restart["Params"] == {"a": "a", "b": "b"}
    assert restart["ForceSourceToSolve"]
    assert restart["PreservePartnerSoln"]
    assert not setup.props["Frozen Flow Simulation"]

    # Without by-name mapping, omitted parameters use the current nominal values.
    assert setup.start_continue_from_previous_setup(
        design=icepak_app.design_name, solution=solution, map_variables_by_name=False
    )
    assert setup.props["RestartSoln"]["Params"]

    # Explicit parameter values and all restart flags are configurable.
    assert setup.start_continue_from_previous_setup(
        design=icepak_app.design_name,
        solution=solution,
        map_variables_by_name=False,
        parameters={"a": "3mm", "b": "4mm"},
        force_source_to_solve=False,
        preserve_partner_solution=False,
        frozen_flow=True,
    )
    restart = setup.props["RestartSoln"]
    assert restart["Params"] == {"a": "3mm", "b": "4mm"}
    assert not restart["ForceSourceToSolve"]
    assert not restart["PreservePartnerSoln"]
    assert setup.props["Frozen Flow Simulation"]

    # An existing project path is accepted and switches the relative path mode.
    icepak_app.save_project()
    project_path = Path(icepak_app.project_file)
    assert project_path.exists()
    assert setup.start_continue_from_previous_setup(
        design=icepak_app.design_name, solution=solution, project=project_path
    )
    assert setup.props["RestartSoln"]["Project"] == str(project_path)

    with pytest.raises(ValueError, match="Project file path provided does not exist"):
        setup.start_continue_from_previous_setup(
            design=icepak_app.design_name, solution=solution, project=tmp_path / "missing.aedt"
        )
    with pytest.raises(ValueError, match="Design does not exist"):
        setup.start_continue_from_previous_setup(design="MissingDesign", solution=solution)
    with pytest.raises(ValueError, match="Provide design name"):
        setup.start_continue_from_previous_setup(design="", solution=solution)
    with pytest.raises(ValueError, match="Provide design name"):
        setup.start_continue_from_previous_setup(design=None, solution=solution)
    with pytest.raises(ValueError, match="Provide a valid solution"):
        setup.start_continue_from_previous_setup(design=icepak_app.design_name, solution="")
    with pytest.raises(ValueError, match="Provide a valid solution"):
        setup.start_continue_from_previous_setup(design=icepak_app.design_name, solution=None)
