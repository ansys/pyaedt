# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
import shutil

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Icepak
from ansys.aedt.core import Mechanical
from ansys.aedt.core.generic.aedt_constants import DesignType
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Mechanical, solution_type="Thermal")
    yield app
    app.close_project(app.project_name, save=False)


def test_save_project(aedt_app, test_tmp_dir):
    test_project = test_tmp_dir / "coax_Mech.aedt"
    aedt_app.save_project(test_project)
    assert Path(test_project).is_file()


def test_create_primitive(aedt_app):
    udp = aedt_app.modeler.Position(0, 0, 0)
    coax_dimension = 30
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
    assert isinstance(o.id, int)


def test_assign_convection(aedt_app):
    aedt_app.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.8, height=20, name="MyCylinder")
    face = aedt_app.modeler["MyCylinder"].faces[0].id
    assert aedt_app.assign_uniform_convection(face, 3)


def test_assign_temperature(aedt_app):
    aedt_app.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.8, height=20, name="MyCylinder")
    face = aedt_app.modeler["MyCylinder"].faces[1].id
    bound = aedt_app.assign_uniform_temperature(face, "35deg")
    assert bound.props["Temperature"] == "35deg"


def test_assign_load(aedt_app, add_app):
    app = add_app(application=Hfss, project=aedt_app.project_name, close_projects=False)

    udp = aedt_app.modeler.Position(0, 0, 0)
    coax_dimension = 30
    app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
    setup = app.create_setup()
    freq = "1GHz"
    setup.props["Frequency"] = freq
    aedt_app.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.8, height=20, name="MyCylinder")
    assert aedt_app.assign_em_losses(app.design_name, app.setups[0].name, "LastAdaptive", freq)


def test_create_setup(aedt_app):
    assert not aedt_app.assign_2way_coupling()
    mysetup = aedt_app.create_setup()
    mysetup.props["Solver"] = "Direct"
    assert mysetup.update()
    assert aedt_app.assign_2way_coupling()


def test_assign_thermal_loss(aedt_app, add_app):
    ipk = add_app(application=Icepak, project=aedt_app.project_name, solution_type="SteadyState", close_projects=False)
    udp = aedt_app.modeler.Position(0, 0, 0)
    coax_dimension = 30
    ipk.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
    ipk.create_setup()
    aedt_app.oproject.InsertDesign(DesignType.ICEPAKFEA.NAME, "MechanicalDesign1", "Structural", "")
    aedt_app.set_active_design("MechanicalDesign1")
    aedt_app.create_setup()
    aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
    assert aedt_app.assign_thermal_map("MyCylinder", ipk.design_name)


def test_assign_mechanical_boundaries(aedt_app):
    udp = aedt_app.modeler.Position(0, 0, 0)
    coax_dimension = 30
    aedt_app.oproject.InsertDesign(DesignType.ICEPAKFEA.NAME, "MechanicalDesign2", "Modal", "")
    aedt_app.set_active_design("MechanicalDesign2")
    aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
    aedt_app.create_setup()
    assert aedt_app.assign_fixed_support(aedt_app.modeler["MyCylinder"].faces[0].id)
    assert aedt_app.assign_frictionless_support(aedt_app.modeler["MyCylinder"].faces[1].id)
    aedt_app.oproject.InsertDesign(DesignType.ICEPAKFEA.NAME, "MechanicalDesign3", "Thermal", "")
    aedt_app.set_active_design("MechanicalDesign3")
    aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
    with pytest.raises(AEDTRuntimeError, match="This method works only in a Mechanical Structural analysis."):
        aedt_app.assign_fixed_support(aedt_app.modeler["MyCylinder"].faces[0].id)
    with pytest.raises(AEDTRuntimeError, match="This method works only in a Mechanical Structural analysis."):
        aedt_app.assign_frictionless_support(aedt_app.modeler["MyCylinder"].faces[0].id)


def test_mesh_settings(aedt_app):
    assert aedt_app.mesh.initial_mesh_settings
    assert aedt_app.mesh.initial_mesh_settings.props


def test_assign_heat_flux(aedt_app):
    aedt_app.insert_design("Th1", "Thermal")
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 3], "box1", "copper")
    b2 = aedt_app.modeler.create_box([20, 20, 2], [10, 10, 3], "box2", "copper")
    hf1 = aedt_app.assign_heat_flux(["box1"], heat_flux_type="Total Power", value="5W")
    hf2 = aedt_app.assign_heat_flux([b2.top_face_x.id], heat_flux_type="Surface Flux", value="25mW_per_m2")
    assert hf1.props["TotalPower"] == "5W"
    assert hf2.props["SurfaceFlux"] == "25mW_per_m2"


def test_assign_heat_generation(aedt_app):
    aedt_app.insert_design("Th2", "Thermal")
    aedt_app.modeler.create_box([40, 40, 2], [10, 10, 3], "box3", "copper")
    hg1 = aedt_app.assign_heat_generation(["box3"], value="1W", name="heatgenBC")
    assert hg1.props["TotalPower"] == "1W"


def test_add_mesh_link(aedt_app, test_tmp_dir):
    setup = aedt_app.create_setup()
    aedt_app.insert_design("MechanicalDesign2")
    aedt_app.create_setup()
    assert setup.add_mesh_link(design="MechanicalDesign2")
    meshlink_props = setup.props["MeshLink"]
    assert meshlink_props["Project"] == "This Project*"
    assert meshlink_props["PathRelativeTo"] == "TargetProject"
    assert meshlink_props["Design"] == "MechanicalDesign2"
    assert meshlink_props["Soln"] == aedt_app.nominal_adaptive
    assert meshlink_props["Params"] == aedt_app.available_variations.nominal_values
    assert not setup.add_mesh_link(design="")
    assert not setup.add_mesh_link(design="MechanicalDesign2", solution="Setup_Test : LastAdaptive")

    assert setup.add_mesh_link(design="MechanicalDesign2", parameters=aedt_app.available_variations.nominal_values)
    assert setup.add_mesh_link(design="MechanicalDesign2", solution="MySetupAuto : LastAdaptive")
    example_project = test_tmp_dir / "test.aedt"
    aedt_app.save_project(example_project)
    example_project_copy = test_tmp_dir / "test_copy.aedt"
    shutil.copyfile(example_project, str(example_project_copy))
    assert setup.add_mesh_link(design="MechanicalDesign2", project=str(example_project_copy))
    aedt_app.close_project(example_project)
    example_project_copy.unlink(missing_ok=True)
