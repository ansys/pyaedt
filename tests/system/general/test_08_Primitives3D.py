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
import sys
import time

import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core import Q2d
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.components_3d import UserDefinedComponent
from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.cad.polylines import Polyline
from ansys.aedt.core.modeler.cad.primitives import PolylineSegment
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_CENTER
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_ORIGIN
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_RADIUS
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_SIZES_2
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_SIZES_3
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
from tests import TESTS_GENERAL_PATH
from tests.conftest import config

test = sys.modules.keys()

scdoc = "input.scdoc"
step = "input.stp"
component3d = "new.a3dcomp"
encrypted_cyl = "encrypted_cylinder.a3dcomp"
layout_comp = "Layoutcomponent_231.aedbcomp"
LAYOUT_COMP_SI_VERSE_SFP = "ANSYS_SVP_V1_1_SFP_main.aedbcomp"
primitive_json_file = "primitives_file.json"
cylinder_primitive_csv_file = "cylinder_geometry_creation.csv"
cylinder_primitive_csv_file_missing_values = "cylinder_geometry_creation_missing_values.csv"
cylinder_primitive_csv_file_wrong_keys = "cylinder_geometry_creation_wrong_keys.csv"
prism_primitive_csv_file = "prism_geometry_creation.csv"
prism_primitive_csv_file_missing_values = "prism_geometry_creation_missing_values.csv"
prism_primitive_csv_file_wrong_keys = "prism_geometry_creation_wrong_keys.csv"
disco = "input.dsco"

test_subfolder = "T08"
if config["desktopVersion"] > "2022.2":
    assembly = "assembly_231"
    assembly2 = "assembly2_231"
    polyline = "polyline_231"
else:
    assembly = "assembly"
    assembly2 = "assembly2"
    polyline = "polyline"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name)


# Utils functions


def create_copper_box(app, name="MyBox"):
    """Create a copper box."""
    if app.modeler[name]:
        app.modeler.delete(name)
    new_object = app.modeler.create_box([0, 0, 0], [10, 10, 5], name, "Copper")
    return new_object


def create_copper_sphere(app, name="Mysphere"):
    """Create a copper sphere."""
    if app.modeler[name]:
        app.modeler.delete(name)
    new_object = app.modeler.create_sphere([0, 0, 0], radius="1mm", name=name, material="Copper")
    return new_object


def create_copper_cylinder(app, name="MyCyl"):
    """Create a copper cylinder."""
    if app.modeler[name]:
        app.modeler.delete(name)
    new_object = app.modeler.create_cylinder(
        orientation="Y", origin=[20, 20, 0], radius=5, height=20, num_sides=8, name=name, material="Copper"
    )
    return new_object


def create_rectangle(app, name="MyRectangle"):
    """Create a rectangle."""
    if app.modeler[name]:
        app.modeler.delete(name)
    plane = Plane.XY
    new_object = app.modeler.create_rectangle(plane, [5, 3, 8], [4, 5], name=name)
    return new_object


def create_copper_torus(app, name="MyTorus"):
    """Create a copper torus."""
    if app.modeler[name]:
        app.modeler.delete(name)
    new_object = app.modeler.create_torus(
        [30, 30, 0], major_radius=1.2, minor_radius=0.5, axis="Z", name=name, material="Copper"
    )
    return new_object


def create_polylines(app, name="Poly_"):
    test_points = [[0, 100, 0], [-100, 0, 0], [-50, -50, 0], [0, 0, 0]]
    if app.modeler[name + "segmented"]:
        app.modeler.delete(
            name + "segmented",
        )
    if app.modeler[name + "compound"]:
        app.modeler.delete(
            name + "compound",
        )
    p1 = app.modeler.create_polyline(points=test_points, name=name + "segmented")
    p2 = app.modeler.create_polyline(points=test_points, segment_type=["Line", "Arc"], name=name + "compound")
    return p1, p2, test_points


# Test functions


def test_01_resolve_object(aedtapp):
    """Test resolve object."""
    box = create_copper_box(aedtapp)

    # Test with object
    resolve_object = aedtapp.modeler._resolve_object(box)
    assert isinstance(resolve_object, Object3d)
    assert resolve_object.id == box.id

    # Test with id
    resolve_object = aedtapp.modeler._resolve_object(box.id)
    assert isinstance(resolve_object, Object3d)
    assert resolve_object.id == box.id

    # Test with name
    resolve_object = aedtapp.modeler._resolve_object(box.name)
    assert isinstance(resolve_object, Object3d)
    assert resolve_object.id == box.id

    # Test invalid inputs
    invaloid_res = aedtapp.modeler._resolve_object(-1)
    assert invaloid_res is None
    invaloid_res = aedtapp.modeler._resolve_object("DummyInvalid")
    assert invaloid_res is None


def test_02_create_box(aedtapp):
    """Test create box."""
    box = create_copper_box(aedtapp, name="MyCreatedBox_11")

    assert box.id > 0
    assert box.name.startswith("MyCreatedBox_11")
    assert box.object_type == "Solid"
    assert box.is_3d
    assert box.material_name == "copper"
    assert "MyCreatedBox_11" in aedtapp.modeler.solid_names
    assert len(aedtapp.modeler.object_names) == len(aedtapp.modeler.objects)


def test_02_create_box_failure(aedtapp):
    """Test create box failure."""
    with pytest.raises(ValueError, match=ERROR_MSG_ORIGIN):
        aedtapp.modeler.create_box([0, 0], [10, 10, 10], "MyCreatedBox_12", "Copper")

    with pytest.raises(ValueError, match=ERROR_MSG_SIZES_3):
        aedtapp.modeler.create_box([0, 0, 0], [10, 10], "MyCreatedBox_12", "Copper")


def test_03_create_polyhedron_with_default_values(aedtapp):
    """Test create polyhedron with default values."""
    polyhedron = aedtapp.modeler.create_polyhedron()

    assert polyhedron.id > 0
    assert polyhedron.name.startswith("New")
    assert polyhedron.object_type == "Solid"
    assert polyhedron.is_3d
    assert polyhedron.material_name == "vacuum"
    assert polyhedron.solve_inside
    assert polyhedron.name in aedtapp.modeler.solid_names
    assert len(aedtapp.modeler.object_names) == len(aedtapp.modeler.objects)


def test_03_create_polyhedron_with_values(aedtapp):
    """Test create polyhedron with values."""
    polyhedron = aedtapp.modeler.create_polyhedron(
        orientation=Axis.Z,
        center=[0, 0, 0],
        origin=[0, 1, 0],
        height=2.0,
        num_sides=5,
        name="MyPolyhedron",
        material="Aluminum",
    )

    assert polyhedron.id > 0
    assert polyhedron.object_type == "Solid"
    assert polyhedron.is_3d
    assert polyhedron.material_name == "aluminum"
    assert not polyhedron.solve_inside
    assert polyhedron.name in aedtapp.modeler.solid_names
    assert len(aedtapp.modeler.object_names) == len(aedtapp.modeler.objects)


def test_03_create_polyhedron_failure(aedtapp):
    """Test create polyhedron failure."""
    with pytest.raises(ValueError, match=ERROR_MSG_CENTER):
        aedtapp.modeler.create_polyhedron(center=[0, 0])

    with pytest.raises(ValueError, match=ERROR_MSG_ORIGIN):
        aedtapp.modeler.create_polyhedron(origin=[0, 1])

    with pytest.raises(ValueError, match="The ``center`` and ``origin`` arguments must be different."):
        aedtapp.modeler.create_polyhedron(center=[0, 0, 0], origin=[0, 0, 0])


def test_05_center_and_centroid(aedtapp):
    """Test center and center from AEDT."""
    box = create_copper_box(aedtapp)
    tol = 1e-9

    assert GeometryOperators.v_norm(box.faces[0].center_from_aedt) - GeometryOperators.v_norm(box.faces[0].center) < tol


def test_06_position(aedtapp):
    """Test position."""
    assert aedtapp.modeler.Position([0])


def test_06_position_failure(aedtapp):
    """Test position failure."""
    with pytest.raises(IndexError):
        aedtapp.modeler.Position(0, 0, 0)[3]


def test_07_sweep_options(aedtapp):
    """Test sweep options."""
    assert aedtapp.modeler.SweepOptions()


def test_11a_get_object_name_from_edge(aedtapp):
    """Test get object name from edge."""
    box = create_copper_box(aedtapp)

    edge = box.edges[0].id

    assert aedtapp.modeler.get_object_name_from_edge_id(edge) == box.name


def test_11b_get_faces_from_materials(aedtapp):
    """Test get faces from materials."""
    create_copper_box(aedtapp)

    faces = aedtapp.modeler.get_faces_from_materials("Copper")

    assert len(faces) == len(set(faces))
    assert len(faces) == 6


def test_11c_access_to_object_faces(aedtapp):
    """Test access to object faces."""
    box = create_copper_box(aedtapp)
    face_list = box.faces

    face = box.faces[0]

    assert len(face_list) == 6
    assert isinstance(face.center, list) and len(face.center) == 3
    assert isinstance(face.area, float) and face.area > 0
    assert box.faces[0].move_with_offset(0.1)
    assert box.faces[0].move_with_vector([0, 0, 0.01])
    assert isinstance(face.normal, list)


def test_11d_check_object_edges(aedtapp):
    """Test access to object edges."""
    box = create_copper_box(aedtapp, name="MyBox")

    edge = box.edges[1]

    assert isinstance(edge.midpoint, list) and len(edge.midpoint) == 3
    assert isinstance(edge.length, float) and edge.length > 0


def test_11e_check_object_vertices(aedtapp):
    """Test access to object vertices."""
    box = create_copper_box(aedtapp, name="MyBox")

    vertex = box.vertices[0]

    assert len(box.vertices) == 8
    assert isinstance(vertex.position, list) and len(vertex.position) == 3


# TODO: personal changes (box) might not work
def test_12_get_objects_in_group(aedtapp):
    """Test access to objects in group."""
    # NOTE
    box = create_copper_box(aedtapp, name="MyBox")

    objs = aedtapp.modeler.get_objects_in_group("Solids")

    assert isinstance(objs, list)
    # NOTE
    assert box in objs


def test_13_create_circle(aedtapp):
    """Test create circle."""
    origin = aedtapp.modeler.Position(5, 3, 8)

    circle = aedtapp.modeler.create_circle(Plane.XY, origin, 2, name="MyCircle", material="Copper")

    assert circle.id > 0
    assert circle.name.startswith("MyCircle")
    assert circle.object_type == "Sheet"
    assert not circle.is_3d
    assert not circle.solve_inside


def test_13_create_circle_failure(aedtapp):
    """Test create circle failures."""
    with pytest.raises(ValueError, match=ERROR_MSG_ORIGIN):
        aedtapp.modeler.create_circle(Plane.XY, [10, 10], 2)

    with pytest.raises(ValueError, match=ERROR_MSG_RADIUS):
        aedtapp.modeler.create_circle(Plane.XY, [10, 10, 10], -1)


def test_14_create_sphere(aedtapp):
    """Test create sphere."""
    origin = aedtapp.modeler.Position(20, 20, 0)
    radius = 5

    sphere = aedtapp.modeler.create_sphere(origin, radius, "MySphere", "Copper")

    assert sphere.id > 0
    assert sphere.name.startswith("MySphere")
    assert sphere.object_type == "Solid"
    assert sphere.is_3d


def test_14_create_sphere_failures(aedtapp):
    """Test create sphere failures."""
    with pytest.raises(ValueError, match="The ``origin`` argument must be a valid three-element list."):
        aedtapp.modeler.create_sphere([10, 10], 10)

    with pytest.raises(ValueError, match="The ``radius`` argument must be greater than 0."):
        aedtapp.modeler.create_sphere([10, 10, 10], -5)


def test_15_create_cylinder(aedtapp):
    """Test create cylinder."""
    origin = aedtapp.modeler.Position(20, 20, 0)
    radius = 5
    height = 50

    cylinder = aedtapp.modeler.create_cylinder(Axis.Y, origin, radius, height, 8, "MyCyl", "Copper")

    assert cylinder.id > 0
    assert cylinder.name.startswith("MyCyl")
    assert cylinder.object_type == "Solid"
    assert cylinder.is_3d


def test_15_create_cylinder_failures(aedtapp):
    """Test create cylinder failures."""
    with pytest.raises(ValueError, match="The ``origin`` argument must be a valid three-element list."):
        aedtapp.modeler.create_cylinder(Axis.Y, [2, 2], 10, 10, 8)
    with pytest.raises(ValueError, match="The ``radius`` argument must be greater than 0."):
        aedtapp.modeler.create_cylinder(Axis.Y, [2, 2], -1, 10, 8)


def test_16_create_ellipse(aedtapp):
    """Test create ellipse."""
    origin = aedtapp.modeler.Position(5, 3, 8)

    ellipse = aedtapp.modeler.create_ellipse(Plane.XY, origin, 5, 1.5, True, name="MyEllipse", material="Copper")

    assert ellipse.id > 0
    assert ellipse.name.startswith("MyEllpise01")
    assert ellipse.object_type == "Sheet"
    assert not ellipse.is_3d
    assert not ellipse.solve_inside


