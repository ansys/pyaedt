# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.aedt.core import Rmxprt
from ansys.aedt.core.generic.general_methods import is_linux

test_project_name = "motor"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Rmxprt)
    yield app
    app.close_project(app.project_name)


@pytest.mark.skipif(is_linux, reason="Emit API fails on linux.")
def test_save(aedtapp, local_scratch):
    test_project = Path(local_scratch.path) / f"{test_project_name}.aedt"
    aedtapp.save_project(test_project)
    assert test_project.exists()


def test_changeesolution(aedtapp):
    assert aedtapp.disable_modelcreation("ORIM")
    assert aedtapp.disable_modelcreation("AFIM")
    assert aedtapp.disable_modelcreation("HM")
    assert aedtapp.disable_modelcreation("LSSM")
    assert aedtapp.disable_modelcreation("UNIM")
    assert aedtapp.disable_modelcreation("LSSM")
    assert aedtapp.enable_modelcreation("WRIM")


def test_getchangeproperty(aedtapp):
    # test increment statorOD by 1mm
    aedtapp.disable_modelcreation("ASSM")
    statorOD = aedtapp.stator["Outer Diameter"]
    assert statorOD
    aedtapp.stator["Outer Diameter"] = statorOD + "+1mm"


def test_create_setup(aedtapp):
    # first test GRM (use Inner-Rotor Induction Machine)
    assert aedtapp.enable_modelcreation("IRIM")
    mysetup = aedtapp.create_setup()
    assert mysetup.props["RatedOutputPower"]
    mysetup.props["RatedOutputPower"] = "100W"
    assert mysetup.update()  # update only needed for assertion
    # second test ASSM setup
    aedtapp.delete_setup(mysetup.name)
    assert aedtapp.disable_modelcreation("ASSM")
    mysetup = aedtapp.create_setup()
    assert mysetup.props["RatedSpeed"]
    mysetup.props["RatedSpeed"] = "3600rpm"
    assert mysetup.update()  # update only needed for assertion
    # third test TPSM/SYNM setup
    aedtapp.delete_setup(mysetup.name)
    assert aedtapp.disable_modelcreation("TPSM")
    mysetup = aedtapp.create_setup()
    assert mysetup.props["RatedVoltage"]
    mysetup.props["RatedVoltage"] = "208V"
    assert mysetup.update()  # update only needed for assertion


def test_set_material_threshold(aedtapp):
    assert aedtapp.set_material_threshold()
    conductivity = 123123123
    permeability = 3
    assert aedtapp.set_material_threshold(conductivity, permeability)
    assert aedtapp.set_material_threshold(str(conductivity), str(permeability))
    assert not aedtapp.set_material_threshold("e", str(permeability))
    assert not aedtapp.set_material_threshold(conductivity, "p")


def test_set_variable(aedtapp):
    aedtapp.variable_manager.set_variable("var_test", expression="123")
    aedtapp["var_test"] = "234"
    assert "var_test" in aedtapp.variable_manager.design_variable_names
    assert aedtapp.variable_manager.design_variables["var_test"].expression == "234"
