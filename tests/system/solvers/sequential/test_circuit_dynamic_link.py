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
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core.modeler.circuits.object_3d_circuit import CircuitComponent
from tests import TESTS_SOLVERS_PATH

TEST_SUBFOLDER = "circuit_dynamic_link"
TEST_PROJECT_NAME = "Dynamic_Link"
SRC_USB = "uUSB"

SRC_PROJECT_NAME = "USB_Connector_231"
LINKED_PROJECT_NAME = "Filter_Board_231"

LAYOUT_DESIGN_NAME = "layout_cutout"
Q2D_Q3D_NAME = "q2d_q3d"

Q3D_SOLVED = "Q3d_solved"


@pytest.fixture
def q3d_solved(add_app_example):
    app = add_app_example(project=Q3D_SOLVED, subfolder=TESTS_SOLVERS_PATH / "example_models" / "T31", application=Q3d)
    yield app
    app.close_project(save=False)


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Circuit)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def usb_app(add_app_example):
    app = add_app_example(project=SRC_PROJECT_NAME, application=Hfss, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def circuit_app(add_app_example):
    app = add_app_example(project=TEST_PROJECT_NAME, application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def q3d_app(add_app_example):
    app = add_app_example(project=Q2D_Q3D_NAME, application=Q3d, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def q2d_app(add_app_example):
    app = add_app_example(project=Q2D_Q3D_NAME, application=Q2d, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def test_q3d_rlgc_link_design_name(q3d_solved, add_app):
    cir = add_app(application=Circuit, project=q3d_solved.project_name, close_projects=False)

    with pytest.raises(ValueError):
        cir.modeler.schematic.add_q3d_rlgc("dummy", solution_name="dummy")

    with pytest.raises(ValueError):
        cir.modeler.schematic.add_q3d_rlgc(q3d_solved.design_name)

    q3d_comp = cir.modeler.schematic.add_q3d_rlgc(q3d_solved.design_name, solution_name="Setup1 : LastAdaptive")
    assert isinstance(q3d_comp, CircuitComponent)
    assert len(q3d_comp.pins) == 6