def test_16_create_ellipse_with_vacuum_without_name(aedtapp):
    """Test create ellipse with vacuum and without name."""
    origin = aedtapp.modeler.Position(5, 3, 8)

    ellipse = aedtapp.modeler.create_ellipse(Plane.XY, origin, 5, 1.5, True, material="Vacuum")

    assert ellipse.id > 0
    assert ellipse.name.startswith("MyEllpise01")
    assert ellipse.object_type == "Sheet"
    assert not ellipse.is_3d
    assert not ellipse.solve_inside


def test_16_create_ellipse_uncovered(aedtapp):
    """Test create uncovered ellipse."""
    origin = aedtapp.modeler.Position(5, 3, 8)

    ellipse = aedtapp.modeler.create_ellipse(Plane.XY, origin, 5, 1.5, False)

    assert ellipse.id > 0
    assert ellipse.name.startswith("MyEllpise02")
    assert ellipse.object_type == "Line"
    assert not ellipse.is_3d
    assert not ellipse.solve_inside


def test_17_create_object_from_edge(aedtapp):
    """Test create object from edge."""
    cylinder = create_copper_cylinder(aedtapp)
    edges = cylinder.edges

    line_obj = aedtapp.modeler.create_object_from_edge(edges[0])

    assert line_obj.id > 0
    assert line_obj.object_type == "Line"
    assert not line_obj.is_3d
    assert line_obj.model


def test_17_create_object_from_edge_with_multiple_edges(aedtapp):
    """Test create from edge with multiple edges."""
    cylinder_0 = create_copper_cylinder(aedtapp, "cyl_e1")
    cylinder_1 = create_copper_cylinder(aedtapp, "cyl_e2")

    edge_objects = aedtapp.modeler.create_object_from_edge(
        [cylinder_0.edges[0], cylinder_1.edges[1], cylinder_0.edges[1]]
    )

    assert edge_objects
    assert len(edge_objects) == 3


def test_create_object_on_edge_as_non_model(aedtapp):
    """Test create object from edge as non model."""
    cylinder = create_copper_cylinder(aedtapp)
    edge = aedtapp.modeler[cylinder.name].edges[0]

    line_obj = edge.create_object(non_model=True)

    assert line_obj.id > 0
    assert line_obj.object_type == "Line"
    assert not line_obj.is_3d
    assert line_obj.model is False


def test_18_create_object_from_face(aedtapp):
    """Test create object from face."""
    cylinder = create_copper_cylinder(aedtapp)
    faces = cylinder.faces

    sheet_obj = aedtapp.modeler.create_object_from_face(faces[0])

    assert sheet_obj.id > 0
    assert sheet_obj.object_type == "Sheet"
    assert not sheet_obj.is_3d


def test_18_create_object_from_multiple_faces(aedtapp):
    """Test create object from multiple faces."""
    cylinder_0 = create_copper_cylinder(aedtapp, "cyl_f1")
    cylinder_1 = create_copper_cylinder(aedtapp, "cyl_f2")

    face_objects = aedtapp.modeler.create_object_from_face(
        [cylinder_0.faces[0], cylinder_1.faces[1], cylinder_1.faces[1], cylinder_0.faces[2]]
    )

    assert face_objects
    assert len(face_objects) == 4


# NOTE: Should we call is_model instead of model ?
def test_create_object_on_face(aedtapp):
    """Test create object on face."""
    cylinder = create_copper_cylinder(aedtapp)

    sheet = aedtapp.modeler[cylinder.name].faces[0].create_object(non_model=True)

    assert sheet.id > 0
    assert sheet.object_type == "Sheet"
    assert not sheet.is_3d
    assert not sheet.model


def test_create_polyline_failure(aedtapp):
    """Test create polyline failure."""
    aedtapp["p1"] = "100mm"
    aedtapp["p2"] = "71mm"
    points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

    with pytest.raises(
        ValueError, match="The position_list argument must contain at least 4 points for segment of type Spline."
    ):
        aedtapp.modeler.create_polyline(points=points[0:3], segment_type="Spline", name="PL03_spline_str_3pt")


def test_19_create_polyline_with_cover_surface(aedtapp):
    """Test create polyline with cover surface."""
    position_0 = [0, 0, 0]
    position_1 = [5, 0, 0]
    position_2 = [5, 5, 0]
    position_3 = [2, 5, 3]
    arrofpos = [position_0, position_3, position_1, position_2, position_0]

    polyline = aedtapp.modeler.create_polyline(arrofpos, cover_surface=True, name="Poly1", material="Copper")

    assert isinstance(polyline, Polyline)
    assert isinstance(polyline, Object3d)
    assert polyline.object_type == "Sheet"
    assert not polyline.is_3d
    assert isinstance(polyline.color, tuple)
    assert isinstance(aedtapp.modeler["Poly1"], Object3d)


def test_19_create_polyline_with_non_model(aedtapp):
    """Test create polyline as non model."""
    position_0 = [0, 0, 0]
    position_1 = [5, 0, 0]
    position_2 = [5, 5, 0]
    position_3 = [2, 5, 3]
    arrofpos = [position_0, position_3, position_1, position_2, position_0]

    polyline = aedtapp.modeler.create_polyline(
        arrofpos, cover_surface=False, name="Poly_nonmodel", material="Copper", non_model=True
    )

    assert isinstance(polyline, Polyline)
    assert isinstance(polyline, Object3d)
    assert not polyline.model
    assert polyline.object_type == "Sheet"
    assert not polyline.is_3d


def test_19_create_polyline_with_segment_type(aedtapp):
    """Test create polyline with segment type."""
    coordinates = [[0.4, 0, 0], [-0.4, -0.6, 0], [0.4, 0, 0]]
    segment_type = [
        PolylineSegment(segment_type="AngularArc", arc_center=[0, 0, 0], arc_angle="180deg", arc_plane="XY"),
        PolylineSegment(segment_type="Line"),
        PolylineSegment(segment_type="AngularArc", arc_center=[0, -0.6, 0], arc_angle="180deg", arc_plane="XY"),
        PolylineSegment(segment_type="Line"),
    ]

    polyline: Polyline = aedtapp.modeler.create_polyline(points=coordinates, segment_type=segment_type)

    assert isinstance(polyline, Polyline)
    assert isinstance(polyline, Object3d)
    assert not polyline.model
    assert polyline.object_type == "Sheet"
    assert polyline.is_3d


def test_20_create_polyline_with_crosssection(aedtapp):
    """Test create polyline with cross section."""
    coordinates = [[0, 0, 0], [5, 0, 0], [5, 5, 0]]

    polyline = aedtapp.modeler.create_polyline(coordinates, name="Poly_xsection", xsection_type="Rectangle")

    assert isinstance(polyline, Polyline)
    assert aedtapp.modeler[polyline.id].object_type == "Solid"
    assert aedtapp.modeler[polyline.id].is3d


def test_21_sweep_along_path_with_single_assignment(aedtapp):
    """Test sweep along path with single assignment."""
    coordinates = [[0, 0, 0], [5, 0, 0], [5, 5, 0]]
    poyline = aedtapp.modeler.create_polyline(coordinates, name="poly_vector1")
    rectangle = aedtapp.modeler.create_rectangle(Plane.YZ, [0, -2, -4], [4, 3], name="rect_1")

    assert aedtapp.modeler.sweep_along_path(rectangle, poyline)
    assert rectangle.name in aedtapp.modeler.solid_names


def test_21_sweep_along_path_with_multiple_assignment(aedtapp):
    """Test sweep along path with multiple assignment."""
    coordinates = [[0, 0, 0], [5, 0, 0], [5, 5, 0]]
    polyline = aedtapp.modeler.create_polyline(coordinates, name="poly_vector1")
    rectangle_0 = aedtapp.modeler.create_rectangle(Plane.YZ, [0, -2, 2], [4, 3], name="rect_2")
    rectangle_1 = aedtapp.modeler.create_rectangle(Plane.YZ, [0, -2, 8], [4, 3], name="rect_3")

    assert aedtapp.modeler.sweep_along_path([rectangle_0, rectangle_1], polyline)
    assert rectangle_0.name in aedtapp.modeler.solid_names
    assert rectangle_1.name in aedtapp.modeler.solid_names


def test_22_sweep_along_vector_with_single_assignment(aedtapp):
    """Test sweep along vector method with single assignment."""
    rectangle = aedtapp.modeler.create_rectangle(Plane.YZ, [0, -2, -2], [4, 3], name="rect_1")

    assert aedtapp.modeler.sweep_along_vector(rectangle, [10, 20, 20])
    assert rectangle.name in aedtapp.modeler.solid_names


def test_22_sweep_along_vector_with_multiple_assignment(aedtapp):
    """Test sweep along vector method with multiple assignment."""
    rectangle_0 = aedtapp.modeler.create_rectangle(Plane.YZ, [0, -2, 2], [4, 3], name="rect_2")
    rectangle_1 = aedtapp.modeler.create_rectangle(Plane.YZ, [0, -2, 4], [4, 3], name="rect_3")

    assert aedtapp.modeler.sweep_along_vector([rectangle_0, rectangle_1], [10, 20, 20])
    assert rectangle_0.name in aedtapp.modeler.solid_names
    assert rectangle_1.name in aedtapp.modeler.solid_names


def test_23_create_rectangle(aedtapp):
    """Test create rectangle."""
    origin = aedtapp.modeler.Position(5, 3, 8)

    rectangle = aedtapp.modeler.create_rectangle(Plane.XY, origin, [4, 5], name="MyRectangle", material="Copper")

    assert rectangle.id > 0
    assert rectangle.name.startswith("MyRectangle")
    assert rectangle.object_type == "Sheet"
    assert rectangle.is_3d is not False


def test_23_create_rectangle_failure(aedtapp):
    """Test create rectangle failures."""
    origin = aedtapp.modeler.Position(5, 3, 8)

    with pytest.raises(ValueError, match=ERROR_MSG_SIZES_2):
        aedtapp.modeler.create_rectangle(Plane.XY, origin, [4, 5, 10], name="MyRectangle", material="Copper")


def test_24_create_cone(aedtapp):
    """Test create cone."""
    origin = aedtapp.modeler.Position(5, 3, 8)

    cone = aedtapp.modeler.create_cone(Axis.Z, origin, 20, 10, 5, name="MyCone", material="Copper")

    assert cone.id > 0
    assert cone.name.startswith("MyCone")
    assert cone.object_type == "Solid"
    assert cone.is_3d


def test_24_create_cone_failure(aedtapp):
    """Test create cone failures."""
    origin = aedtapp.modeler.Position(5, 3, 8)

    with pytest.raises(ValueError):
        aedtapp.modeler.create_cone(Axis.Z, [1, 1], 20, 10, 5, name="MyCone", material="Copper")
    with pytest.raises(ValueError):
        aedtapp.modeler.create_cone(Axis.Z, origin, -20, 20, 5, name="MyCone", material="Copper")
    with pytest.raises(ValueError):
        aedtapp.modeler.create_cone(Axis.Z, origin, 20, -20, 5, name="MyCone", material="Copper")
    with pytest.raises(ValueError):
        aedtapp.modeler.create_cone(Axis.Z, origin, 20, 20, -5, name="MyCone", material="Copper")


def test_25_get_object_id(aedtapp):
    """Test get object id."""
    rectangle = aedtapp.modeler.create_rectangle(Plane.XY, [5, 3, 8], [4, 5], name="MyRectangle5")

    assert aedtapp.modeler.get_obj_id(rectangle.name) == rectangle.id


def test_26_get_solid_objects(aedtapp):
    """Test solid objects retrieval and properties."""
    box = create_copper_box(aedtapp)
    solid_list = aedtapp.modeler.solid_names
    solid_obj = aedtapp.modeler[box.name]
    all_objects_list = aedtapp.modeler.object_names

    assert box.name in solid_list
    assert box.name in all_objects_list
    assert solid_obj.is_3d
    assert solid_obj.object_type == "Solid"


def test_26_get_sheet_objects(aedtapp):
    """Test sheet objects retrieval and properties."""
    rectangle = create_rectangle(aedtapp)
    sheet_list = aedtapp.modeler.sheet_names
    sheet_obj = aedtapp.modeler[rectangle.name]
    all_objects_list = aedtapp.modeler.object_names

    assert rectangle.name in sheet_list
    assert rectangle.name in all_objects_list
    assert not sheet_obj.is_3d
    assert sheet_obj.object_type == "Sheet"


def test_26_get_line_objects(aedtapp):
    """Test line objects retrieval and properties."""
    polyline_0, polyline_1, _ = create_polylines(aedtapp)
    line_list = aedtapp.modeler.line_names
    line_obj_0 = aedtapp.modeler[polyline_0.name]
    line_obj_1 = aedtapp.modeler[polyline_1.name]
    all_objects_list = aedtapp.modeler.object_names

    assert polyline_0.name in line_list
    assert polyline_0.name in all_objects_list
    assert polyline_1.name in line_list
    assert polyline_1.name in all_objects_list
    assert not line_obj_0.is_3d
    assert line_obj_0.object_type == "Line"
    assert not line_obj_1.is_3d
    assert line_obj_1.object_type == "Line"


