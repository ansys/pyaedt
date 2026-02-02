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

import os
import shutil

import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core import Q2d
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.components_3d import UserDefinedComponent
from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.cad.polylines import Polyline
from ansys.aedt.core.modeler.cad.primitives import PolylineSegment
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_CENTER
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_END
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_ORIGIN
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_RADIUS
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_SIZES_2
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_SIZES_3
from ansys.aedt.core.modeler.cad.primitives_3d import ERROR_MSG_START
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION
from tests.conftest import NON_GRAPHICAL
from tests.conftest import USE_GRPC

SDOC_FILE = "input.scdoc"
DISCOVERY_FILE = "input.dsco"
STEP = "input.stp"
COMPONENT_3D_FILE = "new.a3dcomp"
ENCRYPTED_CYL = "encrypted_cylinder.a3dcomp"
LAYOUT_COMP = "Layoutcomponent_231.aedbcomp"
LAYOUT_COMP_SI_VERSE_SFP = "ANSYS_SVP_V1_1_SFP_main.aedbcomp"
PRIMITIVES_FILE = "primitives_file.json"
CYLINDER_PRIMITIVE_FILE = "cylinder_geometry_creation.csv"
CYLINDER_PRIMITIVE_FILE_MISSING_VALUES = "cylinder_geometry_creation_missing_values.csv"
CYLINDER_PRIMITIVE_FILE_WRONG_KEYS = "cylinder_geometry_creation_wrong_keys.csv"
PRISM_PRIMITIVE_FILE = "prism_geometry_creation.csv"
PRISM_PRIMITIVE_FILE_MISSING_VALUES = "prism_geometry_creation_missing_values.csv"
PRISM_PRIMITIVE_FILE_WRONG_KEYS = "prism_geometry_creation_wrong_keys.csv"

TEST_SUBFOLDER = "T08"
POLYLINE_PROJECT = "polyline_231"

ON_CI = os.getenv("ON_CI", "false").lower() == "true"


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Hfss)
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


# Utils functions


def create_copper_box(app, name: str="MyBox"):
    """Create a copper box."""
    if app.modeler[name]:
        app.modeler.delete(name)
    new_object = app.modeler.create_box([0, 0, 0], [10, 10, 5], name, "Copper")
    return new_object


def create_copper_cylinder(app, name: str="MyCyl"):
    """Create a copper cylinder."""
    if app.modeler[name]:
        app.modeler.delete(name)
    new_object = app.modeler.create_cylinder(
        orientation="Y", origin=[20, 20, 0], radius=5, height=20, num_sides=8, name=name, material="Copper"
    )
    return new_object


def create_rectangle(app, name: str="MyRectangle"):
    """Create a rectangle."""
    if app.modeler[name]:
        app.modeler.delete(name)
    plane = Plane.XY
    new_object = app.modeler.create_rectangle(plane, [5, 3, 8], [4, 5], name=name)
    return new_object


def create_copper_torus(app, name: str="MyTorus"):
    """Create a copper torus."""
    if app.modeler[name]:
        app.modeler.delete(name)
    new_object = app.modeler.create_torus(
        [30, 30, 0], major_radius=1.2, minor_radius=0.5, axis="Z", name=name, material="Copper"
    )
    return new_object


def create_polylines(app, name: str="Poly_"):
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


def test_resolve_object(aedt_app) -> None:
    """Test resolve object."""
    box = create_copper_box(aedt_app)

    # Test with object
    resolve_object = aedt_app.modeler._resolve_object(box)
    assert isinstance(resolve_object, Object3d)
    assert resolve_object.id == box.id

    # Test with id
    resolve_object = aedt_app.modeler._resolve_object(box.id)
    assert isinstance(resolve_object, Object3d)
    assert resolve_object.id == box.id

    # Test with name
    resolve_object = aedt_app.modeler._resolve_object(box.name)
    assert isinstance(resolve_object, Object3d)
    assert resolve_object.id == box.id

    # Test invalid inputs
    invaloid_res = aedt_app.modeler._resolve_object(-1)
    assert invaloid_res is None
    invaloid_res = aedt_app.modeler._resolve_object("DummyInvalid")
    assert invaloid_res is None


def test_create_box(aedt_app) -> None:
    """Test create box."""
    box = create_copper_box(aedt_app, name="MyCreatedBox_11")

    assert box.id > 0
    assert box.name.startswith("MyCreatedBox_11")
    assert box.object_type == "Solid"
    assert box.is_3d
    assert box.material_name == "copper"
    assert "MyCreatedBox_11" in aedt_app.modeler.solid_names
    assert len(aedt_app.modeler.object_names) == len(aedt_app.modeler.objects)


def test_create_box_failure(aedt_app) -> None:
    """Test create box failure."""
    with pytest.raises(ValueError, match=ERROR_MSG_ORIGIN):
        aedt_app.modeler.create_box([0, 0], [10, 10, 10], "MyCreatedBox_12", "Copper")

    with pytest.raises(ValueError, match=ERROR_MSG_SIZES_3):
        aedt_app.modeler.create_box([0, 0, 0], [10, 10], "MyCreatedBox_12", "Copper")


def test_create_polyhedron_with_default_values(aedt_app) -> None:
    """Test create polyhedron with default values."""
    polyhedron = aedt_app.modeler.create_polyhedron()

    assert polyhedron.id > 0
    assert polyhedron.name.startswith("New")
    assert polyhedron.object_type == "Solid"
    assert polyhedron.is_3d
    assert polyhedron.material_name == "vacuum"
    assert polyhedron.solve_inside
    assert polyhedron.name in aedt_app.modeler.solid_names
    assert len(aedt_app.modeler.object_names) == len(aedt_app.modeler.objects)


