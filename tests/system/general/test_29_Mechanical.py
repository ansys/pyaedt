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

import os
import shutil

from ansys.aedt.core import Hfss
from ansys.aedt.core import Icepak
from ansys.aedt.core import Mechanical
from ansys.aedt.core.internal.errors import AEDTRuntimeError
import pytest

from tests.system.general.conftest import config

test_project_name = "coax_Mech"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Mechanical, solution_type="Thermal")
    yield app
    app.close_project(app.project_name)


class TestClass:
    def test_01_save(self, aedtapp, local_scratch):
        test_project = os.path.join(local_scratch.path, test_project_name + ".aedt")
        aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_create_primitive(self, aedtapp, local_scratch):
        udp = aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        o = aedtapp.modeler.create_cylinder(aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        assert isinstance(o.id, int)

    def test_03_assign_convection(self, aedtapp, local_scratch):
        face = aedtapp.modeler["MyCylinder"].faces[0].id
        assert aedtapp.assign_uniform_convection(face, 3)

    def test_04_assign_temperature(self, aedtapp, local_scratch):
        face = aedtapp.modeler["MyCylinder"].faces[1].id
        bound = aedtapp.assign_uniform_temperature(face, "35deg")
        assert bound.props["Temperature"] == "35deg"

    def test_05_assign_load(self, add_app, aedtapp, local_scratch):
        hfss = add_app(application=Hfss)
        udp = aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        hfss.modeler.create_cylinder(aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        setup = hfss.create_setup()
        freq = "1GHz"
        setup.props["Frequency"] = freq
        assert aedtapp.assign_em_losses(hfss.design_name, hfss.setups[0].name, "LastAdaptive", freq)

    def test_06a_create_setup(self, aedtapp):
        assert not aedtapp.assign_2way_coupling()
        mysetup = aedtapp.create_setup()
        mysetup.props["Solver"] = "Direct"
        assert mysetup.update()

    def test_06b_two_way(self, aedtapp):
        assert aedtapp.assign_2way_coupling()

    @pytest.mark.skipif(config["desktopVersion"] < "2021.2", reason="Skipped on versions lower than 2021.2")
    def test_07_assign_thermal_loss(self, add_app, aedtapp):
        ipk = add_app(application=Icepak, solution_type=aedtapp.SOLUTIONS.Icepak.SteadyState)
        udp = aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        ipk.modeler.create_cylinder(ipk.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        ipk.create_setup()
        aedtapp.oproject.InsertDesign("Mechanical", "MechanicalDesign1", "Structural", "")
        aedtapp.set_active_design("MechanicalDesign1")
        aedtapp.create_setup()
        aedtapp.modeler.create_cylinder(aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        assert aedtapp.assign_thermal_map("MyCylinder", ipk.design_name)

    def test_07_assign_mechanical_boundaries(self, aedtapp):
        udp = aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        aedtapp.oproject.InsertDesign("Mechanical", "MechanicalDesign2", "Modal", "")
        aedtapp.set_active_design("MechanicalDesign2")
        aedtapp.modeler.create_cylinder(aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        aedtapp.create_setup()
        assert aedtapp.assign_fixed_support(aedtapp.modeler["MyCylinder"].faces[0].id)
        assert aedtapp.assign_frictionless_support(aedtapp.modeler["MyCylinder"].faces[1].id)
        aedtapp.oproject.InsertDesign("Mechanical", "MechanicalDesign3", "Thermal", "")
        aedtapp.set_active_design("MechanicalDesign3")
        aedtapp.modeler.create_cylinder(aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        with pytest.raises(AEDTRuntimeError, match="This method works only in a Mechanical Structural analysis."):
            aedtapp.assign_fixed_support(aedtapp.modeler["MyCylinder"].faces[0].id)
        with pytest.raises(AEDTRuntimeError, match="This method works only in a Mechanical Structural analysis."):
            aedtapp.assign_frictionless_support(aedtapp.modeler["MyCylinder"].faces[0].id)

    def test_08_mesh_settings(self, aedtapp):
        assert aedtapp.mesh.initial_mesh_settings
        assert aedtapp.mesh.initial_mesh_settings.props

    def test_09_assign_heat_flux(self, aedtapp):
        aedtapp.insert_design("Th1", "Thermal")
        aedtapp.modeler.create_box([0, 0, 0], [10, 10, 3], "box1", "copper")
        b2 = aedtapp.modeler.create_box([20, 20, 2], [10, 10, 3], "box2", "copper")
        hf1 = aedtapp.assign_heat_flux(["box1"], heat_flux_type="Total Power", value="5W")
        hf2 = aedtapp.assign_heat_flux([b2.top_face_x.id], heat_flux_type="Surface Flux", value="25mW_per_m2")
        assert hf1.props["TotalPower"] == "5W"
        assert hf2.props["SurfaceFlux"] == "25mW_per_m2"

    def test_10_assign_heat_generation(self, aedtapp):
        aedtapp.insert_design("Th2", "Thermal")
        aedtapp.modeler.create_box([40, 40, 2], [10, 10, 3], "box3", "copper")
        hg1 = aedtapp.assign_heat_generation(["box3"], value="1W", name="heatgenBC")
        assert hg1.props["TotalPower"] == "1W"

    def test_11_add_mesh_link(self, aedtapp, local_scratch):
        setup = aedtapp.create_setup()
        aedtapp.insert_design("MechanicalDesign2")
        aedtapp.create_setup()
        assert setup.add_mesh_link(design="MechanicalDesign2")
        meshlink_props = setup.props["MeshLink"]
        assert meshlink_props["Project"] == "This Project*"
        assert meshlink_props["PathRelativeTo"] == "TargetProject"
        assert meshlink_props["Design"] == "MechanicalDesign2"
        assert meshlink_props["Soln"] == aedtapp.nominal_adaptive
        assert meshlink_props["Params"] == aedtapp.available_variations.nominal_values
        assert not setup.add_mesh_link(design="")
        assert not setup.add_mesh_link(design="MechanicalDesign2", solution="Setup_Test : LastAdaptive")

        assert setup.add_mesh_link(design="MechanicalDesign2", parameters=aedtapp.available_variations.nominal_values)
        assert setup.add_mesh_link(design="MechanicalDesign2", solution="MySetupAuto : LastAdaptive")
        example_project = os.path.join(local_scratch.path, "test.aedt")
        aedtapp.save_project(example_project)
        example_project_copy = os.path.join(local_scratch.path, "test_copy.aedt")
        shutil.copyfile(example_project, example_project_copy)
        assert setup.add_mesh_link(design="MechanicalDesign2", project=example_project_copy)
        os.remove(example_project_copy)
