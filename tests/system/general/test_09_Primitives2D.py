#!/ekm/software/anaconda3/bin/python

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

from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Q2d
from ansys.aedt.core.modeler.cad.polylines import Polyline
import pytest


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(design_name="2D_Primitives_2", solution_type="TransientXY", application=Maxwell2d)
    return app


@pytest.fixture(scope="class")
def axisymmetrical(add_app):
    app = add_app(design_name="2D_Primitives_3", solution_type="TransientZ", application=Maxwell2d)
    return app


@pytest.fixture(scope="class")
def q2d_app(add_app):
    app = add_app(design_name="2d_extr", application=Q2d)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, axisymmetrical, local_scratch):
        self.aedtapp = aedtapp
        self.axisymmetrical = axisymmetrical
        self.local_scratch = local_scratch

    def create_rectangle(self, name=None):
        if not name:
            name = "MyRectangle"
        if self.aedtapp.modeler[name]:
            self.aedtapp.modeler.delete(name)
        o = self.aedtapp.modeler.create_rectangle([5, 3, 0], [4, 5], name=name)
        return o

    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.create_rectangle(udp, [5, 3], name="Rectangle1", material="copper")
        assert isinstance(o.id, int)
        assert o.solve_inside

    def test_03_create_circle(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o1 = self.aedtapp.modeler.create_circle(udp, 3, 0, name="Circle1", material="copper")
        assert isinstance(o1.id, int)
        o2 = self.aedtapp.modeler.create_circle(udp, 3, 8, name="Circle2", material="copper")
        assert isinstance(o2.id, int)

    def test_04_create_ellipse(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.create_ellipse(udp, 3, 2, name="Ellipse1", material="copper")
        assert isinstance(o.id, int)

    def test_05_create_poly(self):
        udp = [self.aedtapp.modeler.Position(0, 0, 0), self.aedtapp.modeler.Position(10, 5, 0)]
        o = self.aedtapp.modeler.create_polyline(udp, name="Ellipse1", material="copper")
        assert isinstance(o, Polyline)

    def test_chamfer_vertex(self):
        o = self.create_rectangle("Rectangle1")
        assert o.vertices[0].chamfer()
        o2 = self.create_rectangle("Rectangle2")
        assert o2.chamfer(o2.vertices)
        assert not o2.chamfer(edges=o2.edges)
        assert not o2.chamfer()

    def test_fillet_vertex(self):
        o = self.create_rectangle("Rectangle1")
        o.vertices[0].fillet()
        o2 = self.create_rectangle("Rectangle2")
        assert o2.fillet(o2.vertices)
        assert not o2.fillet(edges=o2.edges)

    def test_06_create_region(self):
        if self.aedtapp.modeler["Region"]:
            self.aedtapp.modeler.delete(
                "Region",
            )
        assert "Region" not in self.aedtapp.modeler.object_names
        assert self.aedtapp.modeler.create_region([20, "50", "100mm", 20], "Absolute Offset")
        self.aedtapp.modeler["Region"].delete()
        region = self.aedtapp.modeler.create_region("100", "Percentage Offset")
        region.delete()
        # test backward compatibility
        region = self.aedtapp.modeler.create_region(pad_percent=[100, 10, 5, 2], pad_type=True)
        region.delete()
        #
        region = self.aedtapp.modeler.create_region([100, 100, 100, 100])
        assert region.solve_inside
        assert region.model
        assert region.display_wireframe
        assert region.object_type == "Sheet"
        assert region.solve_inside

        region = self.aedtapp.modeler.create_region([100, 100, 100, 100, 100, 100])
        assert not region

    def test_06_a_create_region_Z(self):
        if self.axisymmetrical.modeler["Region"]:
            self.axisymmetrical.modeler.delete(
                "Region",
            )
        assert "Region" not in self.axisymmetrical.modeler.object_names
        assert not self.axisymmetrical.modeler.create_region(["100%", "50%", "20%"])
        assert self.axisymmetrical.modeler.create_region([100, 50, 20])
        self.axisymmetrical.modeler["Region"].delete()
        assert self.axisymmetrical.modeler.create_region(100)
        self.axisymmetrical.modeler["Region"].delete()
        assert self.axisymmetrical.modeler.create_region("200")
        self.axisymmetrical.modeler["Region"].delete()
        assert self.axisymmetrical.modeler.create_region([100, "50mm", 20], False)
        self.axisymmetrical.modeler["Region"].delete()
        assert self.axisymmetrical.modeler.create_region([100, "50mm", "100"], False)
        self.axisymmetrical.modeler["Region"].delete()
        assert self.axisymmetrical.modeler.create_region(["50mm", "50mm", "50mm"], False)
        self.axisymmetrical.modeler["Region"].delete()
        assert self.axisymmetrical.modeler.create_region("10mm", False)
        self.axisymmetrical.modeler["Region"].delete()

    def test_07_assign_material_ceramic(self, material="Ceramic_material"):
        self.aedtapp.assign_material(["Rectangle1"], material)
        assert self.aedtapp.modeler["Rectangle1"].material_name == material

    def test_07_assign_material(self, material="steel_stainless"):
        self.aedtapp.assign_material(["Rectangle1"], material)
        assert self.aedtapp.modeler["Rectangle1"].material_name == material

    def test_08_region(self, q2d_app):
        if q2d_app.modeler["Region"]:
            q2d_app.modeler.delete(
                "Region",
            )
        assert "Region" not in q2d_app.modeler.object_names
        assert not q2d_app.modeler.create_region(["100%", "50%", "20%", "10%"])
        assert q2d_app.modeler.create_region([100, 50, 20, 20])
        q2d_app.modeler["Region"].delete()
        assert q2d_app.modeler.create_region(100)
        q2d_app.modeler["Region"].delete()
        assert q2d_app.modeler.create_region("200")
        q2d_app.modeler["Region"].delete()
        assert q2d_app.modeler.create_region([100, "50mm", 20, 10], False)
        q2d_app.modeler["Region"].delete()