def test_create_polyhedron_with_values(aedt_app) -> None:
    """Test create polyhedron with values."""
    polyhedron = aedt_app.modeler.create_polyhedron(
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
    assert polyhedron.name in aedt_app.modeler.solid_names
    assert len(aedt_app.modeler.object_names) == len(aedt_app.modeler.objects)


def test_create_polyhedron_failure(aedt_app) -> None:
    """Test create polyhedron failure."""
    with pytest.raises(ValueError, match=ERROR_MSG_CENTER):
        aedt_app.modeler.create_polyhedron(center=[0, 0])

    with pytest.raises(ValueError, match=ERROR_MSG_ORIGIN):
        aedt_app.modeler.create_polyhedron(origin=[0, 1])

    with pytest.raises(ValueError, match="The ``center`` and ``origin`` arguments must be different."):
        aedt_app.modeler.create_polyhedron(center=[0, 0, 0], origin=[0, 0, 0])


def test_center_and_centroid(aedt_app) -> None:
    """Test center and center from AEDT."""
    box = create_copper_box(aedt_app)
    tol = 1e-9

    assert GeometryOperators.v_norm(box.faces[0].center_from_aedt) - GeometryOperators.v_norm(box.faces[0].center) < tol


def test_position(aedt_app) -> None:
    """Test position."""
    assert aedt_app.modeler.Position([0])


def test_position_failure(aedt_app) -> None:
    """Test position failure."""
    with pytest.raises(IndexError):
        pos = aedt_app.modeler.Position(0, 0, 0)
        _ = pos[3]


def test_sweep_options(aedt_app) -> None:
    """Test sweep options."""
    assert aedt_app.modeler.SweepOptions()


def test_get_object_name_from_edge(aedt_app) -> None:
    """Test get object name from edge."""
    box = create_copper_box(aedt_app)

    edge = box.edges[0].id

    assert aedt_app.modeler.get_object_name_from_edge_id(edge) == box.name


def test_get_faces_from_materials(aedt_app) -> None:
    """Test get faces from materials."""
    create_copper_box(aedt_app)

    faces = aedt_app.modeler.get_faces_from_materials("Copper")

    assert len(faces) == len(set(faces))
    assert len(faces) == 6


def test_access_to_object_faces(aedt_app) -> None:
    """Test access to object faces."""
    box = create_copper_box(aedt_app)
    face_list = box.faces

    face = box.faces[0]

    assert len(face_list) == 6
    assert isinstance(face.center, list) and len(face.center) == 3
    assert isinstance(face.area, float) and face.area > 0
    assert box.faces[0].move_with_offset(0.1)
    assert box.faces[0].move_with_vector([0, 0, 0.01])
    assert isinstance(face.normal, list)


def test_check_object_edges(aedt_app) -> None:
    """Test access to object edges."""
    box = create_copper_box(aedt_app, name="MyBox")

    edge = box.edges[1]

    assert isinstance(edge.midpoint, list) and len(edge.midpoint) == 3
    assert isinstance(edge.length, float) and edge.length > 0


def test_check_object_vertices(aedt_app) -> None:
    """Test access to object vertices."""
    box = create_copper_box(aedt_app, name="MyBox")

    vertex = box.vertices[0]

    assert len(box.vertices) == 8
    assert isinstance(vertex.position, list) and len(vertex.position) == 3


def test_get_objects_in_group(aedt_app) -> None:
    """Test access to objects in group."""
    box = create_copper_box(aedt_app, name="MyBox")

    objs = aedt_app.modeler.get_objects_in_group("Solids")

    assert isinstance(objs, list)

    assert box.name in objs


def test_create_circle(aedt_app) -> None:
    """Test create circle."""
    origin = aedt_app.modeler.Position(5, 3, 8)

    circle = aedt_app.modeler.create_circle(Plane.XY, origin, 2, name="MyCircle", material="Copper")

    assert circle.id > 0
    assert circle.name.startswith("MyCircle")
    assert circle.object_type == "Sheet"
    assert not circle.is_3d
    assert not circle.solve_inside


def test_create_circle_failure(aedt_app) -> None:
    """Test create circle failures."""
    with pytest.raises(ValueError, match=ERROR_MSG_RADIUS):
        aedt_app.modeler.create_circle(Plane.XY, [10, 10, 10], -1)


def test_create_sphere(aedt_app) -> None:
    """Test create sphere."""
    origin = aedt_app.modeler.Position(20, 20, 0)
    radius = 5

    sphere = aedt_app.modeler.create_sphere(origin, radius, "MySphere", "Copper")

    assert sphere.id > 0
    assert sphere.name.startswith("MySphere")
    assert sphere.object_type == "Solid"
    assert sphere.is_3d


def test_create_sphere_failures(aedt_app) -> None:
    """Test create sphere failures."""
    with pytest.raises(ValueError, match=ERROR_MSG_ORIGIN):
        aedt_app.modeler.create_sphere([10, 10], 10)

    with pytest.raises(ValueError, match=ERROR_MSG_RADIUS):
        aedt_app.modeler.create_sphere([10, 10, 10], -5)


def test_create_cylinder(aedt_app) -> None:
    """Test create cylinder."""
    origin = aedt_app.modeler.Position(20, 20, 0)
    radius = 5
    height = 50

    cylinder = aedt_app.modeler.create_cylinder(Axis.Y, origin, radius, height, 8, "MyCyl", "Copper")

    assert cylinder.id > 0
    assert cylinder.name.startswith("MyCyl")
    assert cylinder.object_type == "Solid"
    assert cylinder.is_3d


def test_create_cylinder_failures(aedt_app) -> None:
    """Test create cylinder failures."""
    with pytest.raises(ValueError, match="The ``origin`` argument must be a valid three-element list."):
        aedt_app.modeler.create_cylinder(Axis.Y, [2, 2], 10, 10, 8)
    with pytest.raises(ValueError, match="The ``radius`` argument must be greater than 0."):
        aedt_app.modeler.create_cylinder(Axis.Y, [2, 2], -1, 10, 8)


def test_create_ellipse(aedt_app) -> None:
    """Test create ellipse."""
    origin = aedt_app.modeler.Position(5, 3, 8)

    ellipse = aedt_app.modeler.create_ellipse(Plane.XY, origin, 5, 1.5, True, name="MyEllipse", material="Copper")

    assert ellipse.id > 0
    assert ellipse.name.startswith("MyEllipse")
    assert ellipse.object_type == "Sheet"
    assert not ellipse.is_3d
    assert not ellipse.solve_inside


def test_create_ellipse_with_vacuum_without_name(aedt_app) -> None:
    """Test create ellipse with vacuum and without name."""
    origin = aedt_app.modeler.Position(5, 3, 8)

    ellipse = aedt_app.modeler.create_ellipse(Plane.XY, origin, 5, 1.5, True, material="Vacuum")

    assert ellipse.id > 0
    assert ellipse.object_type == "Sheet"
    assert not ellipse.is_3d
    assert not ellipse.solve_inside


def test_create_ellipse_uncovered(aedt_app) -> None:
    """Test create uncovered ellipse."""
    origin = aedt_app.modeler.Position(5, 3, 8)

    ellipse = aedt_app.modeler.create_ellipse(Plane.XY, origin, 5, 1.5, False)

    assert ellipse.id > 0
    assert ellipse.object_type == "Line"
    assert not ellipse.is_3d
    assert not ellipse.solve_inside


def test_create_object_from_edge(aedt_app) -> None:
    """Test create object from edge."""
    cylinder = create_copper_cylinder(aedt_app)
    edges = cylinder.edges

    line_obj = aedt_app.modeler.create_object_from_edge(edges[0])

    assert line_obj.id > 0
    assert line_obj.object_type == "Line"
    assert not line_obj.is_3d
    assert line_obj.is_model


def test_create_object_from_edge_with_multiple_edges(aedt_app) -> None:
    """Test create from edge with multiple edges."""
    cylinder_0 = create_copper_cylinder(aedt_app, "cyl_e1")
    cylinder_1 = create_copper_cylinder(aedt_app, "cyl_e2")

    edge_objects = aedt_app.modeler.create_object_from_edge(
        [cylinder_0.edges[0], cylinder_1.edges[1], cylinder_0.edges[1]]
    )

    assert edge_objects
    assert len(edge_objects) == 3


def test_create_object_on_edge_as_non_model(aedt_app) -> None:
    """Test create object from edge as non model."""
    cylinder = create_copper_cylinder(aedt_app)
    edge = aedt_app.modeler[cylinder.name].edges[0]

    line_obj = edge.create_object(non_model=True)

    assert line_obj.id > 0
    assert line_obj.object_type == "Line"
    assert not line_obj.is_3d
    assert line_obj.is_model is False


def test_create_object_from_face(aedt_app) -> None:
    """Test create object from face."""
    cylinder = create_copper_cylinder(aedt_app)
    faces = cylinder.faces

    sheet_obj = aedt_app.modeler.create_object_from_face(faces[0])

    assert sheet_obj.id > 0
    assert sheet_obj.object_type == "Sheet"
    assert not sheet_obj.is_3d


def test_create_object_from_multiple_faces(aedt_app) -> None:
    """Test create object from multiple faces."""
    cylinder_0 = create_copper_cylinder(aedt_app, "cyl_f1")
    cylinder_1 = create_copper_cylinder(aedt_app, "cyl_f2")

    face_objects = aedt_app.modeler.create_object_from_face(
        [cylinder_0.faces[0], cylinder_1.faces[1], cylinder_1.faces[1], cylinder_0.faces[2]]
    )

    assert face_objects
    assert len(face_objects) == 4


def test_create_object_on_face(aedt_app) -> None:
    """Test create object on face."""
    cylinder = create_copper_cylinder(aedt_app)

    sheet = aedt_app.modeler[cylinder.name].faces[0].create_object(non_model=True)

    assert sheet.id > 0
    assert sheet.object_type == "Sheet"
    assert not sheet.is_3d
    assert not sheet.is_model


def test_create_polyline_failure(aedt_app) -> None:
    """Test create polyline failure."""
    aedt_app["p1"] = "100mm"
    aedt_app["p2"] = "71mm"
    points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

    with pytest.raises(
        ValueError, match="The position_list argument must contain at least 4 points for segment of type Spline."
    ):
        aedt_app.modeler.create_polyline(points=points[0:3], segment_type="Spline", name="PL03_spline_str_3pt")


def test_create_polyline_with_cover_surface(aedt_app) -> None:
    """Test create polyline with cover surface."""
    position_0 = [0, 0, 0]
    position_1 = [5, 0, 0]
    position_2 = [5, 5, 0]
    position_3 = [2, 5, 3]
    arrofpos = [position_0, position_3, position_1, position_2, position_0]

    polyline = aedt_app.modeler.create_polyline(arrofpos, cover_surface=True, name="Poly1", material="Copper")

    assert isinstance(polyline, Polyline)
    assert isinstance(polyline, Object3d)
    assert polyline.object_type == "Sheet"
    assert not polyline.is_3d
    assert isinstance(polyline.color, tuple)
    assert isinstance(aedt_app.modeler["Poly1"], Object3d)


def test_create_polyline_with_non_model(aedt_app) -> None:
    """Test create polyline as non-model."""
    position_0 = [0, 0, 0]
    position_1 = [5, 0, 0]
    position_2 = [5, 5, 0]
    position_3 = [2, 5, 3]
    arrofpos = [position_0, position_3, position_1, position_2, position_0]

    polyline = aedt_app.modeler.create_polyline(
        arrofpos, cover_surface=False, name="Poly_nonmodel", material="Copper", non_model=True
    )

    assert isinstance(polyline, Polyline)
    assert isinstance(polyline, Object3d)
    assert not polyline.is_model
    assert polyline.object_type == "Line"
    assert not polyline.is_3d


def test_create_polyline_with_segment_type(aedt_app) -> None:
    """Test create polyline with segment type."""
    coordinates = [[0.4, 0, 0], [-0.4, -0.6, 0], [0.4, 0, 0]]
    segment_type = [
        PolylineSegment(segment_type="AngularArc", arc_center=[0, 0, 0], arc_angle="180deg", arc_plane="XY"),
        PolylineSegment(segment_type="Line"),
        PolylineSegment(segment_type="AngularArc", arc_center=[0, -0.6, 0], arc_angle="180deg", arc_plane="XY"),
        PolylineSegment(segment_type="Line"),
    ]

    polyline: Polyline = aedt_app.modeler.create_polyline(points=coordinates, segment_type=segment_type)

    assert isinstance(polyline, Polyline)
    assert isinstance(polyline, Object3d)
    assert polyline.is_model
    assert polyline.object_type == "Line"
    assert not polyline.is_3d


def test_create_polyline_with_crosssection(aedt_app) -> None:
    """Test create polyline with cross-section."""
    coordinates = [[0, 0, 0], [5, 0, 0], [5, 5, 0]]

    polyline = aedt_app.modeler.create_polyline(coordinates, name="Poly_xsection", xsection_type="Rectangle")

    assert isinstance(polyline, Polyline)
    assert aedt_app.modeler[polyline.id].object_type == "Solid"
    assert aedt_app.modeler[polyline.id].is3d


def test_sweep_along_path_with_single_assignment(aedt_app) -> None:
    """Test sweep along path with single assignment."""
    coordinates = [[0, 0, 0], [5, 0, 0], [5, 5, 0]]
    poyline = aedt_app.modeler.create_polyline(coordinates, name="poly_vector1")
    rectangle = aedt_app.modeler.create_rectangle(Plane.YZ, [0, -2, -4], [4, 3], name="rect_1")

    assert aedt_app.modeler.sweep_along_path(rectangle, poyline)
    assert rectangle.name in aedt_app.modeler.solid_names


def test_sweep_along_path_with_multiple_assignment(aedt_app) -> None:
    """Test sweep along path with multiple assignment."""
    coordinates = [[0, 0, 0], [5, 0, 0], [5, 5, 0]]
    polyline = aedt_app.modeler.create_polyline(coordinates, name="poly_vector1")
    rectangle_0 = aedt_app.modeler.create_rectangle(Plane.YZ, [0, -2, 2], [4, 3], name="rect_2")
    rectangle_1 = aedt_app.modeler.create_rectangle(Plane.YZ, [0, -2, 8], [4, 3], name="rect_3")

    assert aedt_app.modeler.sweep_along_path([rectangle_0, rectangle_1], polyline)
    assert rectangle_0.name in aedt_app.modeler.solid_names
    assert rectangle_1.name in aedt_app.modeler.solid_names


def test_sweep_along_vector_with_single_assignment(aedt_app) -> None:
    """Test sweep along vector method with single assignment."""
    rectangle = aedt_app.modeler.create_rectangle(Plane.YZ, [0, -2, -2], [4, 3], name="rect_1")

    assert aedt_app.modeler.sweep_along_vector(rectangle, [10, 20, 20])
    assert rectangle.name in aedt_app.modeler.solid_names


def test_sweep_along_vector_with_multiple_assignment(aedt_app) -> None:
    """Test sweep along vector method with multiple assignment."""
    rectangle_0 = aedt_app.modeler.create_rectangle(Plane.YZ, [0, -2, 2], [4, 3], name="rect_2")
    rectangle_1 = aedt_app.modeler.create_rectangle(Plane.YZ, [0, -2, 4], [4, 3], name="rect_3")

    assert aedt_app.modeler.sweep_along_vector([rectangle_0, rectangle_1], [10, 20, 20])
    assert rectangle_0.name in aedt_app.modeler.solid_names
    assert rectangle_1.name in aedt_app.modeler.solid_names


def test_create_rectangle(aedt_app) -> None:
    """Test create rectangle."""
    origin = aedt_app.modeler.Position(5, 3, 8)

    rectangle = aedt_app.modeler.create_rectangle(Plane.XY, origin, [4, 5], name="MyRectangle", material="Copper")

    assert rectangle.id > 0
    assert rectangle.name.startswith("MyRectangle")
    assert rectangle.object_type == "Sheet"
    assert not rectangle.is_3d


def test_create_rectangle_failure(aedt_app) -> None:
    """Test create rectangle failures."""
    origin = aedt_app.modeler.Position(5, 3, 8)

    with pytest.raises(ValueError, match=ERROR_MSG_SIZES_2):
        aedt_app.modeler.create_rectangle(Plane.XY, origin, [4, 5, 10], name="MyRectangle", material="Copper")


def test_create_cone(aedt_app) -> None:
    """Test create cone."""
    origin = aedt_app.modeler.Position(5, 3, 8)

    cone = aedt_app.modeler.create_cone(Axis.Z, origin, 20, 10, 5, name="MyCone", material="Copper")

    assert cone.id > 0
    assert cone.name.startswith("MyCone")
    assert cone.object_type == "Solid"
    assert cone.is_3d


def test_create_cone_failure(aedt_app) -> None:
    """Test create cone failures."""
    origin = aedt_app.modeler.Position(5, 3, 8)

    with pytest.raises(ValueError):
        aedt_app.modeler.create_cone(Axis.Z, [1, 1], 20, 10, 5, name="MyCone", material="Copper")
    with pytest.raises(ValueError):
        aedt_app.modeler.create_cone(Axis.Z, origin, -20, 20, 5, name="MyCone", material="Copper")
    with pytest.raises(ValueError):
        aedt_app.modeler.create_cone(Axis.Z, origin, 20, -20, 5, name="MyCone", material="Copper")
    with pytest.raises(ValueError):
        aedt_app.modeler.create_cone(Axis.Z, origin, 20, 20, -5, name="MyCone", material="Copper")


def test_get_object_id(aedt_app) -> None:
    """Test get object id."""
    rectangle = aedt_app.modeler.create_rectangle(Plane.XY, [5, 3, 8], [4, 5], name="MyRectangle5")

    assert aedt_app.modeler.get_obj_id(rectangle.name) == rectangle.id


def test_get_solid_objects(aedt_app) -> None:
    """Test solid objects retrieval and properties."""
    box = create_copper_box(aedt_app)
    solid_list = aedt_app.modeler.solid_names
    solid_obj = aedt_app.modeler[box.name]
    all_objects_list = aedt_app.modeler.object_names

    assert box.name in solid_list
    assert box.name in all_objects_list
    assert solid_obj.is_3d
    assert solid_obj.object_type == "Solid"


def test_get_sheet_objects(aedt_app) -> None:
    """Test sheet objects retrieval and properties."""
    rectangle = create_rectangle(aedt_app)
    sheet_list = aedt_app.modeler.sheet_names
    sheet_obj = aedt_app.modeler[rectangle.name]
    all_objects_list = aedt_app.modeler.object_names

    assert rectangle.name in sheet_list
    assert rectangle.name in all_objects_list
    assert not sheet_obj.is_3d
    assert sheet_obj.object_type == "Sheet"


def test_get_line_objects(aedt_app) -> None:
    """Test line objects retrieval and properties."""
    polyline_0, polyline_1, _ = create_polylines(aedt_app)
    line_list = aedt_app.modeler.line_names
    line_obj_0 = aedt_app.modeler[polyline_0.name]
    line_obj_1 = aedt_app.modeler[polyline_1.name]
    all_objects_list = aedt_app.modeler.object_names

    assert polyline_0.name in line_list
    assert polyline_0.name in all_objects_list
    assert polyline_1.name in line_list
    assert polyline_1.name in all_objects_list
    assert not line_obj_0.is_3d
    assert line_obj_0.object_type == "Line"
    assert not line_obj_1.is_3d
    assert line_obj_1.object_type == "Line"


def test_object_count_consistency(aedt_app) -> None:
    """Test that total object count is consistent across all lists."""
    # Create objects of all types
    polyline_0, polyline_1, _ = create_polylines(aedt_app)
    box = create_copper_box(aedt_app)
    rectangle = create_rectangle(aedt_app)

    # Get all lists
    solid_list = aedt_app.modeler.solid_names
    sheet_list = aedt_app.modeler.sheet_names
    line_list = aedt_app.modeler.line_names
    all_objects_list = aedt_app.modeler.object_names

    # Test count consistency
    assert len(all_objects_list) == len(solid_list) + len(line_list) + len(sheet_list)

    # Test all our objects are present
    created_objects = [box.name, rectangle.name, polyline_0.name, polyline_1.name]
    assert all(map(lambda obj: obj in all_objects_list, created_objects))


def test_get_object_by_material(aedt_app) -> None:
    """Test get objects by material."""
    _ = create_copper_box(aedt_app)

    copper_objects = aedt_app.modeler.get_objects_by_material("copper")
    fr4_objects = aedt_app.modeler.get_objects_by_material("FR4")
    lists_objects = aedt_app.modeler.get_objects_by_material()

    assert len(copper_objects) > 0
    assert len(fr4_objects) == 0
    assert set(aedt_app.materials.conductors).issubset([mat for sublist in lists_objects for mat in sublist])
    assert set(aedt_app.materials.dielectrics).issubset([mat for sublist in lists_objects for mat in sublist])


def test_get_edges_from_position(aedt_app) -> None:
    """Test get edges from position."""
    _ = create_rectangle(aedt_app, name="MyRectangle_for_primitives")
    origin = aedt_app.modeler.Position(5, 3, 8)

    edge_id = aedt_app.modeler.get_edgeid_from_position(origin)
    assert edge_id > 0


def test_get_edges_from_position_with_assignment(aedt_app) -> None:
    """Test get edges from position with assignment."""
    rectangle = create_rectangle(aedt_app, name="MyRectangle_for_primitives")
    origin = aedt_app.modeler.Position(5, 3, 8)

    edge_id = aedt_app.modeler.get_edgeid_from_position(origin, rectangle.name)
    assert edge_id > 0


# TODO: This test and others should be moved to a different file focusing on primitive operations (not 3D)
def test_get_faces_from_position_with_list_object(aedt_app) -> None:
    """Test get faces from position with list object."""
    _ = create_rectangle(aedt_app, name="New_Rectangle1")

    edge_id = aedt_app.modeler.get_faceid_from_position([5, 3, 8], "New_Rectangle1")

    assert edge_id > 0


def test_get_faces_from_position_with_position_object(aedt_app) -> None:
    """Test get faces from position with position object."""
    _ = create_rectangle(aedt_app)
    position = aedt_app.modeler.Position(100, 100, 100)

    edge_id = aedt_app.modeler.get_faceid_from_position(position)

    assert not edge_id


def test_delete_object(aedt_app) -> None:
    """Test delete object."""
    _ = create_rectangle(aedt_app, name="MyRectangle")
    assert "MyRectangle" in aedt_app.modeler.object_names

    deleted = aedt_app.modeler.delete("MyRectangle")

    assert deleted
    assert "MyRectangle" not in aedt_app.modeler.object_names


def test_get_face_vertices(aedt_app) -> None:
    """Test get face vertices."""
    rectangle = aedt_app.modeler.create_rectangle(Plane.XY, [1, 2, 3], [7, 13])
    faces = aedt_app.modeler.get_object_faces(rectangle.name)

    vertices = aedt_app.modeler.get_face_vertices(faces[0])

    assert len(vertices) == 4


def test_get_edge_vertices(aedt_app) -> None:
    """Test get edge vertices."""
    rectangle = aedt_app.modeler.create_rectangle(Plane.XY, [1, 2, 3], [7, 13])
    listedges = aedt_app.modeler.get_object_edges(rectangle.name)

    vertices = aedt_app.modeler.get_edge_vertices(listedges[0])

    assert len(vertices) == 2


def test_get_vertex_position(aedt_app) -> None:
    """Test get vertex position."""
    rectangle = aedt_app.modeler.create_rectangle(Plane.XY, [1, 2, 3], [7, 13])
    edges = aedt_app.modeler.get_object_edges(rectangle.name)
    vertices = aedt_app.modeler.get_edge_vertices(edges[0])

    pos_0 = aedt_app.modeler.get_vertex_position(vertices[0])
    pos_1 = aedt_app.modeler.get_vertex_position(vertices[1])
    edge_length = ((pos_0[0] - pos_1[0]) ** 2 + (pos_0[1] - pos_1[1]) ** 2 + (pos_0[2] - pos_1[2]) ** 2) ** 0.5

    assert len(pos_0) == 3
    assert len(pos_1) == 3
    assert edge_length == 7


def test_get_face_area(aedt_app) -> None:
    """Test get face area."""
    rectangle = aedt_app.modeler.create_rectangle(Plane.XY, [1, 2, 3], [7, 13])
    listfaces = aedt_app.modeler.get_object_faces(rectangle.name)

    area = aedt_app.modeler.get_face_area(listfaces[0])

    assert area == 7 * 13


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1" and USE_GRPC, reason="Not working in 2022.2 gRPC")
def test_get_face_center(aedt_app) -> None:
    """Test get face center."""
    rectangle = aedt_app.modeler.create_rectangle(
        Plane.XY,
        [1, 2, 3],
        [7, 13],
    )
    faces = aedt_app.modeler.get_object_faces(rectangle.name)
    center = aedt_app.modeler.get_face_center(faces[0])

    assert center == [4.5, 8.5, 3.0]


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1" and USE_GRPC, reason="Not working in 2022.2 gRPC")
def test_get_face_center_through_property(aedt_app) -> None:
    """Test get face center through property."""
    cylinder = aedt_app.modeler.create_cylinder(orientation=1, origin=[0, 0, 0], radius=10, height=10)
    if DESKTOP_VERSION >= "2023.1":
        centers = [[0, 10, 0], [0, 0, 0], [0, 5, 10]]
    else:
        centers = [[0, 0, 0], [0, 10, 0], [0, 5, 0]]

    cyl_centers = [face.center for face in cylinder.faces]

    for c0, c1 in zip(centers, cyl_centers):
        assert GeometryOperators.points_distance(c0, c1) < 1e-10


def test_get_edge_midpoint(aedt_app) -> None:
    """Test get edge midpoint."""
    polyline = aedt_app.modeler.create_polyline([[0, 0, 0], [10, 5, 3]])

    point = aedt_app.modeler.get_edge_midpoint(polyline.id)

    assert point == [5.0, 2.5, 1.5]


def test_get_bodynames_from_position(aedt_app) -> None:
    """Test get body names from position"""
    origin = [20, 20, 0]
    sphere = aedt_app.modeler.create_sphere(origin, 1, "fred")
    rectangle = aedt_app.modeler.create_rectangle(Plane.XY, [-50, -50, -50], [2, 2], name="bob")
    position_0 = aedt_app.modeler.Position(-23, -23, 13)
    position_1 = aedt_app.modeler.Position(-27, -27, 11)
    position_2 = aedt_app.modeler.Position(-31, -31, 7)
    position_3 = aedt_app.modeler.Position(2, 5, 3)
    positions = [position_0, position_1, position_2, position_3]
    polyline = aedt_app.modeler.create_polyline(positions, cover_surface=False, name="bill")

    names_0 = aedt_app.modeler.get_bodynames_from_position(origin)
    names_1 = aedt_app.modeler.get_bodynames_from_position([-49.0, -49.0, -50.0])
    names_2 = aedt_app.modeler.get_bodynames_from_position([-27, -27, 11])

    assert sphere.name in names_0
    assert rectangle.name in names_1
    assert polyline.name in names_2


def test_get_objects_with_strings(aedt_app) -> None:
    """Test get objects with strings."""
    origin = aedt_app.modeler.Position(5, 3, 8)
    _ = aedt_app.modeler.create_cone(Axis.Z, origin, 20, 10, 5, name="MyCustomCone", material="Copper")

    objs_0 = aedt_app.modeler.get_objects_w_string("MyCustomCone")
    objs_1 = aedt_app.modeler.get_objects_w_string("mycustom", False)
    objs_2 = aedt_app.modeler.get_objects_w_string("mycustom")

    assert len(objs_0) > 0
    assert len(objs_1) > 0
    assert len(objs_2) == 0


def test_get_model_objects(aedt_app) -> None:
    """Test get model objects consistency."""
    cylinder = create_copper_cylinder(aedt_app)
    edge = aedt_app.modeler[cylinder.name].edges[0]
    _ = edge.create_object(non_model=True)
    _ = edge.create_object(non_model=False)

    model_objects_names = aedt_app.modeler.model_objects
    non_model_objects_names = aedt_app.modeler.non_model_objects
    names = aedt_app.modeler.object_names

    assert set(model_objects_names).isdisjoint(set(non_model_objects_names))
    assert set(model_objects_names).union(set(non_model_objects_names)) == set(names)


def test_create_rect_sheet_to_ground_with_ground_name(aedt_app) -> None:
    """Test create rectangle sheet to ground."""
    create_copper_box(aedt_app, name="MyBox_to_gnd")

    ground_plane = aedt_app.modeler.create_sheet_to_ground("MyBox_to_gnd")

    assert isinstance(ground_plane, Object3d)
    assert ground_plane.id > 0


def test_create_rect_sheet_to_ground_with_multiple_arguments(aedt_app) -> None:
    """Test create rectangle sheet to ground with multiple arguments."""
    rect = create_rectangle(aedt_app)
    box = create_copper_box(aedt_app)

    ground_plane = aedt_app.modeler.create_sheet_to_ground(box.name, rect.name, aedt_app.axis_directions.ZNeg)

    assert isinstance(ground_plane, Object3d)
    assert ground_plane.id > 0


def test_get_edges_for_circuit_port(aedt_app) -> None:
    """Test get edges for circuit port."""
    aedt_app.modeler.model_units = "mm"

    # Create a port sheet and a ground box
    port_sheet = aedt_app.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="PortSheet")
    _ = aedt_app.modeler.create_box([0, 5, 0], [10, 2, -5], name="GroundBox")

    # Get the face ID of the port sheet
    port_face_id = port_sheet.faces[0].id

    # Call the method to find the edges
    edges = aedt_app.modeler.get_edges_for_circuit_port(port_face_id, yz_plane=False)

    # Assert the results
    assert isinstance(edges, list)
    assert len(edges) == 2
    assert all(isinstance(edge_id, int) for edge_id in edges)

    # Verify that new line objects have been created from the edges
    edge1_obj_name = aedt_app.modeler.get_object_name_from_edge_id(edges[0])
    edge2_obj_name = aedt_app.modeler.get_object_name_from_edge_id(edges[1])
    assert edge1_obj_name in aedt_app.modeler.object_names
    assert edge2_obj_name in aedt_app.modeler.object_names