def test_26d_object_count_consistency(aedtapp):
    """Test that total object count is consistent across all lists."""
    # Create objects of all types
    polyline_0, polyline_1, _ = create_polylines()
    box = create_copper_box()
    rectangle = create_rectangle()

    # Get all lists
    solid_list = aedtapp.modeler.solid_names
    sheet_list = aedtapp.modeler.sheet_names
    line_list = aedtapp.modeler.line_names
    all_objects_list = aedtapp.modeler.object_names

    # Test count consistency
    assert len(all_objects_list) == len(solid_list) + len(line_list) + len(sheet_list)

    # Test all our objects are present
    created_objects = [box.name, rectangle.name, polyline_0.name, polyline_1.name]
    assert all(map(lambda obj: obj in all_objects_list, created_objects))


def test_27_get_object_by_material(aedtapp):
    """Test get objects by material."""
    _ = create_copper_box(aedtapp)

    copper_objects = aedtapp.modeler.get_objects_by_material("copper")
    fr4_objects = aedtapp.modeler.get_objects_by_material("FR4")
    lists_objects = aedtapp.modeler.get_objects_by_material()

    assert len(copper_objects) > 0
    assert len(fr4_objects) == 0
    assert set(aedtapp.materials.conductors).issubset([mat for sublist in lists_objects for mat in sublist])
    assert set(aedtapp.materials.dielectrics).issubset([mat for sublist in lists_objects for mat in sublist])


def test_29_get_edges_from_position(aedtapp):
    """Test get edges from position."""
    _ = create_rectangle(aedtapp, name="MyRectangle_for_primitives")
    origin = aedtapp.modeler.Position(5, 3, 8)

    edge_id = aedtapp.modeler.get_edgeid_from_position(origin)
    assert edge_id > 0


def test_29_get_edges_from_position_with_assignment(aedtapp):
    """Test get edges from position with assignment."""
    rectangle = create_rectangle(aedtapp, name="MyRectangle_for_primitives")
    origin = aedtapp.modeler.Position(5, 3, 8)

    edge_id = aedtapp.modeler.get_edgeid_from_position(origin, rectangle.name)
    assert edge_id > 0


# TODO: This test and others should be moved to a different file focusing on primitive operations (not 3D)
def test_30_get_faces_from_position_with_list_object(aedtapp):
    """Test get faces from position with list object."""
    _ = create_rectangle(aedtapp, name="New_Rectangle1")

    edge_id = aedtapp.modeler.get_faceid_from_position([5, 3, 8], "New_Rectangle1")

    assert edge_id > 0


def test_30_get_faces_from_position_with_position_object(aedtapp):
    """Test get faces from position with position object."""
    _ = create_rectangle(aedtapp)
    position = aedtapp.modeler.Position(100, 100, 100)

    edge_id = aedtapp.modeler.get_faceid_from_position(position)

    assert not edge_id


def test_31_delete_object(aedtapp):
    """Test delete object."""
    _ = create_rectangle(name="MyRectangle")
    assert "MyRectangle" in aedtapp.modeler.object_names

    deleted = aedtapp.modeler.delete("MyRectangle")

    assert deleted
    assert "MyRectangle" not in aedtapp.modeler.object_names


def test_32_get_face_vertices(aedtapp):
    """Test get face vertices."""
    rectangle = aedtapp.modeler.create_rectangle(Plane.XY, [1, 2, 3], [7, 13])
    faces = aedtapp.modeler.get_object_faces(rectangle.name)

    vertices = aedtapp.modeler.get_face_vertices(faces[0])

    assert len(vertices) == 4


def test_33_get_edge_vertices(aedtapp):
    """Test get edge vertices."""
    rectangle = aedtapp.modeler.create_rectangle(Plane.XY, [1, 2, 3], [7, 13])
    listedges = aedtapp.modeler.get_object_edges(rectangle.name)

    vertices = aedtapp.modeler.get_edge_vertices(listedges[0])

    assert len(vertices) == 2


def test_34_get_vertex_position(aedtapp):
    """Test get vertex position."""
    rectangle = aedtapp.modeler.create_rectangle(Plane.XY, [1, 2, 3], [7, 13])
    edges = aedtapp.modeler.get_object_edges(rectangle.name)
    vertices = aedtapp.modeler.get_edge_vertices(edges[0])

    pos_0 = aedtapp.modeler.get_vertex_position(vertices[0])
    pos_1 = aedtapp.modeler.get_vertex_position(vertices[1])
    edge_length = ((pos_0[0] - pos_1[0]) ** 2 + (pos_0[1] - pos_1[1]) ** 2 + (pos_0[2] - pos_1[2]) ** 2) ** 0.5

    assert len(pos_0) == 3
    assert len(pos_1) == 3
    assert edge_length == 7


def test_35_get_face_area(aedtapp):
    """Test get face area."""
    rectangle = aedtapp.modeler.create_rectangle(Plane.XY, [1, 2, 3], [7, 13])
    listfaces = aedtapp.modeler.get_object_faces(rectangle.name)

    area = aedtapp.modeler.get_face_area(listfaces[0])

    assert area == 7 * 13


@pytest.mark.skipif(config["desktopVersion"] < "2023.1" and config["use_grpc"], reason="Not working in 2022.2 gRPC")
def test_36_get_face_center(aedtapp):
    """Test get face center."""
    rectangle = aedtapp.modeler.create_rectangle(
        Plane.XY,
        [1, 2, 3],
        [7, 13],
    )
    faces = aedtapp.modeler.get_object_faces(rectangle.name)
    center = aedtapp.modeler.get_face_center(faces[0])

    assert center == [4.5, 8.5, 3.0]


@pytest.mark.skipif(config["desktopVersion"] < "2023.1" and config["use_grpc"], reason="Not working in 2022.2 gRPC")
def test_36_get_face_center_through_property(aedtapp):
    """Test get face center through property."""
    cylinder = aedtapp.modeler.create_cylinder(orientation=1, origin=[0, 0, 0], radius=10, height=10)
    if config["desktopVersion"] >= "2023.1":
        centers = [[0, 10, 0], [0, 0, 0], [0, 5, 10]]
    else:
        centers = [[0, 0, 0], [0, 10, 0], [0, 5, 0]]

    cyl_centers = [face.center for face in cylinder.faces]

    for c0, c1 in zip(centers, cyl_centers):
        assert GeometryOperators.points_distance(c0, c1) < 1e-10


def test_37_get_edge_midpoint(aedtapp):
    """Test get edge midpoint."""
    polyline = aedtapp.modeler.create_polyline([[0, 0, 0], [10, 5, 3]])

    point = aedtapp.modeler.get_edge_midpoint(polyline.id)

    assert point == [5.0, 2.5, 1.5]


def test_38_get_bodynames_from_position(aedtapp):
    """Test get body names from position"""
    origin = [20, 20, 0]
    sphere = aedtapp.modeler.create_sphere(origin, 1, "fred")
    rectangle = aedtapp.modeler.create_rectangle(Plane.XY, [-50, -50, -50], [2, 2], name="bob")
    position_0 = aedtapp.modeler.Position(-23, -23, 13)
    position_1 = aedtapp.modeler.Position(-27, -27, 11)
    position_2 = aedtapp.modeler.Position(-31, -31, 7)
    position_3 = aedtapp.modeler.Position(2, 5, 3)
    positions = [position_0, position_1, position_2, position_3]
    polyline = aedtapp.modeler.create_polyline(positions, cover_surface=False, name="bill")

    names_0 = aedtapp.modeler.get_bodynames_from_position(origin)
    names_1 = aedtapp.modeler.get_bodynames_from_position([-49.0, -49.0, -50.0])
    names_2 = aedtapp.modeler.get_bodynames_from_position([-27, -27, 11])

    assert sphere.name in names_0
    assert rectangle.name in names_1
    assert polyline.name in names_2


def test_39_getobjects_with_strings(aedtapp):
    """Test get objects with strings."""
    origin = aedtapp.modeler.Position(5, 3, 8)
    _ = aedtapp.modeler.create_cone(Axis.Z, origin, 20, 10, 5, name="MyCustomCone", material="Copper")

    objs_0 = aedtapp.modeler.get_objects_w_string("MyCustomCone")
    objs_1 = aedtapp.modeler.get_objects_w_string("mycustom", False)
    objs_2 = aedtapp.modeler.get_objects_w_string("mycustom")

    assert len(objs_0) > 0
    assert len(objs_1) > 0
    assert len(objs_2) == 0


def test_40_getmodel_objects(aedtapp):
    """Test get model objects consistency."""
    cylinder = create_copper_cylinder(aedtapp)
    edge = aedtapp.modeler[cylinder.name].edges[0]
    _ = edge.create_object(non_model=True)
    _ = edge.create_object(non_model=False)

    model_objects_names = aedtapp.modeler.model_objects
    non_model_objects_names = aedtapp.modeler.non_model_objects
    names = aedtapp.modeler.object_names

    assert set(model_objects_names).isdisjoint(set(non_model_objects_names))
    assert set(model_objects_names).union(set(non_model_objects_names)) == set(names)


def test_41a_create_rect_sheet_to_ground_with_ground_name(aedtapp):
    """Test create rectangle sheet to ground."""
    _ = create_copper_box(aedtapp, name="MyBox_to_gnd")

    ground_plane = aedtapp.modeler.create_sheet_to_ground("MyBox_to_gnd")

    assert isinstance(ground_plane, Object3d)
    assert ground_plane.id > 0


def test_41b_create_rect_sheet_to_ground_with_multiple_arguments(aedtapp):
    """Test create rectangle sheet to ground with multiple arguments."""
    rect = create_rectangle(aedtapp)
    box = create_copper_box(aedtapp)

    ground_plane = aedtapp.modeler.create_sheet_to_ground(box.name, rect.name, aedtapp.AxisDir.ZNeg)

    assert isinstance(ground_plane, Object3d)
    assert ground_plane.id > 0


def test_41c_get_edges_for_circuit_port(aedtapp):
    """Test get edges for circuit port."""
    rectangle = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 8], [3, 10], name="MyGND", material="Copper")
    face_id = rectangle.faces[0].id

    edges = aedtapp.modeler.get_edges_for_circuit_port(
        face_id, xy_plane=True, yz_plane=False, xz_plane=False, allow_perpendicular=True, tolerance=1e-6
    )

    assert edges
    assert 2 == len(edges)
    assert all(isinstance(edge, int) and edge > 0 for edge in edges)


def test_41c_get_edges_for_circuit_port_from_sheet(aedtapp):
    """Test get edges for circuit port from sheet."""
    _ = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 8], [3, 10], name="MyGND", material="Copper")

    edges = aedtapp.modeler.get_edges_for_circuit_port_from_sheet(
        "MyGND", xy_plane=True, yz_plane=False, xz_plane=False, allow_perpendicular=True, tolerance=1e-6
    )

    assert edges
    assert 2 == len(edges)
    assert all(isinstance(edge, int) and edge > 0 for edge in edges)


def test_43_fillet_and_undo(aedtapp):
    """Test fillet and undo."""
    box = create_copper_box(aedtapp, name="MyBox")

    res = box.edges[0].fillet()

    assert res
    aedtapp._odesign.Undo()

    res = box.edges[0].fillet()

    assert res


def test_43_fillet_failure(aedtapp):
    """Test fillet failure."""
    rectangle = create_rectangle(aedtapp, name="MyRect")
    with pytest.raises(AEDTRuntimeError):
        rectangle.edges[0].fillet()


def test_43_fillet_with_edges(aedtapp):
    """Test fillet with edges."""
    box = create_copper_box(aedtapp, name="MyBox2")

    res = box.fillet(edges=box.edges)

    assert res


# def test_44_create_polyline_basic_segments(aedtapp):
#     """Test create polyline with basic segments."""
#     modeler = aedtapp.modeler
#     aedtapp["p1"] = "100mm"
#     aedtapp["p2"] = "71mm"
#     test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

#     p1 = modeler.create_polyline(points=test_points[0:2], name="PL01_line")
#     assert len(p1.start_point) == 3
#     assert len(p1.end_point) == 3
#     assert modeler.create_polyline(points=test_points[0:3], segment_type="Arc", name="PL02_arc")

#     assert modeler.create_polyline(
#         points=test_points, segment_type=PolylineSegment("Spline", num_points=4), name="PL03_spline_4pt"
#     )
#     assert modeler.create_polyline(
#         points=test_points, segment_type=PolylineSegment("Spline", num_points=3), name="PL03_spline_3pt"
#     )
#     with pytest.raises(ValueError) as execinfo:
#         modeler.create_polyline(points=test_points[0:3], segment_type="Spline", name="PL03_spline_str_3pt")
#         assert (
#             str(execinfo)
#             == "The 'position_list' argument must contain at least four points for segment of type 'Spline'."
#         )
#     assert modeler.create_polyline(
#         points=[[100, 100, 0]],
#         segment_type=PolylineSegment("AngularArc", arc_center=[0, 0, 0], arc_angle="30deg"),
#         name="PL04_center_point_arc",
#     )
#     assert modeler.create_polyline(
#         points=[[100, 100, 0]],
#         segment_type=PolylineSegment("AngularArc", arc_angle="30deg"),
#         name="PL04_center_point_arc",
#     )


