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

from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.hfss import Hfss
from tests.conftest import DESKTOP_VERSION
from tests.conftest import USE_GRPC


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def maxwell_app(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name, save=False)


def test_assign_model_resolution(aedt_app) -> None:
    # Initialize the modeler and create a cylinder for testing
    udp = aedt_app.modeler.Position(0, 0, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "inner")
    o2 = aedt_app.modeler.create_cylinder(Plane.XY, [10, 10, 20], 3, coax_dimension, 0, "cyl2")
    mesh_object = aedt_app.get_oo_object(aedt_app.odesign, "Mesh")

    # Assign a model resolution to the cylinder and verify its properties
    mr1 = aedt_app.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
    assert mr1.name in aedt_app.get_oo_name(mesh_object)
    mr1.name = "resolution_test"
    assert "resolution_test" in aedt_app.mesh.meshoperations[0].name
    assert "resolution_test" in aedt_app.get_oo_name(mesh_object)
    if mr1.assignment:
        assert mr1.assignment == [o.name]

    # Try to set existing name and verify that it fails
    mr2 = aedt_app.mesh.assign_model_resolution(o, 1e-5, "resolution_test")
    assert mr2.name != "resolution_test"
    with pytest.raises(ValueError):
        mr2.name = "resolution_test"

    # Setting properties and verifying them
    # Single property assignment
    mr1.props["UseAutoLength"] = True
    assert aedt_app.get_oo_property_value(mesh_object, mr1.name, "Use Auto Simplify")

    # If AutoEnable is set to True, DefeatureLength should not be settable. So we set it to False first.
    if "DefeatureLength" in mr1.props:
        mr1.props["DefeatureLength"] = "0.1mm"
        assert aedt_app.get_oo_property_value(mesh_object, mr1.name, "Model Resolution Length") != "0.1mm"

    # Multiple property assignment
    new_props = dict(mr1.props)
    new_props["UseAutoLength"] = False
    new_props["DefeatureLength"] = "0.2mm"
    mr1.props = new_props
    assert aedt_app.get_oo_property_value(mesh_object, mr1.name, "Model Resolution Length") == "0.2mm"
    assert not aedt_app.get_oo_property_value(mesh_object, mr1.name, "Use Auto Simplify")

    # Enable AutoLength
    mr1.props["UseAutoLength"] = True
    assert aedt_app.get_oo_property_value(mesh_object, mr1.name, "Use Auto Simplify")

    # Reassigning the model resolution to a different object and verifying the assignment
    mr1.props["Objects"] = [o2.name, o]
    assert len(mr1.props["Objects"]) == 2
    if mr1.assignment:
        assert len(mr1.assignment) == 2

    new_props = dict(mr1.props)
    new_props["Objects"] = [o2]
    mr1.update_assignment(new_props)
    assert len(mr1.props["Objects"]) == 1
    if mr1.assignment:
        assert len(mr1.assignment) == 1