def test_get_edges_for_circuit_port_from_sheet(aedt_app) -> None:
    """Test get edges for circuit port from sheet."""
    aedt_app.modeler.model_units = "mm"
    # Create a port sheet and a ground box
    port_sheet = aedt_app.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="PortSheet")
    _ = aedt_app.modeler.create_box([0, 5, 0], [10, 2, -5], name="GroundBox")

    # Call the method to find the edges
    edges = aedt_app.modeler.get_edges_for_circuit_port_from_sheet(port_sheet.name, yz_plane=False)

    # Assert the results
    assert isinstance(edges, list)
    assert len(edges) == 2

    # Verify that new line objects have been created from the edges
    edge1_obj_name = aedt_app.modeler.get_object_name_from_edge_id(edges[0])
    edge2_obj_name = aedt_app.modeler.get_object_name_from_edge_id(edges[1])
    assert edge1_obj_name in aedt_app.modeler.object_names
    assert edge2_obj_name in aedt_app.modeler.object_names


def test_fillet_and_undo(aedt_app) -> None:
    """Test fillet and undo."""
    box = create_copper_box(aedt_app, name="MyBox")

    res = box.edges[0].fillet()

    assert res
    aedt_app._odesign.Undo()

    res = box.edges[0].fillet()

    assert res