def test_45_create_circle_from_2_arc_segments(aedtapp):
    prim3D = aedtapp.modeler
    assert prim3D.create_polyline(
        points=[[34.1004, 14.1248, 0], [27.646, 16.7984, 0], [24.9725, 10.3439, 0], [31.4269, 7.6704, 0]],
        segment_type=["Arc", "Arc"],
        cover_surface=True,
        close_surface=True,
        name="Rotor_Subtract_25_0",
        material="vacuum",
    )


def test_46_compound_polylines_segments(aedtapp):
    prim3D = aedtapp.modeler
    aedtapp["p1"] = "100mm"
    aedtapp["p2"] = "71mm"
    test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

    assert prim3D.create_polyline(points=test_points, name="PL06_segmented_compound_line")
    assert prim3D.create_polyline(points=test_points, segment_type=["Line", "Arc"], name="PL05_compound_line_arc")
    assert prim3D.create_polyline(points=test_points, close_surface=True, name="PL07_segmented_compound_line_closed")
    assert prim3D.create_polyline(points=test_points, cover_surface=True, name="SPL01_segmented_compound_line")


def test_47_insert_polylines_segments_test1(aedtapp):
    aedtapp["p1"] = "100mm"
    aedtapp["p2"] = "71mm"
    test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]
    P = aedtapp.modeler.create_polyline(
        points=test_points, close_surface=False, name="PL08_segmented_compound_insert_segment"
    )
    assert P
    assert len(P.points) == 4
    assert P.points == [
        ["0mm", "p1", "0mm"],
        ["-p1", "0mm", "0mm"],
        ["-p1/2", "-p1/2", "0mm"],
        ["0mm", "0mm", "0mm"],
    ]
    start_point = P.start_point
    insert_point = ["90mm", "20mm", "0mm"]
    insert_point2 = ["95mm", "20mm", "0mm"]
    assert P.insert_segment(points=[start_point, insert_point])
    assert len(P.points) == 5
    assert P.points == [
        ["0mm", "p1", "0mm"],
        ["90mm", "20mm", "0mm"],
        ["-p1", "0mm", "0mm"],
        ["-p1/2", "-p1/2", "0mm"],
        ["0mm", "0mm", "0mm"],
    ]
    assert P.insert_segment(points=[insert_point, insert_point2])
    assert len(P.points) == 6
    assert P.points == [
        ["0mm", "p1", "0mm"],
        ["90mm", "20mm", "0mm"],
        ["95mm", "20mm", "0mm"],
        ["-p1", "0mm", "0mm"],
        ["-p1/2", "-p1/2", "0mm"],
        ["0mm", "0mm", "0mm"],
    ]
    assert P.insert_segment(points=[["-p1", "0mm", "0mm"], ["-110mm", "-35mm", "0mm"]])
    assert len(P.points) == 7
    assert P.points == [
        ["0mm", "p1", "0mm"],
        ["90mm", "20mm", "0mm"],
        ["95mm", "20mm", "0mm"],
        ["-p1", "0mm", "0mm"],
        ["-110mm", "-35mm", "0mm"],
        ["-p1/2", "-p1/2", "0mm"],
        ["0mm", "0mm", "0mm"],
    ]
    assert P.insert_segment(points=[["-80mm", "10mm", "0mm"], ["-p1", "0mm", "0mm"]])
    assert len(P.points) == 8
    assert P.points == [
        ["0mm", "p1", "0mm"],
        ["90mm", "20mm", "0mm"],
        ["95mm", "20mm", "0mm"],
        ["-80mm", "10mm", "0mm"],
        ["-p1", "0mm", "0mm"],
        ["-110mm", "-35mm", "0mm"],
        ["-p1/2", "-p1/2", "0mm"],
        ["0mm", "0mm", "0mm"],
    ]
    assert P.insert_segment(points=[["0mm", "0mm", "0mm"], ["10mm", "10mm", "0mm"]])
    assert len(P.points) == 9
    assert P.points == [
        ["0mm", "p1", "0mm"],
        ["90mm", "20mm", "0mm"],
        ["95mm", "20mm", "0mm"],
        ["-80mm", "10mm", "0mm"],
        ["-p1", "0mm", "0mm"],
        ["-110mm", "-35mm", "0mm"],
        ["-p1/2", "-p1/2", "0mm"],
        ["0mm", "0mm", "0mm"],
        ["10mm", "10mm", "0mm"],
    ]
    assert P.insert_segment(points=[["10mm", "5mm", "0mm"], ["0mm", "0mm", "0mm"]])
    assert len(P.points) == 10
    assert P.points == [
        ["0mm", "p1", "0mm"],
        ["90mm", "20mm", "0mm"],
        ["95mm", "20mm", "0mm"],
        ["-80mm", "10mm", "0mm"],
        ["-p1", "0mm", "0mm"],
        ["-110mm", "-35mm", "0mm"],
        ["-p1/2", "-p1/2", "0mm"],
        ["10mm", "5mm", "0mm"],
        ["0mm", "0mm", "0mm"],
        ["10mm", "10mm", "0mm"],
    ]


def test_48_insert_polylines_segments_test2(aedtapp):
    prim3D = aedtapp.modeler
    aedtapp["p1"] = "100mm"
    aedtapp["p2"] = "71mm"
    test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

    P = prim3D.create_polyline(points=test_points, close_surface=False, name="PL08_segmented_compound_insert_arc")
    start_point = P.points[1]
    insert_point1 = ["-120mm", "-25mm", "0mm"]
    insert_point2 = [-115, -40, 0]

    P.insert_segment(points=[start_point, insert_point1, insert_point2], segment="Arc")


def test_49_modify_crossection(aedtapp):
    P = aedtapp.modeler.create_polyline(
        points=[[34.1004, 14.1248, 0], [27.646, 16.7984, 0], [24.9725, 10.3439, 0]],
        name="Rotor_Subtract_25_0",
        material="copper",
    )
    P1 = P.clone()
    P2 = P.clone()
    P3 = P.clone()
    P4 = P.clone()

    P1.set_crosssection_properties(section="Line", width="1mm")

    P2.set_crosssection_properties(section="Circle", width="1mm", num_seg=5)
    P3.set_crosssection_properties(section="Rectangle", width="1mm", height="1mm")
    P4.set_crosssection_properties(section="Isosceles Trapezoid", width="1mm", topwidth="4mm", height="1mm")

    assert P.object_type == "Line"
    assert P1.object_type == "Sheet"
    assert P2.object_type == "Solid"
    assert P3.object_type == "Solid"
    assert P4.object_type == "Solid"


