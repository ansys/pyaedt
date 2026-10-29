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

from ansys.aedt.core import TwinBuilder
from ansys.aedt.core.generic.aedt_constants import Setups
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.modules.setup_templates import SetupKeys
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "TSetup"
TEST_TB = "twinbuilder_setup_test"


pytestmark = pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")


@pytest.fixture
def tb_app(add_app):
    app = add_app(application=TwinBuilder)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def tb_setup_app(add_app_example):
    app = add_app_example(application=TwinBuilder, project=TEST_TB, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_twinbuilder_init(tb_setup_app):
    assert len(tb_setup_app.setup_names) == 3

    assert tb_setup_app.setups[0].solver_type == SetupKeys.SetupNames[Setups.TwinbuilderTR]
    assert str(tb_setup_app.setups[0]) == tb_setup_app.setups[0].name
    assert tb_setup_app.setups[0].__repr__() == tb_setup_app.setups[0].name

    assert tb_setup_app.setups[1].solver_type == SetupKeys.SetupNames[Setups.TwinbuilderAC]
    assert str(tb_setup_app.setups[1]) == tb_setup_app.setups[1].name
    assert tb_setup_app.setups[1].__repr__() == tb_setup_app.setups[1].name

    assert tb_setup_app.setups[2].solver_type == SetupKeys.SetupNames[Setups.TwinbuilderDC]
    assert str(tb_setup_app.setups[2]) == tb_setup_app.setups[2].name
    assert tb_setup_app.setups[2].__repr__() == tb_setup_app.setups[2].name


def test_tr(tb_app) -> None:
    initial_setups = len(tb_app.setups)
    setup_name = SetupKeys.SetupNames[Setups.TwinbuilderTR]

    props = {"TransientData": ["40ms", "10us", "1ms", False, ""]}

    setup1 = tb_app.create_setup(props=props, EnableContSolve=True)

    assert setup1.name in tb_app.setup_names
    assert len(tb_app.setups) == 1 + initial_setups
    assert setup1.child_object
    assert not setup1.is_solved
    assert setup1.props["TransientData"] == ["40ms", "10us", "1ms", False, ""]
    assert setup1.props["EnableContSolve"]
    assert setup1.solver_type == setup_name

    setup2 = tb_app.create_setup(name=setup1.name, setup_type=setup_name)
    assert setup2.name in tb_app.setup_names

    # Edit
    setup1["TransientData"] = ["50ms", "10us", "1ms", False, ""]
    assert setup1["TransientData"] == ["50ms", "10us", "1ms", False, ""]

    assert setup1.disable()
    assert not setup1.properties["Enabled"]
    assert setup1.enable()
    assert setup1.properties["Enabled"]

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in tb_app.setup_names
    assert name not in tb_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Delete
    assert tb_app.delete_setup(name=setup1.name)
    assert "new_name" not in tb_app.setup_names
    assert not tb_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in tb_app.setup_names


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025.2")
def test_ac(tb_app) -> None:
    initial_setups = len(tb_app.setups)
    setup_name = SetupKeys.SetupNames[Setups.TwinbuilderAC]

    props = {"LinearFrequencyData": [1, "2Hz", "1kHz", "10Hz"]}

    setup1 = tb_app.create_setup(setup_type=setup_name, props=props, EnableContSolve=True)

    assert setup1.name in tb_app.setup_names
    assert len(tb_app.setups) == 1 + initial_setups
    assert setup1.child_object
    assert not setup1.is_solved
    assert setup1.props["LinearFrequencyData"] == [1, "2Hz", "1kHz", "10Hz"]
    assert setup1.props["EnableContSolve"]
    assert setup1.solver_type == setup_name

    setup2 = tb_app.create_setup(name=setup1.name, setup_type=setup_name)
    assert setup2.name in tb_app.setup_names

    # Edit
    setup1["LinearFrequencyData"] = [1, "2Hz", "1kHz", "100Hz"]
    assert setup1["LinearFrequencyData"] == [1, "2Hz", "1kHz", "100Hz"]

    assert setup1.disable()
    assert not setup1.properties["Enabled"]
    assert setup1.enable()
    assert setup1.properties["Enabled"]

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in tb_app.setup_names
    assert name not in tb_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Delete
    assert tb_app.delete_setup(name=setup1.name)
    assert "new_name" not in tb_app.setup_names
    assert not tb_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in tb_app.setup_names


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025.2")
def test_dc(tb_app) -> None:
    initial_setups = len(tb_app.setups)
    setup_name = SetupKeys.SetupNames[Setups.TwinbuilderDC]

    setup1 = tb_app.create_setup(setup_type=setup_name)

    assert setup1.name in tb_app.setup_names
    assert len(tb_app.setups) == 1 + initial_setups
    assert setup1.child_object
    assert not setup1.is_solved
    assert setup1.solver_type == setup_name

    setup2 = tb_app.create_setup(name=setup1.name, setup_type=setup_name)
    assert setup2.name in tb_app.setup_names

    assert setup1.disable()
    assert not setup1.properties["Enabled"]
    assert setup1.enable()
    assert setup1.properties["Enabled"]

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in tb_app.setup_names
    assert name not in tb_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Delete
    assert tb_app.delete_setup(name=setup1.name)
    assert "new_name" not in tb_app.setup_names
    assert not tb_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in tb_app.setup_names