def test_fillet_failure(aedt_app) -> None:
    """Test fillet failure."""
    rectangle = create_rectangle(aedt_app, name="MyRect")
    with pytest.raises(AEDTRuntimeError):
        rectangle.edges[0].fillet()


def test_fillet_with_edges(aedt_app) -> None:
    """Test fillet with edges."""
    box = create_copper_box(aedt_app, name="MyBox2")

    res = box.fillet(edges=box.edges)

    assert res


def test_create_circle_from_2_arc_segments(aedt_app) -> None:
    prim3D = aedt_app.modeler
    assert prim3D.create_polyline(
        points=[[34.1004, 14.1248, 0], [27.646, 16.7984, 0], [24.9725, 10.3439, 0], [31.4269, 7.6704, 0]],
        segment_type=["Arc", "Arc"],
        cover_surface=True,
        close_surface=True,
        name="Rotor_Subtract_25_0",
        material="vacuum",
    )


def test_compound_polylines_segments(aedt_app) -> None:
    prim3D = aedt_app.modeler
    aedt_app["p1"] = "100mm"
    aedt_app["p2"] = "71mm"
    test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

    assert prim3D.create_polyline(points=test_points, name="PL06_segmented_compound_line")
    assert prim3D.create_polyline(points=test_points, segment_type=["Line", "Arc"], name="PL05_compound_line_arc")
    assert prim3D.create_polyline(points=test_points, close_surface=True, name="PL07_segmented_compound_line_closed")
    assert prim3D.create_polyline(points=test_points, cover_surface=True, name="SPL01_segmented_compound_line")


def test_insert_polylines_segments_test1(aedt_app) -> None:
    aedt_app["p1"] = "100mm"
    aedt_app["p2"] = "71mm"
    test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]
    P = aedt_app.modeler.create_polyline(
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


def test_insert_polylines_segments_test2(aedt_app) -> None:
    prim3D = aedt_app.modeler
    aedt_app["p1"] = "100mm"
    aedt_app["p2"] = "71mm"
    test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

    P = prim3D.create_polyline(points=test_points, close_surface=False, name="PL08_segmented_compound_insert_arc")
    start_point = P.points[1]
    insert_point1 = ["-120mm", "-25mm", "0mm"]
    insert_point2 = [-115, -40, 0]

    P.insert_segment(points=[start_point, insert_point1, insert_point2], segment="Arc")


def test_modify_crossection(aedt_app) -> None:
    P = aedt_app.modeler.create_polyline(
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


def test_remove_vertex_from_polyline(aedt_app) -> None:
    _, _, test_points = create_polylines(aedt_app, "Poly_remove_")

    P = aedt_app.modeler["Poly_remove_segmented"]
    P.remove_point(test_points[2])
    # time.sleep(0.1)
    P1 = aedt_app.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
    P1.remove_point([0, 1, 2])
    # time.sleep(0.1)

    P2 = aedt_app.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
    P2.remove_point(["0mm", "1mm", "2mm"])
    # time.sleep(0.1)

    P3 = aedt_app.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 2, 5]])
    P3.remove_point(["3mm", "2mm", "5mm"])
    # time.sleep(0.1)

    P4 = aedt_app.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
    P4.remove_point(["0mm", "1mm", "2mm"], tolerance=1e-6)


def test_remove_edges_from_polyline(aedt_app) -> None:
    modeler = aedt_app.modeler
    P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
    P.remove_segments(assignment=0)
    assert P.points == [[0, 2, 3], [2, 1, 4]]
    assert len(P.segment_types) == 1
    assert P.name in aedt_app.modeler.line_names
    P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
    P.remove_segments(assignment=[0, 1])
    assert P.points == [[2, 1, 4], [3, 1, 6]]
    assert len(P.segment_types) == 1
    assert P.name in aedt_app.modeler.line_names
    P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
    P.remove_segments(assignment=1)
    assert P.points == [[0, 1, 2], [2, 1, 4], [3, 1, 6]]
    assert len(P.segment_types) == 2
    assert P.name in aedt_app.modeler.line_names
    P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [2, 2, 5], [3, 1, 6]])
    P.remove_segments(assignment=[1, 3])
    assert P.points == [[0, 1, 2], [2, 1, 4], [2, 2, 5]]
    assert len(P.segment_types) == 2
    assert P.name in aedt_app.modeler.line_names
    P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
    P.remove_segments(assignment=[1, 2])
    assert P.points == [[0, 1, 2], [0, 2, 3]]
    assert len(P.segment_types) == 1
    assert P.name in aedt_app.modeler.line_names
    P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
    P.remove_segments(assignment=2)
    assert P.points == [[0, 1, 2], [0, 2, 3], [2, 1, 4]]
    assert len(P.segment_types) == 2
    assert P.name in aedt_app.modeler.line_names


def test_remove_edges_from_polyline_invalid(aedt_app) -> None:
    P = aedt_app.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
    P.remove_segments(assignment=[0, 1])
    assert P.name not in aedt_app.modeler.line_names


def test_duplicate_polyline_and_manipulate(aedt_app) -> None:
    P1 = aedt_app.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
    P2 = P1.clone()
    assert P2.id != P1.id