class TestClass:
    def test_50_remove_vertex_from_polyline(self):
        p1, p2, test_points = self.create_polylines("Poly_remove_")

        P = self.aedtapp.modeler["Poly_remove_segmented"]
        P.remove_point(test_points[2])
        time.sleep(0.1)
        P1 = self.aedtapp.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P1.remove_point([0, 1, 2])
        time.sleep(0.1)

        P2 = self.aedtapp.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P2.remove_point(["0mm", "1mm", "2mm"])
        time.sleep(0.1)

        P3 = self.aedtapp.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 2, 5]])
        P3.remove_point(["3mm", "2mm", "5mm"])
        time.sleep(0.1)

        P4 = self.aedtapp.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P4.remove_point(["0mm", "1mm", "2mm"], tolerance=1e-6)

    def test_51_remove_edges_from_polyline(self):
        modeler = self.aedtapp.modeler
        P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P.remove_segments(assignment=0)
        assert P.points == [[0, 2, 3], [2, 1, 4]]
        assert len(P.segment_types) == 1
        assert P.name in self.aedtapp.modeler.line_names
        P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
        P.remove_segments(assignment=[0, 1])
        assert P.points == [[2, 1, 4], [3, 1, 6]]
        assert len(P.segment_types) == 1
        assert P.name in self.aedtapp.modeler.line_names
        P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
        P.remove_segments(assignment=1)
        assert P.points == [[0, 1, 2], [2, 1, 4], [3, 1, 6]]
        assert len(P.segment_types) == 2
        assert P.name in self.aedtapp.modeler.line_names
        P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [2, 2, 5], [3, 1, 6]])
        P.remove_segments(assignment=[1, 3])
        assert P.points == [[0, 1, 2], [2, 1, 4], [2, 2, 5]]
        assert len(P.segment_types) == 2
        assert P.name in self.aedtapp.modeler.line_names
        P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
        P.remove_segments(assignment=[1, 2])
        assert P.points == [[0, 1, 2], [0, 2, 3]]
        assert len(P.segment_types) == 1
        assert P.name in self.aedtapp.modeler.line_names
        P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
        P.remove_segments(assignment=2)
        assert P.points == [[0, 1, 2], [0, 2, 3], [2, 1, 4]]
        assert len(P.segment_types) == 2
        assert P.name in self.aedtapp.modeler.line_names

    def test_52_remove_edges_from_polyline_invalid(self):
        P = self.aedtapp.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P.remove_segments(assignment=[0, 1])
        assert P.name not in self.aedtapp.modeler.line_names

    def test_53_duplicate_polyline_and_manipulate(self):
        P1 = self.aedtapp.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P2 = P1.clone()
        assert P2.id != P1.id

    def test_54a_create_spiral_and_add_segments(self):
        self.aedtapp.insert_design("spiral_test")
        save_model_units = self.aedtapp.modeler.model_units
        self.aedtapp.modeler.model_units = "um"
        innerRadius = 20
        wireThickness_um = 1
        numberOfTurns = 5
        NumberOfFaces = 10

        ind = self.aedtapp.modeler.create_spiral(
            internal_radius=innerRadius,
            spacing=wireThickness_um,
            turns=numberOfTurns,
            faces=NumberOfFaces,
            material="copper",
            name="Inductor1",
        )

        ind.set_crosssection_properties(section="Circle", width=wireThickness_um)

        polyline_points = ind.points

        pn = polyline_points[-1]
        new_point = [pn[0], pn[1], 10]
        position_lst = [pn, new_point]
        ind.insert_segment(position_lst)
        assert len(ind.points) == 48
        assert len(ind.segment_types) == 47

        p0 = polyline_points[0]
        position_lst = [[14, -12, 0], p0]
        ind.insert_segment(position_lst)
        assert len(ind.points) == 49
        assert len(ind.segment_types) == 48

        position_lst = [p0, [12, 2, 0]]
        ind.insert_segment(position_lst)
        assert len(ind.points) == 50
        assert len(ind.segment_types) == 49

        p5 = polyline_points[5]
        position_lst = [[12, 10, 0], p5]
        ind.insert_segment(position_lst)
        assert len(ind.points) == 51
        assert len(ind.segment_types) == 50

        p6 = polyline_points[6]
        position_lst = [p6, [-2, 18, 0], [-4, 18, 0]]
        ind.insert_segment(position_lst, "Arc")
        assert len(ind.points) == 53
        assert len(ind.segment_types) == 51

        p10 = polyline_points[10]
        position_lst = [[-14, 10, 0], [-16, 6, 0], p10]
        ind.insert_segment(position_lst, "Arc")
        assert len(ind.points) == 55
        assert len(ind.segment_types) == 52

        p13 = polyline_points[13]
        position_lst = [p13, [-16, -8, 0], [-14, -10, 0], [-10, -10, 0], [-10, -14, 0]]
        ind.insert_segment(position_lst, self.aedtapp.modeler.polyline_segment("Spline", num_points=5))
        assert len(ind.points) == 59
        assert len(ind.segment_types) == 53

        p19 = polyline_points[19]
        position_lst = [[-8, -21, 0], [-4, -18, 0], [-2, -22, 0], p19]
        ind.insert_segment(position_lst, self.aedtapp.modeler.polyline_segment("Spline", num_points=4))
        assert len(ind.points) == 62
        assert len(ind.segment_types) == 54

        pm4 = polyline_points[-4]
        position_lst = [pm4]
        ind.insert_segment(
            position_lst,
            self.aedtapp.modeler.polyline_segment(
                "AngularArc", arc_center=[-28, 26, 0], arc_angle="225.9deg", arc_plane="XY"
            ),
        )
        assert len(ind.points) == 64
        assert len(ind.segment_types) == 55

        # test unclassified
        p11 = polyline_points[11]
        position_lst = [[-142, 130, 0], [-126, 63, 0], p11]
        with pytest.raises(ValueError) as execinfo:
            ind.insert_segment(position_lst, "Arc")
            assert str(execinfo) == "Adding the segment result in an unclassified object. Undoing operation."
        assert len(ind.points) == 64
        assert len(ind.segment_types) == 55

        self.aedtapp.modeler.model_units = save_model_units

    def test_54b_open_and_load_a_polyline(self, add_app):
        aedtapp = add_app(project_name=polyline, subfolder=test_subfolder)

        poly1 = aedtapp.modeler["Inductor1"]
        poly2 = aedtapp.modeler["Polyline1"]
        poly3 = aedtapp.modeler["Polyline2"]

        p1 = poly1.points
        s1 = poly1.segment_types
        assert len(p1) == 10
        assert len(s1) == 9
        p2 = poly2.points
        s2 = poly2.segment_types
        assert len(p2) == 13
        assert len(s2) == 7
        p3 = poly3.points
        s3 = poly3.segment_types
        assert len(p3) == 3
        assert len(s3) == 1

        aedtapp.close_project(save=False)

    def test_55_create_bond_wires(self):
        self.aedtapp["$Ox"] = 0
        self.aedtapp["$Oy"] = 0
        self.aedtapp["$Oz"] = 0
        self.aedtapp["$Endx"] = 10
        self.aedtapp["$Endy"] = 10
        self.aedtapp["$Endz"] = 2
        self.aedtapp["$bondHeight1"] = "0.15mm"
        self.aedtapp["$bondHeight2"] = "0mm"
        b0 = self.aedtapp.modeler.create_bondwire(
            [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, diameter=0.034, facets=8, name="jedec51", material="copper"
        )
        assert b0
        b1 = self.aedtapp.modeler.create_bondwire(
            [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, bond_type=1, diameter=0.034, name="jedec41", material="copper"
        )
        assert b1
        b2 = self.aedtapp.modeler.create_bondwire(
            [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, bond_type=2, diameter=0.034, name="low", material="copper"
        )
        assert b2
        b3 = self.aedtapp.modeler.create_bondwire(
            [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, bond_type=3, diameter=0.034, name="jedec41", material="copper"
        )
        assert not b3
        b4 = self.aedtapp.modeler.create_bondwire(
            (2, 2, 0), (0, 0, 0), h1=0.15, h2=0, bond_type=1, diameter=0.034, name="jedec41", material="copper"
        )
        assert b4
        b5 = self.aedtapp.modeler.create_bondwire(
            ("$Ox", "$Oy", "$Oz"),
            ("$Endx", "$Endy", "$Endz"),
            h1=0.15,
            h2=0,
            bond_type=1,
            diameter=0.034,
            name="jedec41",
            material="copper",
        )
        assert b5
        b6 = self.aedtapp.modeler.create_bondwire(
            [0, 0, 0],
            [10, 10, 2],
            h1="$bondHeight1",
            h2="$bondHeight2",
            bond_type=2,
            diameter=0.034,
            name="low",
            material="copper",
        )
        assert b6
        assert not self.aedtapp.modeler.create_bondwire(
            [0, 0], [10, 10, 2], h1=0.15, h2=0, diameter=0.034, facets=8, name="jedec51", material="copper"
        )
        assert not self.aedtapp.modeler.create_bondwire(
            [0, 0, 0], [10, 10], h1=0.15, h2=0, diameter=0.034, facets=8, name="jedec51", material="copper"
        )

    def test_56_create_group(self):
        assert self.aedtapp.modeler.create_group(["jedec51", "jedec41"], "mygroup")
        assert self.aedtapp.modeler.ungroup("mygroup")

    def test_57_flatten_assembly(self):
        assert self.aedtapp.modeler.flatten_assembly()

    def test_58_solving_volume(self):
        vol = self.aedtapp.modeler.get_solving_volume()
        assert float(vol) > 0

    def test_59_lines(self):
        self.aedtapp.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]], close_surface=True)
        assert self.aedtapp.modeler.vertex_data_of_lines()

    @pytest.mark.skipif("UNITTEST_CURRENT_TEST" in os.environ, reason="Issue in IronPython")
    def test_60_get_edges_on_bounding_box(self):
        self.aedtapp.close_project(name=self.aedtapp.project_name, save=False)
        self.aedtapp.load_project(self.test_99_project)
        edges = self.aedtapp.modeler.get_edges_on_bounding_box(["Port1", "Port2"], return_colinear=True, tolerance=1e-6)
        assert len(edges) == 2
        edges = self.aedtapp.modeler.get_edges_on_bounding_box(
            ["Port1", "Port2"], return_colinear=False, tolerance=1e-6
        )
        assert len(edges) == 4

    def test_61_get_closest_edge_to_position(self):
        self.create_copper_box("test_closest_edge")
        assert isinstance(self.aedtapp.modeler.get_closest_edgeid_to_position([0.2, 0, 0]), int)

    @pytest.mark.skipif(config["NonGraphical"] or is_linux, reason="Not running in non-graphical mode or in Linux")
    def test_62_import_space_claim(self):
        self.aedtapp.insert_design("SCImport")
        assert self.aedtapp.modeler.import_spaceclaim_document(self.scdoc_file)
        assert len(self.aedtapp.modeler.objects) == 1

    @pytest.mark.skipif(is_linux, reason="Not running in Linux with AEDT 2024R1")
    def test_63_import_step(self):
        self.aedtapp.insert_design("StepImport")
        assert self.aedtapp.modeler.import_3d_cad(self.step_file)
        assert len(self.aedtapp.modeler.object_names) == 1

    def test_64_create_3dcomponent(self):
        if is_linux:
            self.aedtapp.insert_design("StepImport")
            self.create_copper_box("Solid")
        self.aedtapp.solution_type = "Modal"
        for i in list(self.aedtapp.modeler.objects.keys()):
            self.aedtapp.modeler.objects[i].material_name = "copper"

        # Folder doesn't exist. Cannot create component.
        assert not self.aedtapp.modeler.create_3dcomponent(self.component3d_file, create_folder=False)

        # By default, the new folder is created.
        assert self.aedtapp.modeler.create_3dcomponent(self.component3d_file)
        assert os.path.exists(self.component3d_file)
        variables = self.aedtapp.get_component_variables(self.component3d_file)
        assert isinstance(variables, dict)
        new_obj = self.aedtapp.modeler.duplicate_along_line("Solid", [100, 0, 0])
        rad = self.aedtapp.assign_radiation_boundary_to_objects("Solid")
        obj1 = self.aedtapp.modeler[new_obj[1][0]]
        exc = self.aedtapp.wave_port(obj1.faces[0])
        self.aedtapp["test_variable"] = "20mm"
        box1 = self.aedtapp.modeler.create_box([0, 0, 0], [10, "test_variable", 30])
        box2 = self.aedtapp.modeler.create_box([0, 0, 0], [10, 100, 30])
        self.aedtapp.mesh.assign_length_mesh([box1.name, box2.name])
        assert self.aedtapp.modeler.create_3dcomponent(
            self.component3d_file,
            variables_to_include=["test_variable"],
            assignment=["Solid", new_obj[1][0], box1.name, box2.name],
            boundaries=[rad.name],
            excitations=[exc.name],
            coordinate_systems="Global",
        )
        assert os.path.exists(self.component3d_file)

    def test_64_create_3d_component_encrypted(self):
        assert self.aedtapp.modeler.create_3dcomponent(
            self.component3d_file, coordinate_systems="Global", is_encrypted=True, password="password_test"
        )
        assert self.aedtapp.modeler.create_3dcomponent(
            self.component3d_file,
            coordinate_systems="Global",
            is_encrypted=True,
            password="password_test",
            hide_contents=["Solid"],
        )
        assert not self.aedtapp.modeler.create_3dcomponent(
            self.component3d_file,
            coordinate_systems="Global",
            is_encrypted=True,
            password="password_test",
            password_type="Invalid",
        )
        assert not self.aedtapp.modeler.create_3dcomponent(
            self.component3d_file,
            coordinate_systems="Global",
            is_encrypted=True,
            password="password_test",
            component_outline="Invalid",
        )

    def test_65_create_equationbased_curve(self):
        self.aedtapp.insert_design("Equations")
        eq_line = self.aedtapp.modeler.create_equationbased_curve(x_t="_t", y_t="_t*2", num_points=0)
        assert len(eq_line.edges) == 1
        eq_segmented = self.aedtapp.modeler.create_equationbased_curve(x_t="_t", y_t="_t*2", num_points=5)
        assert len(eq_segmented.edges) == 4
        eq_xsection = self.aedtapp.modeler.create_equationbased_curve(x_t="_t", y_t="_t*2", xsection_type="Circle")
        assert eq_xsection.name in self.aedtapp.modeler.solid_names

    def test_66a_insert_3dcomponent(self):
        self.aedtapp.solution_type = "Modal"
        self.aedtapp["l_dipole"] = "13.5cm"
        compfile = self.aedtapp.components3d["Dipole_Antenna_DM"]
        geometryparams = self.aedtapp.get_component_variables("Dipole_Antenna_DM")
        geometryparams["dipole_length"] = "l_dipole"
        obj_3dcomp = self.aedtapp.modeler.insert_3d_component(compfile, geometryparams)
        assert isinstance(obj_3dcomp, UserDefinedComponent)

    @pytest.mark.skipif(config["desktopVersion"] > "2022.2", reason="Method failing in version higher than 2022.2")
    @pytest.mark.skipif(config["use_grpc"] and config["desktopVersion"] < "2023.1", reason="Failing in grpc")
    def test_66b_insert_encrypted_3dcomp(self):
        assert not self.aedtapp.modeler.insert_3d_component(self.encrypted_cylinder)
        # assert not self.aedtapp.modeler.insert_3d_component(self.encrypted_cylinder, password="dfgdg")
        assert self.aedtapp.modeler.insert_3d_component(self.encrypted_cylinder, password="test")

    def test_66c_group_components(self):
        self.aedtapp["l_dipole"] = "13.5cm"

        compfile = self.aedtapp.components3d["Dipole_Antenna_DM"]
        geometryparams = self.aedtapp.get_component_variables("Dipole_Antenna_DM")
        geometryparams["dipole_length"] = "l_dipole"
        obj_3dcomp1 = self.aedtapp.modeler.insert_3d_component(compfile, geometryparams)
        obj_3dcomp2 = self.aedtapp.modeler.insert_3d_component(compfile, geometryparams)
        assert (
            self.aedtapp.modeler.create_group(components=[obj_3dcomp1.name, obj_3dcomp2.name], group_name="test_group")
            == "test_group"
        )

    def test_66d_component_bounding_box(self):
        self.aedtapp["tau_variable"] = "0.65"
        my_udmPairs = []
        mypair = ["OuterRadius", "20.2mm"]
        my_udmPairs.append(mypair)
        mypair = ["Tau", "tau_variable"]
        my_udmPairs.append(mypair)
        mypair = ["Sigma", "0.81"]
        my_udmPairs.append(mypair)
        mypair = ["Delta_Angle", "45deg"]
        my_udmPairs.append(mypair)
        mypair = ["Beta_Angle", "45deg"]
        my_udmPairs.append(mypair)
        mypair = ["Port_Gap_Width", "8.1mm"]
        my_udmPairs.append(mypair)
        self.aedtapp.modeler.create_udm(
            udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
            parameters=my_udmPairs,
            library="syslib",
            name="test_udm_83",
        )
        assert (
            GeometryOperators.v_norm(
                GeometryOperators.v_sub(
                    self.aedtapp.modeler.user_defined_components["test_udm_83"].bounding_box,
                    [-18.662366556727996, -20.2, 0.0, 18.662366556727996, 20.2, 0.0],
                )
            )
            < 1e-10
        )

        assert (
            GeometryOperators.v_norm(
                GeometryOperators.v_sub(
                    self.aedtapp.modeler.user_defined_components["test_udm_83"].center,
                    [0.0, 0.0, 0.0],
                )
            )
            < 1e-10
        )

    def test_67_assign_material(self):
        box1 = self.aedtapp.modeler.create_box([60, 60, 60], [4, 5, 5])
        box2 = self.aedtapp.modeler.create_box([50, 50, 50], [2, 3, 4])
        cyl1 = self.aedtapp.modeler.create_cylinder(orientation="X", origin=[50, 0, 0], radius=1, height=20)
        cyl2 = self.aedtapp.modeler.create_cylinder(orientation="Z", origin=[0, 0, 50], radius=1, height=10)

        assert box1.solve_inside
        assert box2.solve_inside
        assert cyl1.solve_inside
        assert cyl2.solve_inside

        box3 = self.aedtapp.modeler.create_box([40, 40, 40], [6, 8, 9], material="pec")
        assert not box3.solve_inside

        objects_list = [box1, box2, cyl1, cyl2]
        self.aedtapp.assign_material(objects_list, "copper")
        assert self.aedtapp.modeler[box1].material_name == "copper"
        assert self.aedtapp.modeler[box2].material_name == "copper"
        assert self.aedtapp.modeler[cyl1].material_name == "copper"
        assert self.aedtapp.modeler[cyl2].material_name == "copper"

        obj_names_list = [box1.name, box2.name, cyl1.name, cyl2.name]
        self.aedtapp.assign_material(obj_names_list, "aluminum")
        assert self.aedtapp.modeler[box1].material_name == "aluminum"
        assert self.aedtapp.modeler[box2].material_name == "aluminum"
        assert self.aedtapp.modeler[cyl1].material_name == "aluminum"
        assert self.aedtapp.modeler[cyl2].material_name == "aluminum"

    def test_68_cover_lines(self):
        P1 = self.aedtapp.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]], close_surface=True)
        assert self.aedtapp.modeler.cover_lines(P1)

    def test_69_create_torus(self):
        torus = self.create_copper_torus()
        assert torus.id > 0
        assert torus.name.startswith("MyTorus")
        assert torus.object_type == "Solid"
        assert torus.is3d is True

    def test_70_create_torus_exceptions(self):
        assert self.aedtapp.modeler.create_torus(
            [30, 30, 0], major_radius=1.3, minor_radius=0.5, axis="Z", name="torus", material="Copper"
        )
        assert not self.aedtapp.modeler.create_torus(
            [30, 30], major_radius=1.3, minor_radius=0.5, axis="Z", name="torus", material="Copper"
        )

    def test_71_create_point(self):
        name = "mypoint"
        if self.aedtapp.modeler[name]:
            self.aedtapp.modeler.delete(name)
        point = self.aedtapp.modeler.create_point([30, 30, 0], name)
        point.set_color("(143 175 158)")
        point2 = self.aedtapp.modeler.create_point([50, 30, 0], "mypoint2", "(100 100 100)")
        point.logger.info("Creation and testing of a point.")

        assert point.name == "mypoint"
        assert point.coordinate_system == "Global"
        assert point2.name == "mypoint2"
        assert point2.coordinate_system == "Global"

        assert self.aedtapp.modeler.points[point.name] == point
        assert self.aedtapp.modeler.points[point2.name] == point2

        # Delete the first point
        assert len(self.aedtapp.modeler.points) == 2
        self.aedtapp.modeler.points[point.name].delete()
        assert name not in self.aedtapp.modeler.points
        self.aedtapp.modeler.points
        assert len(self.aedtapp.modeler.point_objects) == 1
        assert len(self.aedtapp.modeler.point_names) == 1
        assert self.aedtapp.modeler.point_objects[0].name == "mypoint2"

    def test_71_create_plane(self):
        self.aedtapp.set_active_design("3D_Primitives")
        name = "my_plane"
        if self.aedtapp.modeler[name]:
            self.aedtapp.modeler.delete(name)
        plane = self.aedtapp.modeler.create_plane(name, "-0.7mm", "0.3mm", "0mm", "0.7mm", "-0.3mm", "0mm")
        assert name in self.aedtapp.modeler.planes
        plane.set_color("(143 75 158)")
        assert plane.name == name
        plane.name = "my_plane1"
        assert plane.name == "my_plane1"

        plane2 = self.aedtapp.modeler.create_plane(
            plane_base_x="-0.7mm",
            plane_base_z="0.3mm",
            plane_normal_x="-0.7mm",
            plane_normal_z="0.3mm",
            name="my_plane2",
            color="(100 100 100)",
        )
        plane.logger.info("Creation and testing of a plane.")

        assert plane.name == "my_plane1"
        assert plane.coordinate_system == "Global"
        assert plane2.name == "my_plane2"
        assert plane2.coordinate_system == "Global"

        assert self.aedtapp.modeler.planes["my_plane1"].name == plane.name
        assert self.aedtapp.modeler.planes["my_plane2"].name == plane2.name

        # Delete the first plane
        if config["desktopVersion"] < "2023.1":
            assert len(self.aedtapp.modeler.planes) == 2
        else:
            assert len(self.aedtapp.modeler.planes) == 5
        self.aedtapp.modeler.planes["my_plane1"].delete()
        assert name not in self.aedtapp.modeler.planes

    @pytest.mark.parametrize(
        "filename",
        [
            "choke_1winding_1Layer_Corrected.json",
            "choke_2winding_1Layer_Common_Corrected.json",
            "choke_2winding_2Layer_Linked_Differential_Corrected.json",
            "choke_3winding_3Layer_Separate_Corrected.json",
            "choke_4winding_3Layer_Linked_Corrected.json",
            "choke_2winding_2Layer_Common_Corrected.json",
        ],
    )
    def test_71_create_choke(self, filename):
        self.aedtapp.insert_design(generate_unique_name("Chokes"))
        choke_file1 = os.path.join(TESTS_GENERAL_PATH, "example_models", "choke_json_file", filename)

        resolve1 = self.aedtapp.modeler.create_choke(choke_file1)

        assert isinstance(resolve1, list)
        assert resolve1[0]
        assert isinstance(resolve1[1], Object3d)
        for i in range(2, len(resolve1)):
            assert isinstance(resolve1[i][0], Object3d)
            assert isinstance(resolve1[i][1], list)
        self.aedtapp.delete_design(self.aedtapp.design_name)

    def test_72_check_choke_values(self):
        self.aedtapp.insert_design("ChokeValues")
        choke_file1 = os.path.join(
            TESTS_GENERAL_PATH, "example_models", "choke_json_file", "choke_1winding_1Layer.json"
        )
        choke_file2 = os.path.join(
            TESTS_GENERAL_PATH, "example_models", "choke_json_file", "choke_2winding_1Layer_Common.json"
        )
        choke_file3 = os.path.join(
            TESTS_GENERAL_PATH, "example_models", "choke_json_file", "choke_2winding_2Layer_Linked_Differential.json"
        )
        choke_file4 = os.path.join(
            TESTS_GENERAL_PATH, "example_models", "choke_json_file", "choke_3winding_3Layer_Separate.json"
        )
        choke_file5 = os.path.join(
            TESTS_GENERAL_PATH, "example_models", "choke_json_file", "choke_4winding_3Layer_Linked.json"
        )
        choke_file6 = os.path.join(
            TESTS_GENERAL_PATH, "example_models", "choke_json_file", "choke_1winding_3Layer_Linked.json"
        )
        choke_file7 = os.path.join(
            TESTS_GENERAL_PATH, "example_models", "choke_json_file", "choke_2winding_2Layer_Common.json"
        )
        scratch_choke_file1 = self.local_scratch.copyfile(choke_file1)
        scratch_choke_file2 = self.local_scratch.copyfile(choke_file2)
        scratch_choke_file3 = self.local_scratch.copyfile(choke_file3)
        scratch_choke_file4 = self.local_scratch.copyfile(choke_file4)
        scratch_choke_file5 = self.local_scratch.copyfile(choke_file5)
        scratch_choke_file6 = self.local_scratch.copyfile(choke_file6)
        scratch_choke_file7 = self.local_scratch.copyfile(choke_file7)
        resolve1 = self.aedtapp.modeler.check_choke_values(scratch_choke_file1, create_another_file=False)
        resolve2 = self.aedtapp.modeler.check_choke_values(scratch_choke_file2, create_another_file=False)
        resolve3 = self.aedtapp.modeler.check_choke_values(scratch_choke_file3, create_another_file=False)
        resolve4 = self.aedtapp.modeler.check_choke_values(scratch_choke_file4, create_another_file=False)
        resolve5 = self.aedtapp.modeler.check_choke_values(scratch_choke_file5, create_another_file=False)
        resolve6 = self.aedtapp.modeler.check_choke_values(scratch_choke_file6, create_another_file=False)
        resolve7 = self.aedtapp.modeler.check_choke_values(scratch_choke_file7, create_another_file=False)
        assert isinstance(resolve1, list)
        assert resolve1[0]
        assert isinstance(resolve1[1], dict)
        assert isinstance(resolve2, list)
        assert resolve2[0]
        assert isinstance(resolve2[1], dict)
        assert isinstance(resolve3, list)
        assert resolve3[0]
        assert isinstance(resolve3[1], dict)
        assert isinstance(resolve4, list)
        assert resolve4[0]
        assert isinstance(resolve4[1], dict)
        assert isinstance(resolve5, list)
        assert resolve5[0]
        assert isinstance(resolve5[1], dict)
        assert isinstance(resolve6, list)
        assert resolve6[0]
        assert isinstance(resolve6[1], dict)
        assert isinstance(resolve7, list)
        assert resolve7[0]
        assert isinstance(resolve7[1], dict)

    def test_73_make_winding(self):
        self.aedtapp.insert_design("Make_Windings")
        chamfer = self.aedtapp.modeler._make_winding_follow_chamfer(0.8, 1.1, 2, 1)
        winding_list = self.aedtapp.modeler._make_winding(
            "Winding", "copper", 29.9, 52.1, 22.2, 22.2, 5, 15, chamfer, True
        )
        assert isinstance(winding_list, list)
        assert isinstance(winding_list[0], Object3d)
        assert isinstance(winding_list[1], list)

    def test_74_make_double_linked_winding(self):
        chamfer = self.aedtapp.modeler._make_winding_follow_chamfer(0.8, 1.1, 2, 1)
        winding_list = self.aedtapp.modeler._make_double_linked_winding(
            "Double_Winding",
            "copper",
            27.7,
            54.3,
            26.6,
            2,
            3,
            3,
            15,
            16,
            0.8,
            chamfer,
            1.1,
        )
        assert isinstance(winding_list, list)
        assert isinstance(winding_list[0], Object3d)
        assert isinstance(winding_list[1], list)

    def test_75_make_triple_linked_winding(self):
        chamfer = self.aedtapp.modeler._make_winding_follow_chamfer(0.8, 1.1, 2, 1)
        winding_list = self.aedtapp.modeler._make_triple_linked_winding(
            "Triple_Winding",
            "copper",
            25.5,
            56.5,
            31.0,
            2,
            2.5,
            2.5,
            2.5,
            10,
            12,
            14,
            0.8,
            chamfer,
            1.1,
        )
        assert isinstance(winding_list, list)
        assert isinstance(winding_list[0], Object3d)
        assert isinstance(winding_list[1], list)

    def test_make_winding_port_line(self):
        self.aedtapp.insert_design("Make_Winding_Port_Line")
        chamfer = self.aedtapp.modeler._make_winding_follow_chamfer(0.8, 1.1, 2, 1)

        # Test double winding - should have 4 occurrences of most negative Z value
        double_winding_list = self.aedtapp.modeler._make_double_winding(
            "Double_Winding", "copper", 17.525, 32.475, 14.95, 1.5, 2.699, 2.699, 20, 20, 0.8, chamfer, 1.1, True
        )

        # Test triple winding - should have 6 occurrences of most negative Z value
        triple_winding_list = self.aedtapp.modeler._make_triple_winding(
            "Triple_Winding",
            "copper",
            17.525,
            32.475,
            14.95,
            1.5,
            2.699,
            2.699,
            2.699,
            20,
            20,
            20,
            0.8,
            chamfer,
            1.1,
            True,
        )
        # Verify there are is more than 1 object created for each winding type
        assert isinstance(double_winding_list, list)
        assert isinstance(triple_winding_list, list)

        # For double windings: most negative Z should appear 4 times
        double_winding_obj = double_winding_list[0][1]
        double_winding_obj.extend(double_winding_list[1][1])
        double_z_coords = [point[2] for point in double_winding_obj]
        min_z_double = min(double_z_coords)
        assert double_z_coords.count(min_z_double) == 4
        # For triple windings: most negative Z should appear 6 times
        triple_winding_obj = triple_winding_list[0][1]
        triple_winding_obj.extend(triple_winding_list[1][1])
        triple_winding_obj.extend(triple_winding_list[2][1])
        triple_z_coords = [point[2] for point in triple_winding_obj]
        min_z_triple = min(triple_z_coords)
        assert triple_z_coords.count(min_z_triple) == 6

    def test_76_check_value_type(self):
        self.aedtapp.insert_design("other_tests")
        resolve1, boolean1 = self.aedtapp.modeler._check_value_type(2, float, True, "SUCCESS", "SUCCESS")
        resolve2, boolean2 = self.aedtapp.modeler._check_value_type(1, int, True, "SUCCESS", "SUCCESS")
        resolve3, boolean3 = self.aedtapp.modeler._check_value_type(1.1, float, False, "SUCCESS", "SUCCESS")
        assert isinstance(resolve1, float)
        assert boolean1
        assert isinstance(resolve2, int)
        assert boolean2
        assert isinstance(resolve3, float)
        assert not boolean3

    def test_77_create_helix(self):
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        udp3 = [10, 5, 0]
        udp4 = [15, 3, 0]
        polyline = self.aedtapp.modeler.create_polyline(
            [udp1, udp2, udp3, udp4], cover_surface=False, name="helix_polyline"
        )

        helix_right_turn = self.aedtapp.modeler.create_helix(
            assignment=polyline.name,
            origin=[0, 0, 0],
            x_start_dir=0,
            y_start_dir=1.0,
            z_start_dir=1.0,
            turns=1,
            right_hand=True,
            radius_increment=0.0,
            thread=1.0,
        )

        assert helix_right_turn.object_units == "mm"

        # Test left turn without providing argument value for default parameters.
        udp1 = [-45, 0, 0]
        udp2 = [-50, 0, 0]
        udp3 = [-105, 5, 0]
        udp4 = [-110, 3, 0]
        polyline_left = self.aedtapp.modeler.create_polyline(
            [udp1, udp2, udp3, udp4], cover_surface=False, name="helix_polyline_left"
        )

        assert self.aedtapp.modeler.create_helix(
            assignment=polyline_left.name,
            origin=[0, 0, 0],
            x_start_dir=1.0,
            y_start_dir=1.0,
            z_start_dir=1.0,
            right_hand=False,
        )

        assert not self.aedtapp.modeler.create_helix(
            assignment="", origin=[0, 0, 0], x_start_dir=1.0, y_start_dir=1.0, z_start_dir=1.0
        )

        assert not self.aedtapp.modeler.create_helix(
            assignment=polyline_left.name,
            origin=[0, 0],
            x_start_dir=1.0,
            y_start_dir=1.0,
            z_start_dir=1.0,
            right_hand=False,
        )

    def test_78_get_touching_objects(self):
        box1 = self.aedtapp.modeler.create_box([-20, -20, -20], [1, 1, 1], material="copper")
        box2 = self.aedtapp.modeler.create_box([-20, -20, -19], [0.2, 0.2, 0.2], material="copper")
        assert box2.name in box1.touching_objects
        assert box2.name in box1.touching_conductors()
        assert box1.name in box2.touching_objects
        assert box2.name in box1.faces[0].touching_objects
        if config["desktopVersion"] > "2022.2":
            assert box2.name not in box1.faces[3].touching_objects
        else:
            assert box2.name not in box1.faces[1].touching_objects
        assert box2.get_touching_faces(box1)

    @pytest.mark.skipif(config["desktopVersion"] > "2022.2", reason="Method failing in version higher than 2022.2")
    @pytest.mark.skipif(config["desktopVersion"] < "2023.1", reason="Method failing 2022.2")
    def test_79_3dcomponent_operations(self):
        self.aedtapp.solution_type = "Modal"
        self.aedtapp["l_dipole"] = "13.5cm"
        compfile = self.aedtapp.components3d["Dipole_Antenna_DM"]
        geometryparams = self.aedtapp.get_component_variables("Dipole_Antenna_DM")
        geometryparams["dipole_length"] = "l_dipole"
        obj_3dcomp = self.aedtapp.modeler.insert_3d_component(compfile, geometryparams)
        assert isinstance(obj_3dcomp, UserDefinedComponent)
        assert obj_3dcomp.group_name == "Model"
        obj_3dcomp.group_name = "test_group1"
        assert obj_3dcomp.group_name == "test_group1"
        obj_3dcomp.group_name = "test_group"
        assert obj_3dcomp.group_name == "test_group"
        assert obj_3dcomp.is3dcomponent
        assert not obj_3dcomp.mesh_assembly
        obj_3dcomp.mesh_assembly = True
        assert obj_3dcomp.mesh_assembly
        obj_3dcomp.name = "Dipole_pyaedt"
        assert "Dipole_pyaedt" in self.aedtapp.modeler.user_defined_component_names
        assert self.aedtapp.modeler["Dipole_pyaedt"]
        assert obj_3dcomp.name == "Dipole_pyaedt"
        if config["desktopVersion"] < "2023.1":
            assert obj_3dcomp.parameters["dipole_length"] == "l_dipole"
            self.aedtapp["l_dipole2"] = "15.5cm"
            obj_3dcomp.parameters["dipole_length"] = "l_dipole2"
            assert obj_3dcomp.parameters["dipole_length"] == "l_dipole2"
        cs = self.aedtapp.modeler.create_coordinate_system()
        obj_3dcomp.target_coordinate_system = cs.name
        assert obj_3dcomp.target_coordinate_system == cs.name
        obj_3dcomp.delete()
        self.aedtapp.save_project()
        self.aedtapp._project_dictionary = None
        assert "Dipole_pyaedt" not in self.aedtapp.modeler.user_defined_component_names
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(30, 40, 40)
        self.aedtapp.modeler.set_working_coordinate_system("Global")
        obj_3dcomp = self.aedtapp.modeler["Dipole_Antenna2"]
        assert obj_3dcomp.mirror(udp, udp2)
        assert obj_3dcomp.rotate(axis="Y", angle=180)
        assert obj_3dcomp.move(udp2)

        new_comps = obj_3dcomp.duplicate_around_axis(axis="Z", angle=8, clones=3)
        assert new_comps[0] in self.aedtapp.modeler.user_defined_component_names

        udp = self.aedtapp.modeler.Position(5, 5, 5)
        num_clones = 5
        attached_clones = obj_3dcomp.duplicate_along_line(udp, num_clones)
        assert attached_clones[0] in self.aedtapp.modeler.user_defined_component_names

        attached_clones = obj_3dcomp.duplicate_along_line(
            self.aedtapp.modeler.Position(-5, -5, -5), 2, attach_object=True
        )
        assert attached_clones[0] in self.aedtapp.modeler.user_defined_component_names

    @pytest.mark.skipif(config["desktopVersion"] > "2022.2", reason="Method failing in version higher than 2022.2")
    @pytest.mark.skipif(config["desktopVersion"] < "2023.1", reason="Method failing 2022.2")
    def test_80_udm_operations(self):
        my_udmPairs = []
        mypair = ["OuterRadius", "20.2mm"]
        my_udmPairs.append(mypair)
        mypair = ["Tau", "0.65"]
        my_udmPairs.append(mypair)
        mypair = ["Sigma", "0.81"]
        my_udmPairs.append(mypair)
        mypair = ["Delta_Angle", "45deg"]
        my_udmPairs.append(mypair)
        mypair = ["Beta_Angle", "45deg"]
        my_udmPairs.append(mypair)
        mypair = ["Port_Gap_Width", "8.1mm"]
        my_udmPairs.append(mypair)
        obj_udm = self.aedtapp.modeler.create_udm(
            udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
            parameters=my_udmPairs,
            library="syslib",
            name="test_udm",
        )
        assert isinstance(obj_udm, UserDefinedComponent)
        assert len(self.aedtapp.modeler.user_defined_component_names) == len(
            self.aedtapp.modeler.user_defined_components
        )
        assert obj_udm.group_name == "Model"
        obj_udm.group_name = "test_group1"
        assert obj_udm.group_name == "test_group1"
        obj_udm.group_name = "test_group"
        assert obj_udm.group_name == "test_group"
        assert not obj_udm.is3dcomponent
        assert not obj_udm.mesh_assembly
        obj_udm.mesh_assembly = True
        assert not obj_udm.mesh_assembly
        obj_udm.name = "antenna_pyaedt"
        assert "antenna_pyaedt" in self.aedtapp.modeler.user_defined_component_names
        obj_udm.name = "MyTorus"
        assert obj_udm.name == "antenna_pyaedt"
        assert obj_udm.parameters["OuterRadius"] == "20.2mm"
        obj_udm.parameters["OuterRadius"] = "21mm"
        assert obj_udm.parameters["OuterRadius"] == "21mm"
        cs = self.aedtapp.modeler.create_coordinate_system()
        obj_udm.target_coordinate_system = cs.name
        assert obj_udm.target_coordinate_system == cs.name
        obj_udm.delete()
        self.aedtapp.save_project()
        self.aedtapp._project_dictionary = None
        assert "antenna_pyaedt" not in self.aedtapp.modeler.user_defined_component_names
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(30, 40, 40)
        obj_udm = self.aedtapp.modeler.create_udm(
            udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
            parameters=my_udmPairs,
            library="syslib",
            name="test_udm",
        )
        assert obj_udm.mirror(udp, udp2)
        assert obj_udm.rotate(axis="Y", angle=180)
        assert obj_udm.move(udp2)
        assert not obj_udm.duplicate_around_axis(axis="Z", angle=8, clones=3)
        udp = self.aedtapp.modeler.Position(5, 5, 5)
        num_clones = 5
        assert not obj_udm.duplicate_along_line(udp, num_clones)

    @pytest.mark.skipif(config["desktopVersion"] > "2022.2", reason="Method failing in version higher than 2022.2")
    @pytest.mark.skipif(config["desktopVersion"] < "2023.1" and config["use_grpc"], reason="Not working in 2022.2 gRPC")
    def test_81_operations_3dcomponent(self):
        my_udmPairs = []
        mypair = ["OuterRadius", "20.2mm"]
        my_udmPairs.append(mypair)
        mypair = ["Tau", "0.65"]
        my_udmPairs.append(mypair)
        mypair = ["Sigma", "0.81"]
        my_udmPairs.append(mypair)
        mypair = ["Delta_Angle", "45deg"]
        my_udmPairs.append(mypair)
        mypair = ["Beta_Angle", "45deg"]
        my_udmPairs.append(mypair)
        mypair = ["Port_Gap_Width", "8.1mm"]
        my_udmPairs.append(mypair)
        self.aedtapp.modeler.create_udm(
            udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
            parameters=my_udmPairs,
            library="syslib",
            name="test_udm2",
        )
        assert self.aedtapp.modeler.duplicate_and_mirror(
            self.aedtapp.modeler.user_defined_component_names[0], [0, 0, 0], [1, 0, 0]
        )

    def test_83_cover_face(self):
        o1 = self.aedtapp.modeler.create_circle(cs_plane=0, position=[0, 0, 0], radius=10)
        assert self.aedtapp.modeler.cover_faces(o1)

    def test_84_replace_3d_component(self):
        self.aedtapp["test_variable"] = "20mm"
        box1 = self.aedtapp.modeler.create_box([0, 0, 0], [10, "test_variable", 30])
        box2 = self.aedtapp.modeler.create_box([0, 0, 0], ["test_variable", 100, 30])
        self.aedtapp.mesh.assign_length_mesh([box1.name, box2.name])
        obj_3dcomp = self.aedtapp.modeler.replace_3dcomponent(
            variables_to_include=["test_variable"], assignment=[box1.name]
        )
        assert isinstance(obj_3dcomp, UserDefinedComponent)

        self.aedtapp.modeler.replace_3dcomponent(name="new_comp", assignment=[box2.name])
        assert len(self.aedtapp.modeler.user_defined_components) == 2

    @pytest.mark.skipif(config["desktopVersion"] < "2023.1", reason="Method available in beta from 2023.1")
    @pytest.mark.skipif(is_linux, reason="EDB object is not loaded")
    def test_85_insert_layout_component(self):
        self.aedtapp.insert_design("LayoutComponent")
        self.aedtapp.solution_type = "Modal"
        assert not self.aedtapp.modeler.insert_layout_component(
            self.layout_component, name=None, parameter_mapping=False
        )
        self.aedtapp.solution_type = "Terminal"
        comp = self.aedtapp.modeler.insert_layout_component(self.layout_component, name=None, parameter_mapping=False)
        assert comp.layout_component.edb_object
        comp2 = self.aedtapp.modeler.insert_layout_component(
            self.layout_component_si_verse_sfp, name=None, parameter_mapping=False
        )
        assert comp2.layout_component.edb_object
        assert comp.layout_component.edb_object
        assert comp.name in self.aedtapp.modeler.layout_component_names
        assert isinstance(comp, UserDefinedComponent)
        assert len(self.aedtapp.modeler.user_defined_components[comp.name].parts) == 3
        assert comp.layout_component.edb_object
        comp3 = self.aedtapp.modeler.insert_layout_component(
            self.layout_component, name="new_layout", parameter_mapping=True
        )
        assert isinstance(comp3, UserDefinedComponent)
        assert len(comp3.parameters) == 2
        assert comp3.layout_component.show_layout
        comp3.layout_component.show_layout = False
        assert not comp3.layout_component.show_layout
        comp3.layout_component.show_layout = True
        comp3.layout_component.fast_transformation = True
        assert comp3.layout_component.fast_transformation
        comp3.layout_component.fast_transformation = False
        assert comp3.layout_component.show_dielectric
        comp3.layout_component.show_dielectric = False
        assert not comp3.layout_component.show_dielectric
        assert comp3.layout_component.display_mode == 0
        comp3.layout_component.display_mode = 1
        assert comp3.layout_component.display_mode == 1
        comp3.layout_component.layers["Trace"] = [True, True, 90]
        assert comp3.layout_component.update_visibility()
        assert comp.layout_component.close_edb_object()

    def test_insert_layout_component_2(self):
        self.aedtapp.insert_design("LayoutComponent")
        self.aedtapp.modeler.add_layout_component_definition(
            file_path=self.layout_component,
            name="ann",
        )
        self.aedtapp["b1"] = "3.2mm"
        self.aedtapp.modeler._insert_layout_component_instance(
            definition_name="ann", name=None, parameter_mapping={"a": "1.4mm", "b": "b1"}
        )
        self.aedtapp.modeler.add_layout_component_definition(
            file_path=self.layout_component_si_verse_sfp,
            name="SiVerse_SFP",
        )
        self.aedtapp.modeler._insert_layout_component_instance(
            name="PCB_A",
            definition_name="SiVerse_SFP",
        )
        self.aedtapp.modeler._insert_layout_component_instance(
            name="PCB_B", definition_name="SiVerse_SFP", import_coordinate_systems=["L8_1"]
        )

    def test_87_set_mesh_fusion_settings(self):
        self.aedtapp.insert_design("MeshFusionSettings")
        box1 = self.aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])
        obj_3dcomp = self.aedtapp.modeler.replace_3dcomponent(assignment=[box1.name])
        box2 = self.aedtapp.modeler.create_box([0, 0, 0], [100, 20, 30])
        obj2_3dcomp = self.aedtapp.modeler.replace_3dcomponent(assignment=[box2.name])
        assert self.aedtapp.set_mesh_fusion_settings(assignment=obj2_3dcomp.name, volume_padding=None, priority=None)

        assert self.aedtapp.set_mesh_fusion_settings(
            assignment=[obj_3dcomp.name, obj2_3dcomp.name, "Dummy"], volume_padding=None, priority=None
        )

        assert self.aedtapp.set_mesh_fusion_settings(
            assignment=[obj_3dcomp.name, obj2_3dcomp.name],
            volume_padding=[[0, 5, 0, 0, 0, 1], [0, 0, 0, 2, 0, 0]],
            priority=None,
        )
        with pytest.raises(ValueError, match="Volume padding length is different than component list length."):
            self.aedtapp.set_mesh_fusion_settings(
                assignment=[obj_3dcomp.name, obj2_3dcomp.name], volume_padding=[[0, 0, 0, 2, 0, 0]], priority=None
            )

        assert self.aedtapp.set_mesh_fusion_settings(
            assignment=[obj_3dcomp.name, obj2_3dcomp.name], volume_padding=None, priority=[obj2_3dcomp.name, "Dummy"]
        )

        assert self.aedtapp.set_mesh_fusion_settings(
            assignment=[obj_3dcomp.name, obj2_3dcomp.name],
            volume_padding=[[0, 5, 0, 0, 0, 1], [10, 0, 0, 2, 0, 0]],
            priority=[obj_3dcomp.name],
        )
        assert self.aedtapp.set_mesh_fusion_settings(assignment=None, volume_padding=None, priority=None)

    def test_88_import_primitives_file_json(self):
        self.aedtapp.insert_design("PrimitiveFromFile")
        primitive_file = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, primitive_json_file)
        primitive_names = self.aedtapp.modeler.import_primitives_from_file(input_file=primitive_file)
        assert len(primitive_names) == 9

    def test_89_import_cylinder_primitives_csv(self):
        self.aedtapp.insert_design("PrimitiveFromFile")
        primitive_file = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, cylinder_primitive_csv_file)
        primitive_names = self.aedtapp.modeler.import_primitives_from_file(input_file=primitive_file)
        assert len(primitive_names) == 2
        self.aedtapp.insert_design("PrimitiveFromFileTest")
        primitive_file = os.path.join(
            TESTS_GENERAL_PATH, "example_models", test_subfolder, cylinder_primitive_csv_file_wrong_keys
        )
        with pytest.raises(ValueError):
            self.aedtapp.modeler.import_primitives_from_file(input_file=primitive_file)
        primitive_file = os.path.join(
            TESTS_GENERAL_PATH, "example_models", test_subfolder, cylinder_primitive_csv_file_missing_values
        )
        with pytest.raises(ValueError):
            self.aedtapp.modeler.import_primitives_from_file(input_file=primitive_file)

    def test_90_import_prism_primitives_csv(self):
        self.aedtapp.insert_design("PrimitiveFromFile")
        primitive_file = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, prism_primitive_csv_file)
        primitive_names = self.aedtapp.modeler.import_primitives_from_file(input_file=primitive_file)
        assert len(primitive_names) == 2
        self.aedtapp.insert_design("PrimitiveFromFileTest")
        primitive_file = os.path.join(
            TESTS_GENERAL_PATH, "example_models", test_subfolder, prism_primitive_csv_file_wrong_keys
        )
        with pytest.raises(ValueError):
            self.aedtapp.modeler.import_primitives_from_file(input_file=primitive_file)
        primitive_file = os.path.join(
            TESTS_GENERAL_PATH, "example_models", test_subfolder, prism_primitive_csv_file_missing_values
        )
        with pytest.raises(ValueError):
            self.aedtapp.modeler.import_primitives_from_file(input_file=primitive_file)

    def test_91_primitives_builder(self, add_app):
        from ansys.aedt.core.generic.data_handlers import json_to_dict
        from ansys.aedt.core.modeler.cad.primitives import PrimitivesBuilder

        ipk = add_app(application=Icepak)

        primitive_file = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, primitive_json_file)
        primitive_dict = json_to_dict(primitive_file)

        with pytest.raises(TypeError):
            PrimitivesBuilder(ipk)

        del primitive_dict["Primitives"]
        with pytest.raises(AttributeError):
            PrimitivesBuilder(ipk, input_dict=primitive_dict)

        primitive_dict = json_to_dict(primitive_file)
        del primitive_dict["Coordinate Systems"][0]["Name"]
        primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
        assert not primitives_builder.create()

        primitive_dict = json_to_dict(primitive_file)
        del primitive_dict["Coordinate Systems"][0]["Mode"]
        primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
        assert not primitives_builder.create()

        primitive_dict = json_to_dict(primitive_file)
        del primitive_dict["Coordinate Systems"][0]["Origin"]
        del primitive_dict["Coordinate Systems"][0]["Y Point"]
        del primitive_dict["Coordinate Systems"][1]["Phi"]
        del primitive_dict["Coordinate Systems"][1]["Theta"]
        primitive_dict["Coordinate Systems"][1]["Mode"] = "Euler Angle ZXZ"
        primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
        del primitives_builder.coordinate_systems[0]["X Axis"]
        del primitives_builder.coordinate_systems[1]["Psi"]
        primitive_names = primitives_builder.create()
        assert len(primitive_names) == 9

        ipk.modeler.coordinate_systems[0].delete()
        ipk.modeler.coordinate_systems[0].delete()

        primitive_dict = json_to_dict(primitive_file)
        primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
        del primitives_builder.instances[0]["Name"]
        assert not primitives_builder.create()
        assert len(primitive_names) == 9

        primitive_dict = json_to_dict(primitive_file)
        primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
        del primitives_builder.instances[0]["Coordinate System"]
        primitive_names = primitives_builder.create()
        assert len(primitive_names) == 9
        ipk.modeler.coordinate_systems[0].delete()
        ipk.modeler.coordinate_systems[0].delete()

        primitive_dict = json_to_dict(primitive_file)
        primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
        primitives_builder.instances[0]["Coordinate System"] = "Invented"
        assert not primitives_builder.create()

        primitive_dict = json_to_dict(primitive_file)
        primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
        del primitives_builder.instances[0]["Origin"]
        primitive_names = primitives_builder.create()
        assert len(primitive_names) == 9

        q2d = add_app(application=Q2d)
        primitive_dict = json_to_dict(primitive_file)
        primitives_builder = PrimitivesBuilder(q2d, input_dict=primitive_dict)
        primitive_names = primitives_builder.create()
        assert all(element is None for element in primitive_names)

    def test_92_detach_faces(self):
        box = self.aedtapp.modeler.create_box([0, 0, 0], [1, 2, 3])
        out_obj = box.detach_faces(box.top_face_z)
        assert len(out_obj) == 2
        assert isinstance(out_obj[0], Object3d)
        box = self.aedtapp.modeler.create_box([0, 0, 0], [1, 2, 3])
        out_obj = box.detach_faces([box.top_face_z.id, box.bottom_face_z.id])
        assert len(out_obj) == 3
        assert all(isinstance(o, Object3d) for o in out_obj)

    @pytest.mark.skipif(config["desktopVersion"] < "2024.1", reason="Feature not available until 2024.1")
    @pytest.mark.skipif(config["desktopVersion"] < "2027.1", reason="Very long test skipping it.")
    def test_93_import_discovery(self):
        self.aedtapp.insert_design("DiscoImport")
        assert not self.aedtapp.modeler.objects
        assert not self.aedtapp.modeler.solid_bodies
        if is_linux:
            assert not self.aedtapp.modeler.import_discovery_model(self.discovery_file)
        else:
            assert self.aedtapp.modeler.import_discovery_model(self.discovery_file)
            assert self.aedtapp.modeler.objects
            assert self.aedtapp.modeler.solid_bodies

    def test_94_create_equationbased_surface(self):
        self.aedtapp.insert_design("Equations_surf")
        surf = self.aedtapp.modeler.create_equationbased_surface(
            x_uv="(sin(_v*2*pi)^2+1.2)*cos(_u*2*pi)", y_uv="(sin(_v*2*pi)^2+1.2)*sin(_u*2*pi)", z_uv="_v*2"
        )
        assert surf.name in self.aedtapp.modeler.sheet_names

    def test_95_update_geometry_property(self):
        self.aedtapp.insert_design("Update_properties")
        box1 = self.aedtapp.modeler.create_box([0, 0, 0], [1, 2, 3])
        box2 = self.aedtapp.modeler.create_box([10, 10, 10], [1, 2, 3])
        box1.display_wireframe = False
        box2.display_wireframe = False

        assert not self.aedtapp.modeler.update_geometry_property([box1.name], "wireframe", True)
        assert not self.aedtapp.modeler.update_geometry_property([box1.name], "material_name", "invented")
        assert not self.aedtapp.modeler.update_geometry_property([box1.name], "color", "red")

        self.aedtapp.modeler.update_geometry_property([box1.name], "display_wireframe", True)
        assert box1.display_wireframe

        self.aedtapp.modeler.update_geometry_property([box1.name, box2.name], "display_wireframe", True)
        assert box2.display_wireframe

        self.aedtapp.modeler.update_geometry_property([box1.name, box2.name], "material_name", "copper")
        assert box2.material_name == "copper"
        assert not box2.solve_inside

        self.aedtapp.modeler.update_geometry_property([box2.name], "solve_inside", True)
        assert box2.solve_inside
        assert not box1.solve_inside

        self.aedtapp.modeler.update_geometry_property([box1.name, box2.name], "color", (255, 255, 0))
        assert box2.color == box1.color == (255, 255, 0)

        self.aedtapp.modeler.update_geometry_property([box1.name, box2.name], "transparency", 0.75)
        assert box2.transparency == 0.75

        cs = self.aedtapp.modeler.create_coordinate_system()
        self.aedtapp.modeler.update_geometry_property([box2.name], "part_coordinate_system", cs.name)
        assert box2.part_coordinate_system == cs.name
        assert box1.part_coordinate_system == "Global"

        self.aedtapp.modeler.update_geometry_property([box1.name], "material_appearance", True)
        assert box1.material_appearance

        self.aedtapp.modeler.update_geometry_property([box1.name, box2.name], "material_appearance", True)
        assert box2.material_appearance

    def test_96_sweep_around_axis(self):
        circle1 = self.aedtapp.modeler.create_circle(
            orientation="Z", origin=[5, 0, 0], radius=2, num_sides=8, name="circle1"
        )
        circle2 = self.aedtapp.modeler.create_circle(
            orientation="Z", origin=[15, 0, 0], radius=2, num_sides=8, name="circle2"
        )
        circle3 = self.aedtapp.modeler.create_circle(
            orientation="Z", origin=[25, 0, 0], radius=2, num_sides=8, name="circle3"
        )

        assert self.aedtapp.modeler.sweep_around_axis(assignment=circle1, axis="Z")
        assert self.aedtapp.modeler.sweep_around_axis(assignment=[circle2, circle3], axis="Z")

        assert circle1.name in self.aedtapp.modeler.solid_names
        assert circle2.name in self.aedtapp.modeler.solid_names
        assert circle3.name in self.aedtapp.modeler.solid_names

    def test_97_uncover_faces(self):
        o1 = self.aedtapp.modeler.create_circle(cs_plane=0, position=[0, 0, 0], radius=10)
        assert self.aedtapp.modeler.uncover_faces([o1.faces[0]])
        c1 = self.aedtapp.modeler.create_circle(orientation=Axis.X, origin=[0, 10, 20], radius="3", name="Circle1")
        b1 = self.aedtapp.modeler.create_box(origin=[-13.9, 0, 0], sizes=[27.8, -40, 25.4], name="Box1")
        assert self.aedtapp.modeler.uncover_faces([c1.faces[0], b1.faces[0], b1.faces[2]])
        assert len(b1.faces) == 4
        c2 = self.aedtapp.modeler.create_circle(orientation=Axis.X, origin=[0, 10, 20], radius="3", name="Circle2")
        b2 = self.aedtapp.modeler.create_box(origin=[-13.9, 0, 0], sizes=[27.8, -40, 25.4], name="Box2")
        assert self.aedtapp.modeler.uncover_faces([c2.faces, b2.faces])
        c3 = self.aedtapp.modeler.create_circle(orientation=Axis.X, origin=[0, 10, 20], radius="3", name="Circle3")
        b3 = self.aedtapp.modeler.create_box(origin=[-13.9, 0, 0], sizes=[27.8, -40, 25.4], name="Box3")
        assert self.aedtapp.modeler.uncover_faces([c3.faces[0], b3.faces])
        assert len(b3.faces) == 0
