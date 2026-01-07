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


def test_assign_model_resolution(aedt_app):
    udp = aedt_app.modeler.Position(0, 0, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "inner")
    mr1 = aedt_app.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
    assert mr1.name in aedt_app.odesign.GetChildObject("Mesh").GetChildNames()
    mr1.name = "resolution_test"
    assert "resolution_test" in aedt_app.mesh.meshoperations[0].name
    mr1.name = "resolution_test"
    assert aedt_app.odesign.GetChildObject("Mesh")
    mr1.auto_update = False
    mr1.props["DefeatureLength"] = "0.1mm"
    assert not (
        aedt_app.odesign.GetChildObject("Mesh").GetChildObject(mr1.name).GetPropValue("Model Resolution Length")
        == "0.1mm"
    )
    mr1.update()
    assert (
        aedt_app.odesign.GetChildObject("Mesh").GetChildObject(mr1.name).GetPropValue("Model Resolution Length")
        == "0.1mm"
    )
    mr1.auto_update = True
    mr1.props["UseAutoLength"] = True
    assert aedt_app.odesign.GetChildObject("Mesh").GetChildObject(mr1.name).GetPropValue("Use Auto Simplify")
    o2 = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "inner")
    mr1.props["Objects"] = [o2.name, o]
    if DESKTOP_VERSION >= "2023.1":
        assert len(aedt_app.mesh.omeshmodule.GetMeshOpAssignment(mr1.name)) == 2
    mr2 = aedt_app.mesh.assign_model_resolution(o.faces[0], 1e-4, "ModelRes2")
    assert not mr2
    assert aedt_app.mesh[mr1.name].type == "DefeatureBased"


def test_assign_surface_mesh(aedt_app):
    udp = aedt_app.modeler.Position(10, 10, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface")
    surface = aedt_app.mesh.assign_surface_mesh(o.id, 3, "Surface")
    assert "Surface" in [i.name for i in aedt_app.mesh.meshoperations]
    assert surface.props["SliderMeshSettings"] == 3


def test_assign_surface_mesh_manual(aedt_app):
    udp = aedt_app.modeler.Position(20, 20, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface_manual")
    surface = aedt_app.mesh.assign_surface_mesh_manual(o.id, 1e-6, aspect_ratio=3, name="Surface_Manual")
    assert "Surface_Manual" in [i.name for i in aedt_app.mesh.meshoperations]
    assert surface.props["SurfDev"] == 1e-6
    surface.props["SurfDev"] = 1e-05
    assert (
        aedt_app.odesign.GetChildObject("Mesh").GetChildObject(surface.name).GetPropValue("Surface Deviation")
        == "1e-05"
    )
    assert surface.props["NormalDev"] == "1"
    surface.props["AspectRatio"] = 20
    assert aedt_app.odesign.GetChildObject("Mesh").GetChildObject(surface.name).GetPropValue("Aspect Ratio") == "20"

    cylinder_zx = aedt_app.modeler.create_cylinder(Plane.ZX, udp, 3, coax_dimension, 0, "surface_manual")
    surface_default_value = aedt_app.mesh.assign_surface_mesh_manual(cylinder_zx.id)
    assert surface_default_value.name in [i.name for i in aedt_app.mesh.meshoperations]
    assert surface_default_value.props["SurfDevChoice"] == 0
    assert surface_default_value.props["NormalDev"] == "1"


def test_assign_surface_priority(aedt_app):
    surface = aedt_app.mesh.assign_surf_priority_for_tau(["surface", "surface_manual"], 1)
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
def test_delete_mesh_ops(aedt_app):
    udp = aedt_app.modeler.Position(20, 20, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface")
    aedt_app.mesh.assign_surface_mesh(o.id, 3, "Surface")
    assert aedt_app.mesh.delete_mesh_operations("surface")
    assert len(aedt_app.mesh.meshoperation_names) == 0


def test_curvature_extraction(aedt_app):
    aedt_app.solution_type = "SBR+"
    curv = aedt_app.mesh.assign_curvature_extraction("inner")
    assert curv.props["DisableForFacetedSurfaces"]
    curv.props["DisableForFacetedSurfaces"] = False
    assert (
        not aedt_app.odesign.GetChildObject("Mesh")
        .GetChildObject(curv.name)
        .GetPropValue("Disable for Faceted Surface")
    )


def test_maxwell_mesh(maxwell_app):
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

    assert dens.props["MaxElemLength"] == 10000
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