def test_create_spiral_and_add_segments(aedt_app) -> None:
    aedt_app.insert_design("spiral_test")
    save_model_units = aedt_app.modeler.model_units
    aedt_app.modeler.model_units = "um"
    innerRadius = 20
    wireThickness_um = 1
    numberOfTurns = 5
    NumberOfFaces = 10

    ind = aedt_app.modeler.create_spiral(
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
    ind.insert_segment(position_lst, aedt_app.modeler.polyline_segment("Spline", num_points=5))
    assert len(ind.points) == 59
    assert len(ind.segment_types) == 53

    p19 = polyline_points[19]
    position_lst = [[-8, -21, 0], [-4, -18, 0], [-2, -22, 0], p19]
    ind.insert_segment(position_lst, aedt_app.modeler.polyline_segment("Spline", num_points=4))
    assert len(ind.points) == 62
    assert len(ind.segment_types) == 54

    pm4 = polyline_points[-4]
    position_lst = [pm4]
    ind.insert_segment(
        position_lst,
        aedt_app.modeler.polyline_segment("AngularArc", arc_center=[-28, 26, 0], arc_angle="225.9deg", arc_plane="XY"),
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

    aedt_app.modeler.model_units = save_model_units


def test_open_and_load_a_polyline(add_app_example) -> None:
    app = add_app_example(project=POLYLINE_PROJECT, subfolder=TEST_SUBFOLDER)

    poly1 = app.modeler["Inductor1"]
    poly2 = app.modeler["Polyline1"]
    poly3 = app.modeler["Polyline2"]

    p1 = poly1.points
    s1 = poly1.segment_types
    assert not p1
    assert not s1
    p2 = poly2.points
    s2 = poly2.segment_types
    assert len(p2) == 13
    assert len(s2) == 7
    p3 = poly3.points
    s3 = poly3.segment_types
    assert len(p3) == 3
    assert len(s3) == 1
    app.close_project(save=False)


def test_create_bond_wires(aedt_app) -> None:
    aedt_app["$Ox"] = 0
    aedt_app["$Oy"] = 0
    aedt_app["$Oz"] = 0
    aedt_app["$Endx"] = 10
    aedt_app["$Endy"] = 10
    aedt_app["$Endz"] = 2
    aedt_app["$bondHeight1"] = "0.15mm"
    aedt_app["$bondHeight2"] = "0mm"
    b0 = aedt_app.modeler.create_bondwire(
        [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, diameter=0.034, facets=8, name="jedec51", material="copper"
    )
    assert b0
    b1 = aedt_app.modeler.create_bondwire(
        [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, bond_type=1, diameter=0.034, name="jedec41", material="copper"
    )
    assert b1
    b2 = aedt_app.modeler.create_bondwire(
        [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, bond_type=2, diameter=0.034, name="low", material="copper"
    )
    assert b2
    b3 = aedt_app.modeler.create_bondwire(
        [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, bond_type=3, diameter=0.034, name="jedec41", material="copper"
    )
    assert not b3
    b4 = aedt_app.modeler.create_bondwire(
        (2, 2, 0), (0, 0, 0), h1=0.15, h2=0, bond_type=1, diameter=0.034, name="jedec41", material="copper"
    )
    assert b4
    b5 = aedt_app.modeler.create_bondwire(
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
    b6 = aedt_app.modeler.create_bondwire(
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
    with pytest.raises(ValueError, match=ERROR_MSG_START):
        aedt_app.modeler.create_bondwire(
            [0, 0], [10, 10, 2], h1=0.15, h2=0, diameter=0.034, facets=8, name="jedec51", material="copper"
        )
    with pytest.raises(ValueError, match=ERROR_MSG_END):
        aedt_app.modeler.create_bondwire(
            [0, 0, 0], [10, 10], h1=0.15, h2=0, diameter=0.034, facets=8, name="jedec51", material="copper"
        )


def test_create_group(aedt_app) -> None:
    assert aedt_app.modeler.create_group(["jedec51", "jedec41"], "mygroup")
    assert aedt_app.modeler.ungroup("mygroup")


def test_flatten_assembly(aedt_app) -> None:
    assert aedt_app.modeler.flatten_assembly()


def test_solving_volume(aedt_app) -> None:
    vol = aedt_app.modeler.get_solving_volume()
    assert float(vol) > 0


def test_lines(aedt_app) -> None:
    aedt_app.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]], close_surface=True)
    assert aedt_app.modeler.vertex_data_of_lines()


def test_get_edges_on_bounding_box(aedt_app) -> None:
    # The bounding box for these two rectangles will be [0, 0, 0, 13, 8, 0].
    # Edges on bounding box for Rect1 are on y=0 and x=0.
    # Edges on bounding box for Rect2 are on x=13 and y=8.
    # Total edges on bounding box: 4.
    # Colinear edges: None.
    rect1 = aedt_app.modeler.create_rectangle(Plane.XY, origin=[0, 0, 0], sizes=[10, 5], name="Rect1")
    rect2 = aedt_app.modeler.create_rectangle(Plane.XY, origin=[5, 5, 0], sizes=[8, 3], name="Rect2")

    # Test with return_colinear=False
    edges = aedt_app.modeler.get_edges_on_bounding_box([rect1, rect2], return_colinear=False)
    assert len(edges) == 4

    # Test with return_colinear=True (default)
    # No colinear edges are expected in this configuration.
    edges = aedt_app.modeler.get_edges_on_bounding_box([rect1, rect2], return_colinear=True)
    assert len(edges) == 0

    # Create a third rectangle that introduces colinear edges with Rect1.
    # The new bounding box will be [0, 0, 0, 13, 8, 0].
    # Rect3 has an edge from (0,5,0) to (0,8,0) which is on the bounding box (x=0).
    # This edge is colinear with the edge from Rect1 on x=0.
    rect3 = aedt_app.modeler.create_rectangle(Plane.XY, origin=[0, 5, 0], sizes=[5, 3], name="Rect3")
    edges = aedt_app.modeler.get_edges_on_bounding_box([rect1, rect2, rect3], return_colinear=True)
    assert len(edges) == 4

    # Test with a single object assignment
    edges = aedt_app.modeler.get_edges_on_bounding_box(rect1.name, return_colinear=False)
    assert len(edges) == 2

    # Test with objects that have no edges on the bounding box
    aedt_app.modeler.create_box(origin=[20, 20, 20], sizes=[5, 5, 5])
    rect4 = aedt_app.modeler.create_rectangle(Plane.XY, origin=[1, 1, 0], sizes=[1, 1], name="Rect4")
    edges = aedt_app.modeler.get_edges_on_bounding_box(rect4, return_colinear=False)
    assert len(edges) == 0


def test_get_closest_edge_to_position(aedt_app) -> None:
    create_copper_box(aedt_app, "test_closest_edge")
    assert isinstance(aedt_app.modeler.get_closest_edgeid_to_position([0.2, 0, 0]), int)


@pytest.mark.skipif(NON_GRAPHICAL or is_linux, reason="Not running in non-graphical mode or in Linux")
@pytest.mark.skipif(ON_CI, reason="Needs Workbench to run.")
def test_import_space_claim(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / SDOC_FILE
    input_file = shutil.copy2(file_original, test_tmp_dir / SDOC_FILE)

    assert aedt_app.modeler.import_spaceclaim_document(str(input_file))
    assert len(aedt_app.modeler.objects) == 1


def test_import_step(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / STEP
    input_file = shutil.copy2(file_original, test_tmp_dir / STEP)

    assert aedt_app.modeler.import_3d_cad(input_file)
    assert len(aedt_app.modeler.object_names) == 1


def test_create_3dcomponent(aedt_app, test_tmp_dir) -> None:
    box = create_copper_box(aedt_app)
    aedt_app.solution_type = "Modal"
    for i in list(aedt_app.modeler.objects.keys()):
        aedt_app.modeler.objects[i].material_name = "copper"

    input_file = test_tmp_dir / "new" / COMPONENT_3D_FILE

    # Folder doesn't exist. Cannot create component.
    assert not aedt_app.modeler.create_3dcomponent(str(input_file), create_folder=False)

    # By default, the new folder is created.
    assert aedt_app.modeler.create_3dcomponent(str(input_file))
    assert input_file.is_file()
    variables = aedt_app.get_component_variables(str(input_file))
    assert isinstance(variables, dict)
    new_obj = aedt_app.modeler.duplicate_along_line(box, [100, 0, 0])
    rad = aedt_app.assign_radiation_boundary_to_objects(box)
    obj1 = aedt_app.modeler[new_obj[1][0]]
    exc = aedt_app.wave_port(obj1.faces[0])
    aedt_app["test_variable"] = "20mm"
    box1 = aedt_app.modeler.create_box([0, 0, 0], [10, "test_variable", 30])
    box2 = aedt_app.modeler.create_box([0, 0, 0], [10, 100, 30])
    aedt_app.mesh.assign_length_mesh([box1.name, box2.name])

    input_file = test_tmp_dir / "new2" / COMPONENT_3D_FILE
    assert aedt_app.modeler.create_3dcomponent(
        str(input_file),
        variables_to_include=["test_variable"],
        assignment=[box.name, new_obj[1][0], box1.name, box2.name],
        boundaries=[rad.name],
        excitations=[exc.name],
        coordinate_systems="Global",
    )
    assert input_file.is_file()


def test_create_3d_component_encrypted(aedt_app, test_tmp_dir) -> None:
    create_copper_box(aedt_app)
    input_file = test_tmp_dir / COMPONENT_3D_FILE
    assert aedt_app.modeler.create_3dcomponent(
        str(input_file), coordinate_systems="Global", is_encrypted=True, password="password_test"
    )
    assert aedt_app.modeler.create_3dcomponent(
        str(input_file),
        coordinate_systems="Global",
        is_encrypted=True,
        password="password_test",
        hide_contents=["Solid"],
    )
    assert not aedt_app.modeler.create_3dcomponent(
        str(input_file),
        coordinate_systems="Global",
        is_encrypted=True,
        password="password_test",
        password_type="Invalid",
    )
    assert not aedt_app.modeler.create_3dcomponent(
        str(input_file),
        coordinate_systems="Global",
        is_encrypted=True,
        password="password_test",
        component_outline="Invalid",
    )


def test_create_equationbased_curve(aedt_app) -> None:
    aedt_app.insert_design("Equations")
    eq_line = aedt_app.modeler.create_equationbased_curve(x_t="_t", y_t="_t*2", num_points=0)
    assert len(eq_line.edges) == 1
    eq_segmented = aedt_app.modeler.create_equationbased_curve(x_t="_t", y_t="_t*2", num_points=5)
    assert len(eq_segmented.edges) == 4
    eq_xsection = aedt_app.modeler.create_equationbased_curve(x_t="_t", y_t="_t*2", xsection_type="Circle")
    assert eq_xsection.name in aedt_app.modeler.solid_names


def test_insert_3dcomponent(aedt_app) -> None:
    aedt_app.solution_type = "Modal"
    aedt_app["l_dipole"] = "13.5cm"
    compfile = aedt_app.components3d["Dipole_Antenna_DM"]
    geometryparams = aedt_app.get_component_variables("Dipole_Antenna_DM")
    geometryparams["dipole_length"] = "l_dipole"
    obj_3dcomp = aedt_app.modeler.insert_3d_component(compfile, geometryparams)
    assert isinstance(obj_3dcomp, UserDefinedComponent)


@pytest.mark.skipif(DESKTOP_VERSION > "2022.2", reason="Method failing in version higher than 2022.2")
@pytest.mark.skipif(USE_GRPC and DESKTOP_VERSION < "2023.1", reason="Failing in grpc")
def test_insert_encrypted_3dcomp(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / ENCRYPTED_CYL
    input_file = shutil.copy2(file_original, test_tmp_dir / ENCRYPTED_CYL)

    assert not aedt_app.modeler.insert_3d_component(str(input_file))
    # assert not aedt_app.modeler.insert_3d_component(encrypted_cylinder, password="dfgdg")
    assert aedt_app.modeler.insert_3d_component(str(input_file), password="test")


def test_group_components(aedt_app) -> None:
    aedt_app["l_dipole"] = "13.5cm"

    compfile = aedt_app.components3d["Dipole_Antenna_DM"]
    geometryparams = aedt_app.get_component_variables("Dipole_Antenna_DM")
    geometryparams["dipole_length"] = "l_dipole"
    obj_3dcomp1 = aedt_app.modeler.insert_3d_component(compfile, geometryparams)
    obj_3dcomp2 = aedt_app.modeler.insert_3d_component(compfile, geometryparams)
    assert (
        aedt_app.modeler.create_group(components=[obj_3dcomp1.name, obj_3dcomp2.name], group_name="test_group")
        == "test_group"
    )


def test_component_bounding_box(aedt_app) -> None:
    aedt_app["tau_variable"] = "0.65"
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
    aedt_app.modeler.create_udm(
        udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
        parameters=my_udmPairs,
        library="syslib",
        name="test_udm_83",
    )
    assert (
        GeometryOperators.v_norm(
            GeometryOperators.v_sub(
                aedt_app.modeler.user_defined_components["test_udm_83"].bounding_box,
                [-18.662366556727996, -20.2, 0.0, 18.662366556727996, 20.2, 0.0],
            )
        )
        < 1e-10
    )

    assert (
        GeometryOperators.v_norm(
            GeometryOperators.v_sub(
                aedt_app.modeler.user_defined_components["test_udm_83"].center,
                [0.0, 0.0, 0.0],
            )
        )
        < 1e-10
    )


def test_assign_material(aedt_app) -> None:
    box1 = aedt_app.modeler.create_box([60, 60, 60], [4, 5, 5])
    box2 = aedt_app.modeler.create_box([50, 50, 50], [2, 3, 4])
    cyl1 = aedt_app.modeler.create_cylinder(orientation="X", origin=[50, 0, 0], radius=1, height=20)
    cyl2 = aedt_app.modeler.create_cylinder(orientation="Z", origin=[0, 0, 50], radius=1, height=10)

    assert box1.solve_inside
    assert box2.solve_inside
    assert cyl1.solve_inside
    assert cyl2.solve_inside

    box3 = aedt_app.modeler.create_box([40, 40, 40], [6, 8, 9], material="pec")
    assert not box3.solve_inside

    objects_list = [box1, box2, cyl1, cyl2]
    aedt_app.assign_material(objects_list, "copper")
    assert aedt_app.modeler[box1].material_name == "copper"
    assert aedt_app.modeler[box2].material_name == "copper"
    assert aedt_app.modeler[cyl1].material_name == "copper"
    assert aedt_app.modeler[cyl2].material_name == "copper"

    obj_names_list = [box1.name, box2.name, cyl1.name, cyl2.name]
    aedt_app.assign_material(obj_names_list, "aluminum")
    assert aedt_app.modeler[box1].material_name == "aluminum"
    assert aedt_app.modeler[box2].material_name == "aluminum"
    assert aedt_app.modeler[cyl1].material_name == "aluminum"
    assert aedt_app.modeler[cyl2].material_name == "aluminum"


def test_cover_lines(aedt_app) -> None:
    P1 = aedt_app.modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]], close_surface=True)
    assert aedt_app.modeler.cover_lines(P1)


def test_create_torus(aedt_app) -> None:
    torus = create_copper_torus(aedt_app)
    assert torus.id > 0
    assert torus.name.startswith("MyTorus")
    assert torus.object_type == "Solid"
    assert torus.is3d is True


def test_create_torus_exceptions(aedt_app) -> None:
    assert aedt_app.modeler.create_torus(
        [30, 30, 0], major_radius=1.3, minor_radius=0.5, axis="Z", name="torus", material="Copper"
    )

    with pytest.raises(ValueError, match=ERROR_MSG_ORIGIN):
        aedt_app.modeler.create_torus(
            [30, 30], major_radius=1.3, minor_radius=0.5, axis="Z", name="torus", material="Copper"
        )


def test_create_point(aedt_app) -> None:
    name = "mypoint"
    if aedt_app.modeler[name]:
        aedt_app.modeler.delete(name)
    point = aedt_app.modeler.create_point([30, 30, 0], name)
    point.set_color("(143 175 158)")
    point2 = aedt_app.modeler.create_point([50, 30, 0], "mypoint2", "(100 100 100)")
    point.logger.info("Creation and testing of a point.")

    assert point.name == "mypoint"
    assert point.coordinate_system == "Global"
    assert point2.name == "mypoint2"
    assert point2.coordinate_system == "Global"

    assert aedt_app.modeler.points[point.name] == point
    assert aedt_app.modeler.points[point2.name] == point2

    # Delete the first point
    assert len(aedt_app.modeler.points) == 2
    aedt_app.modeler.points[point.name].delete()
    assert name not in aedt_app.modeler.points

    assert len(aedt_app.modeler.point_objects) == 1
    assert len(aedt_app.modeler.point_names) == 1
    assert aedt_app.modeler.point_objects[0].name == "mypoint2"


def test_create_plane(aedt_app) -> None:
    aedt_app.set_active_design("3D_Primitives")
    name = "my_plane"
    if aedt_app.modeler[name]:
        aedt_app.modeler.delete(name)
    plane = aedt_app.modeler.create_plane(name, "-0.7mm", "0.3mm", "0mm", "0.7mm", "-0.3mm", "0mm")
    assert name in aedt_app.modeler.planes
    plane.set_color("(143 75 158)")
    assert plane.name == name
    plane.name = "my_plane1"
    assert plane.name == "my_plane1"

    plane2 = aedt_app.modeler.create_plane(
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

    assert aedt_app.modeler.planes["my_plane1"].name == plane.name
    assert aedt_app.modeler.planes["my_plane2"].name == plane2.name

    # Delete the first plane
    if DESKTOP_VERSION < "2023.1":
        assert len(aedt_app.modeler.planes) == 2
    else:
        assert len(aedt_app.modeler.planes) == 5
    aedt_app.modeler.planes["my_plane1"].delete()
    assert name not in aedt_app.modeler.planes


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
def test_create_choke(aedt_app, filename) -> None:
    choke_file1 = TESTS_GENERAL_PATH / "example_models" / "choke_json_file" / filename

    resolve1 = aedt_app.modeler.create_choke(str(choke_file1))

    assert isinstance(resolve1, list)
    assert resolve1[0]
    assert isinstance(resolve1[1], Object3d)
    for i in range(2, len(resolve1)):
        assert isinstance(resolve1[i][0], Object3d)
        assert isinstance(resolve1[i][1], list)


def test_check_choke_values(aedt_app, test_tmp_dir) -> None:
    choke_file1_original = TESTS_GENERAL_PATH / "example_models" / "choke_json_file" / "choke_1winding_1Layer.json"
    choke_file1 = shutil.copy2(choke_file1_original, test_tmp_dir / "choke_1winding_1Layer.json")

    choke_file2_original = (
        TESTS_GENERAL_PATH / "example_models" / "choke_json_file" / "choke_2winding_1Layer_Common.json"
    )
    choke_file2 = shutil.copy2(choke_file2_original, test_tmp_dir / "choke_2winding_1Layer_Common.json")

    choke_file3_original = (
        TESTS_GENERAL_PATH / "example_models" / "choke_json_file" / "choke_2winding_2Layer_Linked_Differential.json"
    )
    choke_file3 = shutil.copy2(choke_file3_original, test_tmp_dir / "choke_2winding_2Layer_Linked_Differential.json")

    choke_file4_original = (
        TESTS_GENERAL_PATH / "example_models" / "choke_json_file" / "choke_3winding_3Layer_Separate.json"
    )
    choke_file4 = shutil.copy2(choke_file4_original, test_tmp_dir / "choke_3winding_3Layer_Separate.json")

    choke_file5_original = (
        TESTS_GENERAL_PATH / "example_models" / "choke_json_file" / "choke_4winding_3Layer_Linked.json"
    )
    choke_file5 = shutil.copy2(choke_file5_original, test_tmp_dir / "choke_4winding_3Layer_Linked.json")

    choke_file6_original = (
        TESTS_GENERAL_PATH / "example_models" / "choke_json_file" / "choke_1winding_3Layer_Linked.json"
    )
    choke_file6 = shutil.copy2(choke_file6_original, test_tmp_dir / "choke_1winding_3Layer_Linked.json")

    choke_file7_original = (
        TESTS_GENERAL_PATH / "example_models" / "choke_json_file" / "choke_2winding_2Layer_Common.json"
    )
    choke_file7 = shutil.copy2(choke_file7_original, test_tmp_dir / "choke_2winding_2Layer_Common.json")

    resolve1 = aedt_app.modeler.check_choke_values(str(choke_file1), create_another_file=False)
    resolve2 = aedt_app.modeler.check_choke_values(str(choke_file2), create_another_file=False)
    resolve3 = aedt_app.modeler.check_choke_values(str(choke_file3), create_another_file=False)
    resolve4 = aedt_app.modeler.check_choke_values(str(choke_file4), create_another_file=False)
    resolve5 = aedt_app.modeler.check_choke_values(str(choke_file5), create_another_file=False)
    resolve6 = aedt_app.modeler.check_choke_values(str(choke_file6), create_another_file=False)
    resolve7 = aedt_app.modeler.check_choke_values(str(choke_file7), create_another_file=False)

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


def test_make_winding(aedt_app) -> None:
    aedt_app.insert_design("Make_Windings")
    chamfer = aedt_app.modeler._make_winding_follow_chamfer(0.8, 1.1, 2, 1)
    winding_list = aedt_app.modeler._make_winding("Winding", "copper", 29.9, 52.1, 22.2, 22.2, 5, 15, chamfer, True)
    assert isinstance(winding_list, list)
    assert isinstance(winding_list[0], Object3d)
    assert isinstance(winding_list[1], list)


def test_make_double_linked_winding(aedt_app) -> None:
    chamfer = aedt_app.modeler._make_winding_follow_chamfer(0.8, 1.1, 2, 1)
    winding_list = aedt_app.modeler._make_double_linked_winding(
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


def test_make_triple_linked_winding(aedt_app) -> None:
    chamfer = aedt_app.modeler._make_winding_follow_chamfer(0.8, 1.1, 2, 1)
    winding_list = aedt_app.modeler._make_triple_linked_winding(
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


def test_make_winding_port_line(aedt_app) -> None:
    aedt_app.insert_design("Make_Winding_Port_Line")
    chamfer = aedt_app.modeler._make_winding_follow_chamfer(0.8, 1.1, 2, 1)

    # Test double winding - should have 4 occurrences of most negative Z value
    double_winding_list = aedt_app.modeler._make_double_winding(
        "Double_Winding", "copper", 17.525, 32.475, 14.95, 1.5, 2.699, 2.699, 20, 20, 0.8, chamfer, 1.1, True
    )

    # Test triple winding - should have 6 occurrences of most negative Z value
    triple_winding_list = aedt_app.modeler._make_triple_winding(
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


def test_check_value_type(aedt_app) -> None:
    aedt_app.insert_design("other_tests")
    resolve1, boolean1 = aedt_app.modeler._check_value_type(2, float, True, "SUCCESS", "SUCCESS")
    resolve2, boolean2 = aedt_app.modeler._check_value_type(1, int, True, "SUCCESS", "SUCCESS")
    resolve3, boolean3 = aedt_app.modeler._check_value_type(1.1, float, False, "SUCCESS", "SUCCESS")
    assert isinstance(resolve1, float)
    assert boolean1
    assert isinstance(resolve2, int)
    assert boolean2
    assert isinstance(resolve3, float)
    assert not boolean3


def test_create_helix(aedt_app) -> None:
    udp1 = [0, 0, 0]
    udp2 = [5, 0, 0]
    udp3 = [10, 5, 0]
    udp4 = [15, 3, 0]
    polyline = aedt_app.modeler.create_polyline([udp1, udp2, udp3, udp4], cover_surface=False, name="helix_polyline")

    helix_right_turn = aedt_app.modeler.create_helix(
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
    polyline_left = aedt_app.modeler.create_polyline(
        [udp1, udp2, udp3, udp4], cover_surface=False, name="helix_polyline_left"
    )

    assert aedt_app.modeler.create_helix(
        assignment=polyline_left.name,
        origin=[0, 0, 0],
        x_start_dir=1.0,
        y_start_dir=1.0,
        z_start_dir=1.0,
        right_hand=False,
    )

    with pytest.raises(ValueError):
        aedt_app.modeler.create_helix(
            assignment="", origin=[0, 0, 0], x_start_dir=1.0, y_start_dir=1.0, z_start_dir=1.0
        )

    with pytest.raises(ValueError, match=ERROR_MSG_ORIGIN):
        aedt_app.modeler.create_helix(
            assignment=polyline_left.name,
            origin=[0, 0],
            x_start_dir=1.0,
            y_start_dir=1.0,
            z_start_dir=1.0,
            right_hand=False,
        )


def test_get_touching_objects(aedt_app) -> None:
    box1 = aedt_app.modeler.create_box([-20, -20, -20], [1, 1, 1], material="copper")
    box2 = aedt_app.modeler.create_box([-20, -20, -19], [0.2, 0.2, 0.2], material="copper")
    assert box2.name in box1.touching_objects
    assert box2.name in box1.touching_conductors()
    assert box1.name in box2.touching_objects
    assert box2.name in box1.faces[0].touching_objects
    if DESKTOP_VERSION > "2022.2":
        assert box2.name not in box1.faces[3].touching_objects
    else:
        assert box2.name not in box1.faces[1].touching_objects
    assert box2.get_touching_faces(box1)


@pytest.mark.skipif(DESKTOP_VERSION > "2022.2", reason="Method failing in version higher than 2022.2")
@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Method failing 2022.2")
def test_3dcomponent_operations(aedt_app) -> None:
    aedt_app.solution_type = "Modal"
    aedt_app["l_dipole"] = "13.5cm"
    compfile = aedt_app.components3d["Dipole_Antenna_DM"]
    geometryparams = aedt_app.get_component_variables("Dipole_Antenna_DM")
    geometryparams["dipole_length"] = "l_dipole"
    obj_3dcomp = aedt_app.modeler.insert_3d_component(compfile, geometryparams)
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
    assert "Dipole_pyaedt" in aedt_app.modeler.user_defined_component_names
    assert aedt_app.modeler["Dipole_pyaedt"]
    assert obj_3dcomp.name == "Dipole_pyaedt"
    if DESKTOP_VERSION < "2023.1":
        assert obj_3dcomp.parameters["dipole_length"] == "l_dipole"
        aedt_app["l_dipole2"] = "15.5cm"
        obj_3dcomp.parameters["dipole_length"] = "l_dipole2"
        assert obj_3dcomp.parameters["dipole_length"] == "l_dipole2"
    cs = aedt_app.modeler.create_coordinate_system()
    obj_3dcomp.target_coordinate_system = cs.name
    assert obj_3dcomp.target_coordinate_system == cs.name
    obj_3dcomp.delete()
    aedt_app.save_project()
    aedt_app._project_dictionary = None
    assert "Dipole_pyaedt" not in aedt_app.modeler.user_defined_component_names
    udp = aedt_app.modeler.Position(0, 0, 0)
    udp2 = aedt_app.modeler.Position(30, 40, 40)
    aedt_app.modeler.set_working_coordinate_system("Global")
    obj_3dcomp = aedt_app.modeler["Dipole_Antenna2"]
    assert obj_3dcomp.mirror(udp, udp2)
    assert obj_3dcomp.rotate(axis="Y", angle=180)
    assert obj_3dcomp.move(udp2)

    new_comps = obj_3dcomp.duplicate_around_axis(axis="Z", angle=8, clones=3)
    assert new_comps[0] in aedt_app.modeler.user_defined_component_names

    udp = aedt_app.modeler.Position(5, 5, 5)
    num_clones = 5
    attached_clones = obj_3dcomp.duplicate_along_line(udp, num_clones)
    assert attached_clones[0] in aedt_app.modeler.user_defined_component_names

    attached_clones = obj_3dcomp.duplicate_along_line(aedt_app.modeler.Position(-5, -5, -5), 2, attach_object=True)
    assert attached_clones[0] in aedt_app.modeler.user_defined_component_names


@pytest.mark.skipif(DESKTOP_VERSION > "2022.2", reason="Method failing in version higher than 2022.2")
@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Method failing 2022.2")
def test_udm_operations(aedt_app) -> None:
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
    obj_udm = aedt_app.modeler.create_udm(
        udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
        parameters=my_udmPairs,
        library="syslib",
        name="test_udm",
    )
    assert isinstance(obj_udm, UserDefinedComponent)
    assert len(aedt_app.modeler.user_defined_component_names) == len(aedt_app.modeler.user_defined_components)
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
    assert "antenna_pyaedt" in aedt_app.modeler.user_defined_component_names
    obj_udm.name = "MyTorus"
    assert obj_udm.name == "antenna_pyaedt"
    assert obj_udm.parameters["OuterRadius"] == "20.2mm"
    obj_udm.parameters["OuterRadius"] = "21mm"
    assert obj_udm.parameters["OuterRadius"] == "21mm"
    cs = aedt_app.modeler.create_coordinate_system()
    obj_udm.target_coordinate_system = cs.name
    assert obj_udm.target_coordinate_system == cs.name
    obj_udm.delete()
    aedt_app.save_project()
    aedt_app._project_dictionary = None
    assert "antenna_pyaedt" not in aedt_app.modeler.user_defined_component_names
    udp = aedt_app.modeler.Position(0, 0, 0)
    udp2 = aedt_app.modeler.Position(30, 40, 40)
    obj_udm = aedt_app.modeler.create_udm(
        udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
        parameters=my_udmPairs,
        library="syslib",
        name="test_udm",
    )
    assert obj_udm.mirror(udp, udp2)
    assert obj_udm.rotate(axis="Y", angle=180)
    assert obj_udm.move(udp2)
    assert not obj_udm.duplicate_around_axis(axis="Z", angle=8, clones=3)
    udp = aedt_app.modeler.Position(5, 5, 5)
    num_clones = 5
    assert not obj_udm.duplicate_along_line(udp, num_clones)


@pytest.mark.skipif(DESKTOP_VERSION > "2022.2", reason="Method failing in version higher than 2022.2")
@pytest.mark.skipif(DESKTOP_VERSION < "2023.1" and USE_GRPC, reason="Not working in 2022.2 gRPC")
def test_operations_3dcomponent(aedt_app) -> None:
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
    aedt_app.modeler.create_udm(
        udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
        parameters=my_udmPairs,
        library="syslib",
        name="test_udm2",
    )
    assert aedt_app.modeler.duplicate_and_mirror(aedt_app.modeler.user_defined_component_names[0], [0, 0, 0], [1, 0, 0])


def test_cover_face(aedt_app) -> None:
    o1 = aedt_app.modeler.create_circle(orientation=0, origin=[0, 0, 0], radius=10)
    assert aedt_app.modeler.cover_faces(o1)


def test_replace_3d_component(aedt_app) -> None:
    aedt_app["test_variable"] = "20mm"
    box1 = aedt_app.modeler.create_box([0, 0, 0], [10, "test_variable", 30])
    box2 = aedt_app.modeler.create_box([0, 0, 0], ["test_variable", 100, 30])
    aedt_app.mesh.assign_length_mesh([box1.name, box2.name])
    obj_3dcomp = aedt_app.modeler.replace_3dcomponent(variables_to_include=["test_variable"], assignment=[box1.name])
    assert isinstance(obj_3dcomp, UserDefinedComponent)

    aedt_app.modeler.replace_3dcomponent(name="new_comp", assignment=[box2.name])
    assert len(aedt_app.modeler.user_defined_components) == 2


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Method available in beta from 2023.1")
@pytest.mark.skipif(is_linux, reason="EDB object is not loaded")
def test_insert_layout_component(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP
    input_file = shutil.copy2(file_original, test_tmp_dir / LAYOUT_COMP)

    file_original2 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP_SI_VERSE_SFP
    input_file2 = shutil.copy2(file_original2, test_tmp_dir / LAYOUT_COMP_SI_VERSE_SFP)

    aedt_app.solution_type = "Modal"

    assert not aedt_app.modeler.insert_layout_component(str(input_file), name=None, parameter_mapping=False)
    aedt_app.solution_type = "Terminal"
    comp = aedt_app.modeler.insert_layout_component(str(input_file), name=None, parameter_mapping=False)
    assert comp.layout_component.edb_object
    comp2 = aedt_app.modeler.insert_layout_component(str(input_file2), name=None, parameter_mapping=False)
    assert comp2.layout_component.edb_object
    assert comp.layout_component.edb_object
    assert comp.name in aedt_app.modeler.layout_component_names
    assert isinstance(comp, UserDefinedComponent)
    assert len(aedt_app.modeler.user_defined_components[comp.name].parts) == 3
    assert comp.layout_component.edb_object
    comp3 = aedt_app.modeler.insert_layout_component(str(input_file), name="new_layout", parameter_mapping=True)
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


def test_insert_layout_component_2(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP
    input_file = shutil.copy2(file_original, test_tmp_dir / LAYOUT_COMP)

    file_original2 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP_SI_VERSE_SFP
    input_file2 = shutil.copy2(file_original2, test_tmp_dir / LAYOUT_COMP_SI_VERSE_SFP)

    aedt_app.modeler.add_layout_component_definition(
        file_path=str(input_file),
        name="ann",
    )
    aedt_app["b1"] = "3.2mm"
    aedt_app.modeler._insert_layout_component_instance(
        definition_name="ann", name=None, parameter_mapping={"a": "1.4mm", "b": "b1"}
    )
    aedt_app.modeler.add_layout_component_definition(
        file_path=str(input_file2),
        name="SiVerse_SFP",
    )
    aedt_app.modeler._insert_layout_component_instance(
        name="PCB_A",
        definition_name="SiVerse_SFP",
    )
    aedt_app.modeler._insert_layout_component_instance(
        name="PCB_B", definition_name="SiVerse_SFP", import_coordinate_systems=["L8_1"]
    )


def test_set_mesh_fusion_settings(aedt_app) -> None:
    aedt_app.insert_design("MeshFusionSettings")
    box1 = aedt_app.modeler.create_box([0, 0, 0], [10, 20, 30])
    obj_3dcomp = aedt_app.modeler.replace_3dcomponent(assignment=[box1.name])
    box2 = aedt_app.modeler.create_box([0, 0, 0], [100, 20, 30])
    obj2_3dcomp = aedt_app.modeler.replace_3dcomponent(assignment=[box2.name])
    assert aedt_app.set_mesh_fusion_settings(assignment=obj2_3dcomp.name, volume_padding=None, priority=None)

    assert aedt_app.set_mesh_fusion_settings(
        assignment=[obj_3dcomp.name, obj2_3dcomp.name, "Dummy"], volume_padding=None, priority=None
    )

    assert aedt_app.set_mesh_fusion_settings(
        assignment=[obj_3dcomp.name, obj2_3dcomp.name],
        volume_padding=[[0, 5, 0, 0, 0, 1], [0, 0, 0, 2, 0, 0]],
        priority=None,
    )
    with pytest.raises(ValueError, match="Volume padding length is different than component list length."):
        aedt_app.set_mesh_fusion_settings(
            assignment=[obj_3dcomp.name, obj2_3dcomp.name], volume_padding=[[0, 0, 0, 2, 0, 0]], priority=None
        )

    assert aedt_app.set_mesh_fusion_settings(
        assignment=[obj_3dcomp.name, obj2_3dcomp.name], volume_padding=None, priority=[obj2_3dcomp.name, "Dummy"]
    )

    assert aedt_app.set_mesh_fusion_settings(
        assignment=[obj_3dcomp.name, obj2_3dcomp.name],
        volume_padding=[[0, 5, 0, 0, 0, 1], [10, 0, 0, 2, 0, 0]],
        priority=[obj_3dcomp.name],
    )
    assert aedt_app.set_mesh_fusion_settings(assignment=None, volume_padding=None, priority=None)


def test_import_primitives_file_json(aedt_app) -> None:
    aedt_app.insert_design("PrimitiveFromFile")
    primitive_file = os.path.join(TESTS_GENERAL_PATH, "example_models", TEST_SUBFOLDER, PRIMITIVES_FILE)
    primitive_names = aedt_app.modeler.import_primitives_from_file(input_file=primitive_file)
    assert len(primitive_names) == 9


def test_import_cylinder_primitives_csv(aedt_app) -> None:
    aedt_app.insert_design("PrimitiveFromFile")
    primitive_file = os.path.join(TESTS_GENERAL_PATH, "example_models", TEST_SUBFOLDER, CYLINDER_PRIMITIVE_FILE)
    primitive_names = aedt_app.modeler.import_primitives_from_file(input_file=primitive_file)
    assert len(primitive_names) == 2
    aedt_app.insert_design("PrimitiveFromFileTest")
    primitive_file = os.path.join(
        TESTS_GENERAL_PATH, "example_models", TEST_SUBFOLDER, CYLINDER_PRIMITIVE_FILE_WRONG_KEYS
    )
    with pytest.raises(ValueError):
        aedt_app.modeler.import_primitives_from_file(input_file=primitive_file)
    primitive_file = os.path.join(
        TESTS_GENERAL_PATH, "example_models", TEST_SUBFOLDER, CYLINDER_PRIMITIVE_FILE_MISSING_VALUES
    )
    with pytest.raises(ValueError):
        aedt_app.modeler.import_primitives_from_file(input_file=primitive_file)


def test_import_prism_primitives_csv(aedt_app) -> None:
    aedt_app.insert_design("PrimitiveFromFile")
    primitive_file = os.path.join(TESTS_GENERAL_PATH, "example_models", TEST_SUBFOLDER, PRISM_PRIMITIVE_FILE)
    primitive_names = aedt_app.modeler.import_primitives_from_file(input_file=primitive_file)
    assert len(primitive_names) == 2
    aedt_app.insert_design("PrimitiveFromFileTest")
    primitive_file = os.path.join(TESTS_GENERAL_PATH, "example_models", TEST_SUBFOLDER, PRISM_PRIMITIVE_FILE_WRONG_KEYS)
    with pytest.raises(ValueError):
        aedt_app.modeler.import_primitives_from_file(input_file=primitive_file)
    primitive_file = os.path.join(
        TESTS_GENERAL_PATH, "example_models", TEST_SUBFOLDER, PRISM_PRIMITIVE_FILE_MISSING_VALUES
    )
    with pytest.raises(ValueError):
        aedt_app.modeler.import_primitives_from_file(input_file=primitive_file)


def test_primitives_builder(add_app, test_tmp_dir) -> None:
    from ansys.aedt.core.generic.file_utils import read_json
    from ansys.aedt.core.modeler.cad.primitives import PrimitivesBuilder

    ipk = add_app(application=Icepak)

    primitive_file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / PRIMITIVES_FILE
    primitive_file = shutil.copy2(primitive_file_original, test_tmp_dir / PRIMITIVES_FILE)

    primitive_dict = read_json(primitive_file)

    with pytest.raises(TypeError):
        PrimitivesBuilder(ipk)

    del primitive_dict["Primitives"]
    with pytest.raises(AttributeError):
        PrimitivesBuilder(ipk, input_dict=primitive_dict)

    primitive_dict = read_json(primitive_file)
    del primitive_dict["Coordinate Systems"][0]["Name"]
    primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
    assert not primitives_builder.create()

    primitive_dict = read_json(primitive_file)
    del primitive_dict["Coordinate Systems"][0]["Mode"]
    primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
    assert not primitives_builder.create()

    primitive_dict = read_json(primitive_file)
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

    primitive_dict = read_json(primitive_file)
    primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
    del primitives_builder.instances[0]["Name"]
    assert not primitives_builder.create()
    assert len(primitive_names) == 9

    primitive_dict = read_json(primitive_file)
    primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
    del primitives_builder.instances[0]["Coordinate System"]
    primitive_names = primitives_builder.create()
    assert len(primitive_names) == 9
    ipk.modeler.coordinate_systems[0].delete()
    ipk.modeler.coordinate_systems[0].delete()

    primitive_dict = read_json(primitive_file)
    primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
    primitives_builder.instances[0]["Coordinate System"] = "Invented"
    assert not primitives_builder.create()

    primitive_dict = read_json(primitive_file)
    primitives_builder = PrimitivesBuilder(ipk, input_dict=primitive_dict)
    del primitives_builder.instances[0]["Origin"]
    primitive_names = primitives_builder.create()
    assert len(primitive_names) == 9

    q2d = add_app(application=Q2d, close_projects=False)
    primitive_dict = read_json(primitive_file)
    primitives_builder = PrimitivesBuilder(q2d, input_dict=primitive_dict)
    primitive_names = primitives_builder.create()
    assert all(element is None for element in primitive_names)
    q2d.close_project(save=False)


def test_detach_faces(aedt_app) -> None:
    box = aedt_app.modeler.create_box([0, 0, 0], [1, 2, 3])
    out_obj = box.detach_faces(box.top_face_z)
    assert len(out_obj) == 2
    assert isinstance(out_obj[0], Object3d)
    box = aedt_app.modeler.create_box([0, 0, 0], [1, 2, 3])
    out_obj = box.detach_faces([box.top_face_z.id, box.bottom_face_z.id])
    assert len(out_obj) == 3
    assert all(isinstance(o, Object3d) for o in out_obj)


@pytest.mark.skipif(DESKTOP_VERSION < "2024.1", reason="Feature not available until 2024.1")
@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Very long test skipping it.")
@pytest.mark.skipif(ON_CI, reason="Needs Workbench to run.")
def test_import_discovery(aedt_app, test_tmp_dir) -> None:
    assert not aedt_app.modeler.objects
    assert not aedt_app.modeler.solid_bodies

    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / DISCOVERY_FILE
    input_file = shutil.copy2(file_original, test_tmp_dir / DISCOVERY_FILE)

    if is_linux:
        assert not aedt_app.modeler.import_discovery_model(str(input_file))
    else:
        assert aedt_app.modeler.import_discovery_model(str(input_file))
        assert aedt_app.modeler.objects
        assert aedt_app.modeler.solid_bodies


def test_create_equationbased_surface(aedt_app) -> None:
    surf = aedt_app.modeler.create_equationbased_surface(
        x_uv="(sin(_v*2*pi)^2+1.2)*cos(_u*2*pi)", y_uv="(sin(_v*2*pi)^2+1.2)*sin(_u*2*pi)", z_uv="_v*2"
    )
    assert surf.name in aedt_app.modeler.sheet_names


def test_update_geometry_property(aedt_app) -> None:
    box1 = aedt_app.modeler.create_box([0, 0, 0], [1, 2, 3])
    box2 = aedt_app.modeler.create_box([10, 10, 10], [1, 2, 3])
    box1.display_wireframe = False
    box2.display_wireframe = False

    assert not aedt_app.modeler.update_geometry_property([box1.name], "wireframe", True)
    assert not aedt_app.modeler.update_geometry_property([box1.name], "material_name", "invented")
    assert not aedt_app.modeler.update_geometry_property([box1.name], "color", "red")

    aedt_app.modeler.update_geometry_property([box1.name], "display_wireframe", True)
    assert box1.display_wireframe

    aedt_app.modeler.update_geometry_property([box1.name, box2.name], "display_wireframe", True)
    assert box2.display_wireframe

    aedt_app.modeler.update_geometry_property([box1.name, box2.name], "material_name", "copper")
    assert box2.material_name == "copper"
    assert not box2.solve_inside

    aedt_app.modeler.update_geometry_property([box2.name], "solve_inside", True)
    assert box2.solve_inside
    assert not box1.solve_inside

    aedt_app.modeler.update_geometry_property([box1.name, box2.name], "color", (255, 255, 0))
    assert box2.color == box1.color == (255, 255, 0)

    aedt_app.modeler.update_geometry_property([box1.name, box2.name], "transparency", 0.75)
    assert box2.transparency == 0.75

    cs = aedt_app.modeler.create_coordinate_system()
    aedt_app.modeler.update_geometry_property([box2.name], "part_coordinate_system", cs.name)
    assert box2.part_coordinate_system == cs.name
    assert box1.part_coordinate_system == "Global"

    aedt_app.modeler.update_geometry_property([box1.name], "material_appearance", True)
    assert box1.material_appearance

    aedt_app.modeler.update_geometry_property([box1.name, box2.name], "material_appearance", True)
    assert box2.material_appearance


def test_sweep_around_axis(aedt_app) -> None:
    circle1 = aedt_app.modeler.create_circle(orientation="Z", origin=[5, 0, 0], radius=2, num_sides=8, name="circle1")
    circle2 = aedt_app.modeler.create_circle(orientation="Z", origin=[15, 0, 0], radius=2, num_sides=8, name="circle2")
    circle3 = aedt_app.modeler.create_circle(orientation="Z", origin=[25, 0, 0], radius=2, num_sides=8, name="circle3")

    assert aedt_app.modeler.sweep_around_axis(assignment=circle1, axis="Z")
    assert aedt_app.modeler.sweep_around_axis(assignment=[circle2, circle3], axis="Z")

    assert circle1.name in aedt_app.modeler.solid_names
    assert circle2.name in aedt_app.modeler.solid_names
    assert circle3.name in aedt_app.modeler.solid_names


def test_uncover_faces(aedt_app) -> None:
    o1 = aedt_app.modeler.create_circle(orientation=0, origin=[0, 0, 0], radius=10)
    assert aedt_app.modeler.uncover_faces([o1.faces[0]])
    c1 = aedt_app.modeler.create_circle(orientation=Axis.X, origin=[0, 10, 20], radius="3", name="Circle1")
    b1 = aedt_app.modeler.create_box(origin=[-13.9, 0, 0], sizes=[27.8, -40, 25.4], name="Box1")
    assert aedt_app.modeler.uncover_faces([c1.faces[0], b1.faces[0], b1.faces[2]])
    assert len(b1.faces) == 4
    c2 = aedt_app.modeler.create_circle(orientation=Axis.X, origin=[0, 10, 20], radius="3", name="Circle2")
    b2 = aedt_app.modeler.create_box(origin=[-13.9, 0, 0], sizes=[27.8, -40, 25.4], name="Box2")
    assert aedt_app.modeler.uncover_faces([c2.faces, b2.faces])
    c3 = aedt_app.modeler.create_circle(orientation=Axis.X, origin=[0, 10, 20], radius="3", name="Circle3")
    b3 = aedt_app.modeler.create_box(origin=[-13.9, 0, 0], sizes=[27.8, -40, 25.4], name="Box3")
    assert aedt_app.modeler.uncover_faces([c3.faces[0], b3.faces])
    assert len(b3.faces) == 0
