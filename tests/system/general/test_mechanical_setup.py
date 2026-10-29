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

from ansys.aedt.core import Mechanical
from ansys.aedt.core.modules.setup_templates import SetupKeys
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


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Skipped on versions earlier than 2023.1")
def test_setup_mechanical_init(mechanical_setup_app):
    mechanical_setup_app.set_active_design("IcepakSteady")
    assert len(mechanical_setup_app.setups) == 1
    assert isinstance(mechanical_setup_app.setups[0], SetupIcepakFEA)
    assert str(mechanical_setup_app.setups[0]) == f"{mechanical_setup_app.setups[0].name} : SteadyState"
    assert mechanical_setup_app.setups[0].__repr__() == mechanical_setup_app.setups[0].name
    assert mechanical_setup_app.setups[0].solver_type == "IcepakSteadyState"
    assert mechanical_setup_app.setups[0]["Include Temperature"]
    assert mechanical_setup_app.setups[0]["Include Flow"]

    mechanical_setup_app.set_active_design("IcepakSteadyFlow")
    assert len(mechanical_setup_app.setups) == 1
    assert isinstance(mechanical_setup_app.setups[0], SetupIcepakFEA)
    assert str(mechanical_setup_app.setups[0]) == f"{mechanical_setup_app.setups[0].name} : SteadyState"
    assert mechanical_setup_app.setups[0].__repr__() == mechanical_setup_app.setups[0].name
    assert mechanical_setup_app.setups[0].solver_type == "IcepakSteadyState"
    assert "Include Temperature" in mechanical_setup_app.setups[0].props
    assert "Include Flow" not in mechanical_setup_app.setups[0].props

    mechanical_setup_app.set_active_design("IcepakTransient")
    assert len(mechanical_setup_app.setups) == 1
    assert isinstance(mechanical_setup_app.setups[0], SetupIcepakFEA)
    assert str(mechanical_setup_app.setups[0]) == f"{mechanical_setup_app.setups[0].name} : Transient"
    assert mechanical_setup_app.setups[0].__repr__() == mechanical_setup_app.setups[0].name
    assert mechanical_setup_app.setups[0].solver_type == "IcepakTransient"
    assert "Include Temperature" in mechanical_setup_app.setups[0].props
    assert "Include Flow" in mechanical_setup_app.setups[0].props


def test_setup_icepak(mechanical_app) -> None:
    props = {"Include Flow": False}

    setup1 = mechanical_app.create_setup(setup_type="SteadyTemperatureOnly", props=props)

    assert setup1.name == "MySetupAuto"
    assert mechanical_app.setups[0].name == setup1.name
    assert setup1.name in mechanical_app.setup_names
    assert isinstance(setup1, SetupIcepakFEA)
    assert len(mechanical_app.setup_names) == 1
    assert setup1.solver_type == "IcepakSteadyState"
    assert setup1["Flow Regime"] == "Laminar"
    assert not setup1["Include Flow"]

    # Properties
    setup2 = mechanical_app.create_setup()
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
    setup1["Include Flow"] = True
    assert setup1["Include Flow"]

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


def test_icepak_setup_templates(mechanical_app) -> None:
    setup = mechanical_app.create_setup(setup_type="SteadyTemperatureOnly")
    templates = SetupKeys().get_default_icepak_template(default_type="Natural Convection")
    assert templates
    assert setup["Include Temperature"]
    setup.props = templates["IcepakSteadyState"]
    assert not setup["Include Temperature"]

    assert SetupKeys().get_default_icepak_template(default_type="Default")
    assert SetupKeys().get_default_icepak_template(default_type="Forced Convection")

    with pytest.raises(AttributeError):
        SetupKeys().get_default_icepak_template(default_type="Default Convection")


def test_restart_solution(mechanical_app, tmp_path) -> None:
    mechanical_app["a"] = "1mm"
    mechanical_app["b"] = "2mm"
    setup = mechanical_app.create_setup()
    solution = str(setup)

    # By-name mapping takes precedence over explicitly passed values.
    assert setup.start_continue_from_previous_setup(
        design=mechanical_app.design_name, solution=solution, parameters={"a": "9mm"}
    )
    restart = setup.props["RestartSoln"]
    assert restart["Project"] == "This Project*"
    assert restart["Design"] == mechanical_app.design_name
    assert restart["Soln"] == solution
    assert restart["Params"] == {"a": "a", "b": "b"}
    assert restart["ForceSourceToSolve"]
    assert restart["PreservePartnerSoln"]
    assert not setup.props["Frozen Flow Simulation"]

    # Without by-name mapping, omitted parameters use the current nominal values.
    assert setup.start_continue_from_previous_setup(
        design=mechanical_app.design_name, solution=solution, map_variables_by_name=False
    )
    assert setup.props["RestartSoln"]["Params"]

    # Explicit parameter values and all restart flags are configurable.
    assert setup.start_continue_from_previous_setup(
        design=mechanical_app.design_name,
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
    mechanical_app.save_project()
    project_path = Path(mechanical_app.project_file)
    assert project_path.exists()
    assert setup.start_continue_from_previous_setup(
        design=mechanical_app.design_name, solution=solution, project=project_path
    )
    assert setup.props["RestartSoln"]["Project"] == str(project_path)

    with pytest.raises(ValueError, match="Project file path provided does not exist"):
        setup.start_continue_from_previous_setup(
            design=mechanical_app.design_name, solution=solution, project=tmp_path / "missing.aedt"
        )
    with pytest.raises(ValueError, match="Design does not exist"):
        setup.start_continue_from_previous_setup(design="MissingDesign", solution=solution)
    with pytest.raises(ValueError, match="Provide design name"):
        setup.start_continue_from_previous_setup(design="", solution=solution)
    with pytest.raises(ValueError, match="Provide design name"):
        setup.start_continue_from_previous_setup(design=None, solution=solution)
    with pytest.raises(ValueError, match="Provide a valid solution"):
        setup.start_continue_from_previous_setup(design=mechanical_app.design_name, solution="")
    with pytest.raises(ValueError, match="Provide a valid solution"):
        setup.start_continue_from_previous_setup(design=mechanical_app.design_name, solution=None)
