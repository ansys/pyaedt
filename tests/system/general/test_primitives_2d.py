#!/ekm/software/anaconda3/bin/python

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

from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Q2d
from ansys.aedt.core.modeler.cad.polylines import Polyline


@pytest.fixture
def aedt_app(add_app):
    app = add_app(solution_type="TransientXY", application=Maxwell2d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def axisymmetrical_app(add_app):
    app = add_app(solution_type="TransientZ", application=Maxwell2d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def q2d_app(add_app):
    app = add_app(application=Q2d)
    yield app
    app.close_project(app.project_name, save=False)


def create_rectangle(app, name=None):
    if not name:
        name = "MyRectangle"
    if app.modeler[name]:
        app.modeler.delete(name)
    o = app.modeler.create_rectangle([5, 3, 0], [4, 5], name=name)
    return o


def test_create_primitive(aedt_app):
    udp = aedt_app.modeler.Position(0, 0, 0)
    o = aedt_app.modeler.create_rectangle(udp, [5, 3], name="Rectangle1", material="copper")
    assert isinstance(o.id, int)
    assert o.solve_inside


def test_create_circle(aedt_app):
    udp = aedt_app.modeler.Position(0, 0, 0)
    o1 = aedt_app.modeler.create_circle(udp, 3, 0, name="Circle1", material="copper")
    assert isinstance(o1.id, int)
    o2 = aedt_app.modeler.create_circle(udp, 3, 8, name="Circle2", material="copper")
    assert isinstance(o2.id, int)


def test_create_ellipse(aedt_app):
    udp = aedt_app.modeler.Position(0, 0, 0)
    o = aedt_app.modeler.create_ellipse(udp, 3, 2, name="Ellipse1", material="copper")
    assert isinstance(o.id, int)


def test_create_poly(aedt_app):
    udp = [aedt_app.modeler.Position(0, 0, 0), aedt_app.modeler.Position(10, 5, 0)]
    o = aedt_app.modeler.create_polyline(udp, name="Ellipse1", material="copper")
    assert isinstance(o, Polyline)


def test_chamfer_vertex(aedt_app):
    o = create_rectangle(aedt_app, "Rectangle1")
    assert o.vertices[0].chamfer()
    o2 = create_rectangle(aedt_app, "Rectangle2")
    assert o2.chamfer(o2.vertices)
    assert not o2.chamfer(edges=o2.edges)
    assert not o2.chamfer()


def test_fillet_vertex(aedt_app):
    o = create_rectangle(aedt_app, "Rectangle1")
    o.vertices[0].fillet()
    o2 = create_rectangle(aedt_app, "Rectangle2")
    assert o2.fillet(o2.vertices)
    assert not o2.fillet(edges=o2.edges)


def test_create_region(aedt_app):
    if aedt_app.modeler["Region"]:
        aedt_app.modeler.delete("Region")
    assert "Region" not in aedt_app.modeler.object_names
    assert aedt_app.modeler.create_region([20, "50", "100mm", 20], "Absolute Offset")
    aedt_app.modeler["Region"].delete()

    region = aedt_app.modeler.create_region("100", "Percentage Offset")
    region.delete()
    # test backward compatibility
    region = aedt_app.modeler.create_region(pad_percent=[100, 10, 5, 2], pad_type=True)
    region.delete()
    #
    region = aedt_app.modeler.create_region([100, 100, 100, 100])
    assert region.solve_inside
    assert region.model
    assert region.display_wireframe
    assert region.object_type == "Sheet"
    assert region.solve_inside

    region = aedt_app.modeler.create_region([100, 100, 100, 100, 100, 100])
    assert not region


def test_create_region_Z(axisymmetrical_app):
    if axisymmetrical_app.modeler["Region"]:
        axisymmetrical_app.modeler.delete("Region")
    assert "Region" not in axisymmetrical_app.modeler.object_names
    assert not axisymmetrical_app.modeler.create_region(["100%", "50%", "20%"])
    assert axisymmetrical_app.modeler.create_region([100, 50, 20])
    axisymmetrical_app.modeler["Region"].delete()
    assert axisymmetrical_app.modeler.create_region(100)
    axisymmetrical_app.modeler["Region"].delete()
    assert axisymmetrical_app.modeler.create_region("200")
    axisymmetrical_app.modeler["Region"].delete()
    assert axisymmetrical_app.modeler.create_region([100, "50mm", 20], False)
    axisymmetrical_app.modeler["Region"].delete()
    assert axisymmetrical_app.modeler.create_region([100, "50mm", "100"], False)
    axisymmetrical_app.modeler["Region"].delete()
    assert axisymmetrical_app.modeler.create_region(["50mm", "50mm", "50mm"], False)
    axisymmetrical_app.modeler["Region"].delete()
    assert axisymmetrical_app.modeler.create_region("10mm", False)
    axisymmetrical_app.modeler["Region"].delete()


def test_assign_material_ceramic(aedt_app):
    material = "Ceramic_material"
    o = create_rectangle(aedt_app, "Rectangle1")
    aedt_app.assign_material([o.name], material)
    assert aedt_app.modeler[o.name].material_name == material


def test_assign_material(aedt_app, material="steel_stainless"):
    o = create_rectangle(aedt_app, "Rectangle1")
    aedt_app.assign_material([o.name], material)
    assert aedt_app.modeler[o.name].material_name == material


def test_region(q2d_app):
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