def test_assign_surface_mesh(aedt_app) -> None:
    udp = aedt_app.modeler.Position(10, 10, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface")
    surface = aedt_app.mesh.assign_surface_mesh(o.id, 3, "Surface")
    assert "Surface" in [i.name for i in aedt_app.mesh.meshoperations]
    assert surface.props["SliderMeshSettings"] == 3


def test_assign_surface_mesh_manual(aedt_app) -> None:
    udp = aedt_app.modeler.Position(20, 20, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface_manual")
    surface = aedt_app.mesh.assign_surface_mesh_manual(o.id, 1e-6, aspect_ratio=3, name="Surface_Manual")
    assert "Surface_Manual" in [i.name for i in aedt_app.mesh.meshoperations]
    assert float(surface.props["SurfDev"]) == 1e-6

    surface.props["SurfDev"] = 1e-05
    assert aedt_app.mesh.meshoperations[0].properties["Surface Deviation"] in ["1e-05", 1e-05]

    surface.props["NormalDevChoice"] = 2
    surface.props["NormalDev"] = "10deg"
    assert aedt_app.mesh.meshoperations[0].properties["Normal Deviation"] == "10deg"

    surface.props["AspectRatioChoice"] = 2
    surface.props["AspectRatio"] = 20
    assert aedt_app.mesh.meshoperations[0].properties["Aspect Ratio"] in [20, "20"]

    if DESKTOP_VERSION >= "2026.1":
        # Switch off the manual surface mesh and check if the default values are applied
        surface.props["NormalDevChoice"] = 0
        assert "NormalDev" not in surface.props

    cylinder_zx = aedt_app.modeler.create_cylinder(Plane.ZX, udp, 3, coax_dimension, 0, "surface_manual")
    surface_default_value = aedt_app.mesh.assign_surface_mesh_manual(cylinder_zx.id)
    assert surface_default_value.name in [i.name for i in aedt_app.mesh.meshoperations]
    assert surface_default_value.props["SurfDevChoice"] == 0


def test_assign_surface_priority(aedt_app):
    box = aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    rect = aedt_app.modeler.create_rectangle(Plane.XY, [0, 0, 10], [10, 10])

    surface = aedt_app.mesh.assign_surf_priority_for_tau([box.name, rect.name], 1)
    assert surface.props["SurfaceRepPriority"] == 1
    surface.props["SurfaceRepPriority"] = 0
    assert (
        aedt_app.odesign.GetChildObject("Mesh")
        .GetChildObject(surface.name)
        .GetPropValue("Surface Representation Priority for TAU")
        == "Normal"
    )

    surface.props["SurfaceRepPriority"] = 1
    assert (
        aedt_app.odesign.GetChildObject("Mesh")
        .GetChildObject(surface.name)
        .GetPropValue("Surface Representation Priority for TAU")
        == "High"
    )


@pytest.mark.skipif(not USE_GRPC, reason="Not running in COM mode")
def test_delete_mesh_ops(aedt_app) -> None:
    udp = aedt_app.modeler.Position(20, 20, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface")
    aedt_app.mesh.assign_surface_mesh(o.id, 3, "Surface")
    assert aedt_app.mesh.delete_mesh_operations("surface")
    assert len(aedt_app.mesh.meshoperation_names) == 0


def test_curvature_extraction(aedt_app) -> None:
    aedt_app.solution_type = "SBR+"
    box = aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    curv = aedt_app.mesh.assign_curvature_extraction(box.name)
    assert curv.props["DisableForFacetedSurfaces"]
    curv.props["DisableForFacetedSurfaces"] = False
    assert (
        not aedt_app.odesign.GetChildObject("Mesh")
        .GetChildObject(curv.name)
        .GetPropValue("Disable for Faceted Surface")
    )


def test_maxwell_mesh(maxwell_app) -> None:
    o = maxwell_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box_Mesh")
    rot = maxwell_app.mesh.assign_rotational_layer(o.name, total_thickness="5mm", name="Rotational")
    assert rot.props["Number of Layers"] == "3"
    rot.props["Number of Layers"] = 1
    assert str(rot.props["Number of Layers"]) == maxwell_app.odesign.GetChildObject("Mesh").GetChildObject(
        rot.name
    ).GetPropValue("Number of Layers")
    assert rot.props["Total Layer Thickness"] == "5mm"
    rot.props["Total Layer Thickness"] = "1mm"
    assert rot.props["Total Layer Thickness"] == maxwell_app.odesign.GetChildObject("Mesh").GetChildObject(
        rot.name
    ).GetPropValue("Total Layer Thickness")

    edge_cut = maxwell_app.mesh.assign_edge_cut(o.name, name="Edge")
    assert edge_cut.props["Layer Thickness"] == "1mm"
    edge_cut.props["Layer Thickness"] = "2mm"
    assert edge_cut.props["Layer Thickness"] == maxwell_app.odesign.GetChildObject("Mesh").GetChildObject(
        edge_cut.name
    ).GetPropValue("Layer Thickness")

    dens = maxwell_app.mesh.assign_density_control(o.name, maximum_element_length=10000, name="Density")
    assert dens.props["RestrictMaxElemLength"]

    assert int(dens.props["MaxElemLength"]) == 10000
    dens.props["MaxElemLength"] = 10
    assert str(dens.props["MaxElemLength"]) == maxwell_app.odesign.GetChildObject("Mesh").GetChildObject(
        dens.name
    ).GetPropValue("Max Element Length")

    assert not dens.props["RestrictLayersNum"]
    dens.props["RestrictLayersNum"] = True
    assert dens.props["RestrictLayersNum"] == maxwell_app.odesign.GetChildObject("Mesh").GetChildObject(
        dens.name
    ).GetPropValue("Restrict Layers Number")

    assert dens.props["LayersNum"] == "1"
    dens.props["LayersNum"] = 2
    assert str(dens.props["LayersNum"]) == maxwell_app.odesign.GetChildObject("Mesh").GetChildObject(
        dens.name
    ).GetPropValue("Number of layers")
