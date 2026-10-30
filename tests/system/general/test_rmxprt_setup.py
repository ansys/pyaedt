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

from ansys.aedt.core import Rmxprt
from ansys.aedt.core.generic.aedt_constants import RmxprtConstants
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import SetupRmxprt
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "TSetup"
TEST_RMXPRT = "rmxprt_setup_test"


@pytest.fixture
def rmxprt_app(add_app):
    app = add_app(application=Rmxprt)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def rmxprt_setup_app(add_app_example):
    app = add_app_example(application=Rmxprt, project=TEST_RMXPRT, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
@pytest.mark.parametrize(
    "design_name",
    [
        "ASSM",
        "BLDC",
        "CPSM",
        "DCM",
        "IBDM",
        "IRIM",
        "LSSM",
        "NSSM",
        "PIM",
        "PMDC",
        "SPIM",
        "SRM",
        "SYNM",
        "UNIM",
    ],
)
def test_setup_rmxprt_init(rmxprt_setup_app, design_name) -> None:
    rmxprt_setup_app.set_active_design(design_name)
    assert len(rmxprt_setup_app.setups) == 1
    setup = rmxprt_setup_app.setups[0]
    assert isinstance(setup, SetupRmxprt)
    assert str(setup) == setup.name
    assert repr(setup) == setup.name
    assert setup.solver_type == rmxprt_setup_app.solution_type


@pytest.mark.parametrize(
    ("solution_type", "model_creation", "property_name", "property_value", "edit_value", "extra_kwargs"),
    [
        ("IRIM", True, "RatedPowerFactor", "0.9", "0.95", {"Frequency": "70Hz"}),
        ("ASSM", False, "RatedSpeed", "3600rpm", "3000rpm", {}),
        ("TPSM", False, "RatedVoltage", "208V", "220V", {}),
    ],
    ids=("irim", "assm", "tpsm"),
)
def test_setup_rmxprt(
    rmxprt_app, solution_type, model_creation, property_name, property_value, edit_value, extra_kwargs
) -> None:
    if model_creation:
        assert rmxprt_app.enable_modelcreation(solution_type)
    else:
        assert rmxprt_app.disable_modelcreation(solution_type)

    setup_type = RmxprtConstants.solution_types[solution_type]["default_setup"]
    setup_template = SetupKeys.get_setup_templates()[setup_type]
    assert property_name in setup_template
    template_value = setup_template[property_name]
    props = {property_name: property_value}
    setup1 = rmxprt_app.create_setup(props=props, **extra_kwargs)

    assert setup_template[property_name] == template_value
    assert setup1.name == "MySetupAuto"
    assert rmxprt_app.setups[0].name == setup1.name
    assert setup1.name in rmxprt_app.setup_names
    assert isinstance(setup1, SetupRmxprt)
    assert len(rmxprt_app.setup_names) == 1
    assert setup1.solver_type == rmxprt_app.solution_type
    assert setup1[property_name] == property_value
    for key, value in extra_kwargs.items():
        assert setup1[key] == value

    # Properties
    setup2 = rmxprt_app.create_setup(name=setup1.name)
    assert setup2.name in rmxprt_app.setup_names
    assert len(rmxprt_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in rmxprt_app.setup_names
    assert name not in rmxprt_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Edit
    setup1[property_name] = edit_value
    assert setup1[property_name] == edit_value

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert rmxprt_app.delete_setup(name=setup1.name)
    assert "new_name" not in rmxprt_app.setup_names
    assert not rmxprt_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in rmxprt_app.setup_names
