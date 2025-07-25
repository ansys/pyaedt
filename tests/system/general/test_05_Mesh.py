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

import pytest

from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.constants import Plane
from tests.system.general.conftest import config
from tests.system.general.conftest import desktop_version


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name="Test05")
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_01_assign_model_resolution(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "inner")
        mr1 = self.aedtapp.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        assert mr1.name in self.aedtapp.odesign.GetChildObject("Mesh").GetChildNames()
        mr1.name = "resolution_test"
        assert "resolution_test" in self.aedtapp.mesh.meshoperations[0].name
        mr1.name = "resolution_test"
        assert self.aedtapp.odesign.GetChildObject("Mesh")
        mr1.auto_update = False
        mr1.props["DefeatureLength"] = "0.1mm"
        assert not (
            self.aedtapp.odesign.GetChildObject("Mesh").GetChildObject(mr1.name).GetPropValue("Model Resolution Length")
            == "0.1mm"
        )
        mr1.update()
        assert (
            self.aedtapp.odesign.GetChildObject("Mesh").GetChildObject(mr1.name).GetPropValue("Model Resolution Length")
            == "0.1mm"
        )
        mr1.auto_update = True
        mr1.props["UseAutoLength"] = True
        assert self.aedtapp.odesign.GetChildObject("Mesh").GetChildObject(mr1.name).GetPropValue("Use Auto Simplify")
        o2 = self.aedtapp.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "inner")
        mr1.props["Objects"] = [o2.name, o]
        if desktop_version >= "2023.1":
            assert len(self.aedtapp.mesh.omeshmodule.GetMeshOpAssignment(mr1.name)) == 2
        mr2 = self.aedtapp.mesh.assign_model_resolution(o.faces[0], 1e-4, "ModelRes2")
        assert not mr2
        assert self.aedtapp.mesh[mr1.name].type == "DefeatureBased"

    def test_02_assign_surface_mesh(self):
        udp = self.aedtapp.modeler.Position(10, 10, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface")
        surface = self.aedtapp.mesh.assign_surface_mesh(o.id, 3, "Surface")
        assert "Surface" in [i.name for i in self.aedtapp.mesh.meshoperations]
        assert surface.props["SliderMeshSettings"] == 3

    def test_03_assign_surface_mesh_manual(self):
        udp = self.aedtapp.modeler.Position(20, 20, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface_manual")
        surface = self.aedtapp.mesh.assign_surface_mesh_manual(o.id, 1e-6, aspect_ratio=3, name="Surface_Manual")
        assert "Surface_Manual" in [i.name for i in self.aedtapp.mesh.meshoperations]
        assert surface.props["SurfDev"] == 1e-6
        surface.props["SurfDev"] = 1e-05
        assert (
            self.aedtapp.odesign.GetChildObject("Mesh").GetChildObject(surface.name).GetPropValue("Surface Deviation")
            == "1e-05"
        )
        assert surface.props["NormalDev"] == "1"
        surface.props["AspectRatio"] = 20
        assert (
            self.aedtapp.odesign.GetChildObject("Mesh").GetChildObject(surface.name).GetPropValue("Aspect Ratio")
            == "20"
        )

        cylinder_zx = self.aedtapp.modeler.create_cylinder(Plane.ZX, udp, 3, coax_dimension, 0, "surface_manual")
        surface_default_value = self.aedtapp.mesh.assign_surface_mesh_manual(cylinder_zx.id)
        assert surface_default_value.name in [i.name for i in self.aedtapp.mesh.meshoperations]
        assert surface_default_value.props["SurfDevChoice"] == 0
        assert surface_default_value.props["NormalDev"] == "1"

    def test_04_assign_surface_priority(self):
        surface = self.aedtapp.mesh.assign_surf_priority_for_tau(["surface", "surface_manual"], 1)
        assert surface.props["SurfaceRepPriority"] == 1
        surface.props["SurfaceRepPriority"] = 0
        assert (
            self.aedtapp.odesign.GetChildObject("Mesh")
            .GetChildObject(surface.name)
            .GetPropValue("Surface Representation Priority for TAU")
            == "Normal"
        )

        surface.props["SurfaceRepPriority"] = 1
        assert (
            self.aedtapp.odesign.GetChildObject("Mesh")
            .GetChildObject(surface.name)
            .GetPropValue("Surface Representation Priority for TAU")
            == "High"
        )

    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    def test_05_delete_mesh_ops(self):
        assert self.aedtapp.mesh.delete_mesh_operations("surface")
        assert len(self.aedtapp.mesh.meshoperation_names) == 2

    def test_06_curvature_extraction(self):
        self.aedtapp.solution_type = "SBR+"
        curv = self.aedtapp.mesh.assign_curvature_extraction("inner")
        assert curv.props["DisableForFacetedSurfaces"]
        curv.props["DisableForFacetedSurfaces"] = False
        assert (
            not self.aedtapp.odesign.GetChildObject("Mesh")
            .GetChildObject(curv.name)
            .GetPropValue("Disable for Faceted Surface")
        )

    def test_07_maxwell_mesh(self, add_app):
        m3d = add_app(application=Maxwell3d)
        o = m3d.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box_Mesh")
        rot = m3d.mesh.assign_rotational_layer(o.name, total_thickness="5mm", name="Rotational")
        assert rot.props["Number of Layers"] == "3"
        rot.props["Number of Layers"] = 1
        assert str(rot.props["Number of Layers"]) == m3d.odesign.GetChildObject("Mesh").GetChildObject(
            rot.name
        ).GetPropValue("Number of Layers")
        assert rot.props["Total Layer Thickness"] == "5mm"
        rot.props["Total Layer Thickness"] = "1mm"
        assert rot.props["Total Layer Thickness"] == m3d.odesign.GetChildObject("Mesh").GetChildObject(
            rot.name
        ).GetPropValue("Total Layer Thickness")

        edge_cut = m3d.mesh.assign_edge_cut(o.name, name="Edge")
        assert edge_cut.props["Layer Thickness"] == "1mm"
        edge_cut.props["Layer Thickness"] = "2mm"
        assert edge_cut.props["Layer Thickness"] == m3d.odesign.GetChildObject("Mesh").GetChildObject(
            edge_cut.name
        ).GetPropValue("Layer Thickness")

        dens = m3d.mesh.assign_density_control(o.name, maximum_element_length=10000, name="Density")
        assert dens.props["RestrictMaxElemLength"]

        assert dens.props["MaxElemLength"] == 10000
        dens.props["MaxElemLength"] = 10
        assert str(dens.props["MaxElemLength"]) == m3d.odesign.GetChildObject("Mesh").GetChildObject(
            dens.name
        ).GetPropValue("Max Element Length")

        assert not dens.props["RestrictLayersNum"]
        dens.props["RestrictLayersNum"] = True
        assert dens.props["RestrictLayersNum"] == m3d.odesign.GetChildObject("Mesh").GetChildObject(
            dens.name
        ).GetPropValue("Restrict Layers Number")

        assert dens.props["LayersNum"] == "1"
        dens.props["LayersNum"] = 2
        assert str(dens.props["LayersNum"]) == m3d.odesign.GetChildObject("Mesh").GetChildObject(
            dens.name
        ).GetPropValue("Number of layers")
