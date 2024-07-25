# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

import os

import pytest

from pyaedt import Rmxprt
from pyaedt.generic.general_methods import is_linux

test_project_name = "motor"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(application=Rmxprt)
    return app


@pytest.mark.skipif(is_linux, reason="Emit API fails on linux.")
class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_01_save(self):
        test_project = os.path.join(self.local_scratch.path, test_project_name + ".aedt")
        self.aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_changeesolution(self):
        assert self.aedtapp.disable_modelcreation("ORIM")
        assert self.aedtapp.disable_modelcreation("AFIM")
        assert self.aedtapp.disable_modelcreation("HM")
        assert self.aedtapp.disable_modelcreation("LSSM")
        assert self.aedtapp.disable_modelcreation("UNIM")
        assert self.aedtapp.disable_modelcreation("LSSM")
        assert self.aedtapp.enable_modelcreation("WRIM")

    def test_03_getchangeproperty(self):
        # test increment statorOD by 1mm
        self.aedtapp.disable_modelcreation("ASSM")
        statorOD = self.aedtapp.stator["Outer Diameter"]
        assert statorOD
        self.aedtapp.stator["Outer Diameter"] = statorOD + "+1mm"

    def test_04_create_setup(self):
        # first test GRM (use Inner-Rotor Induction Machine)
        assert self.aedtapp.enable_modelcreation("IRIM")
        mysetup = self.aedtapp.create_setup()
        assert mysetup.props["RatedOutputPower"]
        mysetup.props["RatedOutputPower"] = "100W"
        assert mysetup.update()  # update only needed for assertion
        # second test ASSM setup
        self.aedtapp.delete_setup(mysetup.name)
        assert self.aedtapp.disable_modelcreation("ASSM")
        mysetup = self.aedtapp.create_setup()
        assert mysetup.props["RatedSpeed"]
        mysetup.props["RatedSpeed"] = "3600rpm"
        assert mysetup.update()  # update only needed for assertion
        # third test TPSM/SYNM setup
        self.aedtapp.delete_setup(mysetup.name)
        assert self.aedtapp.disable_modelcreation("TPSM")
        mysetup = self.aedtapp.create_setup()
        assert mysetup.props["RatedVoltage"]
        mysetup.props["RatedVoltage"] = "208V"
        assert mysetup.update()  # update only needed for assertion

    def test_05_set_material_threshold(self):
        assert self.aedtapp.set_material_threshold()
        conductivity = 123123123
        permeability = 3
        assert self.aedtapp.set_material_threshold(conductivity, permeability)
        assert self.aedtapp.set_material_threshold(str(conductivity), str(permeability))
        assert not self.aedtapp.set_material_threshold("e", str(permeability))
        assert not self.aedtapp.set_material_threshold(conductivity, "p")

    def test_06_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_07_export_to_maxwell(self, add_app):
        app = add_app("assm_test", application=Rmxprt, subfolder="T32")
        app.analyze(cores=1)
        m2d = app.create_maxwell_design("Setup1")
        assert m2d.design_type == "Maxwell 2D"
        m3d = app.create_maxwell_design("Setup1", maxwell_2d=False)
        assert m3d.design_type == "Maxwell 3D"
        config = app.export_configuration(os.path.join(self.local_scratch.path, "assm.json"))
        app2 = add_app("assm_test2", application=Rmxprt)
        app2.import_configuration(config)
        assert app2.circuit
