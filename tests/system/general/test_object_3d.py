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

import math

import pytest

from ansys.aedt.core.generic.file_utils import _uname
from ansys.aedt.core.generic.general_methods import _to_boolean
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.numbers_utils import is_close
from ansys.aedt.core.modeler.cad.elements_3d import EdgePrimitive
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive
from typing import Optional


@pytest.fixture
def aedt_app(add_app):
    app = add_app()
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


def create_example_coil(app, name: Optional[str]=None):
    if not name:
        name = "test_coil"
    RI = 10
    RO = 18
    HT = 9
    N = 1.5
    tetarad = 4 * math.pi / 180
    pointsList1 = [
        [RI * math.cos(tetarad), -RI * math.sin(tetarad), HT / 2 - N],
        [(RI + N) * math.cos(tetarad), -(RI + N) * math.sin(tetarad), HT / 2],
        [RO - N, 0, HT / 2],
        [RO, 0, HT / 2 - N],
        [RO, 0, -HT / 2 + N],
        [RO - N, 0, -HT / 2],
        [(RI + N) * math.cos(tetarad), (RI + N) * math.sin(tetarad), -HT / 2],
        [RI * math.cos(tetarad), RI * math.sin(tetarad), -HT / 2 + N],
        [RI * math.cos(tetarad), RI * math.sin(tetarad), HT / 2 - N],
        [(RI + N) * math.cos(tetarad), (RI + N) * math.sin(tetarad), HT / 2],
    ]
    if app.modeler[name]:
        app.modeler.delete(name)
    return app.modeler.create_polyline(points=pointsList1, name=name)


def create_copper_box(app, name: Optional[str]=None):
    if not name:
        name = "MyBox"
    box = app.modeler[name]
    if not box:
        box = app.modeler.create_box([0, 0, 0], [10, 10, 5], name, "Copper")
    return box


def create_copper_sphere(app, name: Optional[str]=None):
    if not name:
        name = "Mysphere"
    if app.modeler[name]:
        app.modeler.delete(name)
    return app.modeler.create_sphere([0, 0, 0], radius=4, name=name, material="Copper")


def create_copper_cylinder(app, name: Optional[str]=None):
    if not name:
        name = "MyCyl"
    if app.modeler[name]:
        app.modeler.delete(name)
    return app.modeler.create_cylinder(
        orientation="Y", origin=[0, 0, 0], radius=1, height=20, num_sides=8, name=name, material="Copper"
    )


def test_uname() -> None:
    test_name = _uname()
    assert test_name.startswith("NewObject")


def test_bounding_box_and_dimension(aedt_app) -> None:
    l1 = len(aedt_app.modeler.solid_objects)
    box = create_copper_box(aedt_app)
    assert len(aedt_app.modeler.solid_objects) == l1 + 1
    assert len(aedt_app.modeler.sheet_objects) == 0
    assert len(aedt_app.modeler.line_objects) == 0
    assert isinstance(box.color, tuple)
    bb = box.bounding_box
    assert len(bb) == 6
    bd = box.bounding_dimension
    assert len(bd) == 3


def test_delete_object(aedt_app) -> None:
    box = create_copper_box(aedt_app, "DeleteBox")
    name = box.name
    assert name in aedt_app.modeler.object_names
    box.delete()
    assert not aedt_app.modeler[name]
    assert not box.__dict__
    assert name not in aedt_app.modeler.object_names
    # 1 body and 1 sheet
    circle = aedt_app.modeler.create_circle(orientation=0, origin=[0, 0, 0], radius=5)
    name_circle = circle.name
    vacuum_box = aedt_app.modeler.create_box(origin=[0, 0, 0], sizes=[10, 10, 10], material="vacuum")
    name_vacuum_box = vacuum_box.name
    vacuum_box.delete()
    assert not aedt_app.modeler[name_vacuum_box]
    circle.delete()
    assert not aedt_app.modeler[name_circle]


def test_subtract_object(aedt_app) -> None:
    box = create_copper_box(aedt_app, "subtract_box")
    sphere = create_copper_sphere(aedt_app, "subtract_sphere")
    cylinder = create_copper_cylinder(aedt_app, "subtract_cylinder")
    box_2 = box.clone()
    box_2.subtract(sphere)
    box_3 = box.clone()
    box_3.subtract([sphere, cylinder])
    assert len(box_2.faces) == 7
    assert len(box_3.faces) == 9


def test_face_edge_vertex(aedt_app) -> None:
    box = create_copper_box(aedt_app, "faces_box")
    object_faces = box.faces
    assert len(object_faces) == 6
    for face in object_faces:
        assert len(face.edges) == 4
        assert len(face.normal) == 3
    object_edges = box.edges
    for edge in object_edges:
        assert len(edge.vertices) == 2
        assert len(edge.midpoint) == 3
    assert box.edges[0].segment_info
    object_vertices = box.vertices
    for vertex in object_vertices:
        assert len(vertex.position) == 3
    circle = aedt_app.modeler.create_circle("Z", [0, 0, 0], 2)
    assert len(circle.faces) == 1
    circle2 = aedt_app.modeler.create_circle("Z", [0, 0, 0], 2, non_model=True)
    assert not circle2.model


def test_face_primitive(aedt_app) -> None:
    box = create_copper_box(aedt_app, "PrimitiveBox")
    planar_face = box.faces[0]
    assert planar_face.center == [5.0, 5.0, 5.0]
    planar_face.move_with_offset(1)
    assert planar_face.center == [5.0, 5.0, 6.0]
    assert planar_face.normal == [0, 0, 1]
    assert is_close(planar_face.area, 100)
    assert planar_face.is_planar
    assert isinstance(box.largest_face()[0], FacePrimitive)
    assert isinstance(box.smallest_face(2), list)
    assert isinstance(box.longest_edge()[0], EdgePrimitive)
    assert isinstance(box.shortest_edge()[0], EdgePrimitive)
    sphere = create_copper_sphere(aedt_app, "PrimitiveSphere")
    non_planar_face = sphere.faces[0]
    assert is_close(non_planar_face.area, 201.06192982974676)
    assert non_planar_face.move_with_offset(1)
    assert is_close(non_planar_face.area, 314.1592653589793)
    assert not non_planar_face.normal
    assert not sphere.faces[0].is_planar
    box2 = aedt_app.modeler.create_box([300, 300, 300], [10, 10, 5], "BoxBounding", "Copper")
    for face in box2.faces:
        assert isinstance(face.is_on_bounding(), bool)
    assert len(box2.faces_on_bounding_box) == 3
    assert box2.face_closest_to_bounding_box.id in [i.id for i in box2.faces_on_bounding_box]


def test_object_material_property_invalid(aedt_app) -> None:
    box = create_copper_box(aedt_app, "Invalid1")
    box.material_name = "Copper1234Invalid"
    assert box.material_name == "copper"


def test_object_material_property_valid(aedt_app) -> None:
    box = create_copper_box(aedt_app, "Valid2")
    box.material_name = "aluminum"
    assert box.material_name == "aluminum"


def test_material_name_setter(aedt_app) -> None:
    box = create_copper_box(aedt_app)
    aedt_app.materials.add_material("myMat")
    aedt_app.materials.add_material("myMat2")
    aedt_app["mat_sweep_test"] = '["myMat", "myMat2"]'
    box.material_name = "mat_sweep_test[0]"
    assert aedt_app.modeler.get_objects_by_material(material="myMat")[0].name == "MyBox"


def test_object3d_properties_transparency(aedt_app) -> None:
    box = create_copper_box(aedt_app, "TransparencyBox")
    box.transparency = 50
    assert box.transparency == 1.0
    box.transparency = 0.67
    assert box.transparency == 0.67
    box.transparency = 0.0
    assert box.transparency == 0.0
    box.transparency = 1.0
    assert box.transparency == 1.0
    box.transparency = -1
    assert box.transparency == 0.0


def test_object3d_properties_color(aedt_app) -> None:
    box = create_copper_box(aedt_app, "color_box")
    box.color = (0, 0, 255)
    assert box.color == (0, 0, 255)


def test_object_clone_and_get_properties(aedt_app) -> None:
    initial_object = create_copper_box(aedt_app, "Properties_Box")
    initial_object.transparency = 0.76
    new_object = initial_object.clone()
    assert new_object.name != initial_object.name
    assert new_object.material_name == initial_object.material_name
    assert new_object.solve_inside == initial_object.solve_inside
    assert new_object.model == initial_object.model
    assert new_object.display_wireframe == initial_object.display_wireframe
    assert new_object.material_appearance == initial_object.material_appearance
    assert new_object.part_coordinate_system == initial_object.part_coordinate_system
    assert new_object.transparency == 0.76
    assert new_object.color == initial_object.color
    assert new_object.bounding_box == initial_object.bounding_box
    assert len(new_object.vertices) == 8
    assert len(new_object.faces) == 6
    assert len(new_object.edges) == 12
    new_object.name = "Properties_Box"
    assert not new_object.name == "Properties_Box"


def test_top_bottom_face(aedt_app) -> None:
    box = create_copper_box(aedt_app)
    assert isinstance(box.top_face_x, FacePrimitive)
    assert isinstance(box.top_face_y, FacePrimitive)
    assert isinstance(box.top_face_z, FacePrimitive)
    assert isinstance(box.bottom_face_x, FacePrimitive)
    assert isinstance(box.bottom_face_y, FacePrimitive)
    assert isinstance(box.bottom_face_z, FacePrimitive)


def test_top_bottom_edge(aedt_app) -> None:
    box = create_copper_box(aedt_app)
    assert isinstance(box.faces[0].top_edge_x, EdgePrimitive)
    assert isinstance(box.faces[0].top_edge_y, EdgePrimitive)
    assert isinstance(box.faces[0].top_edge_z, EdgePrimitive)
    assert isinstance(box.top_edge_x, EdgePrimitive)
    assert isinstance(box.top_edge_y, EdgePrimitive)
    assert isinstance(box.top_edge_z, EdgePrimitive)
    cylinder = create_copper_cylinder(aedt_app)
    assert isinstance(cylinder.bottom_edge_x, EdgePrimitive)
    assert isinstance(cylinder.bottom_edge_y, EdgePrimitive)
    assert isinstance(cylinder.bottom_edge_z, EdgePrimitive)
    for edge in cylinder.edges:
        assert edge.segment_info


def test_to_boolean() -> None:
    assert _to_boolean(True)
    assert not _to_boolean(False)
    assert _to_boolean("d")
    assert not _to_boolean("f")
    assert not _to_boolean("no")


NEW_VERTICES_POSITION = [[10.0, 0.0, 3.0], [0.0, 0.0, 3.0], [0.0, 2.0, 5.0], [10.0, 2.0, 5.0]]


def test_chamfer_called_on_edge(aedt_app) -> None:
    box = create_copper_box(aedt_app, "ChamferOnEdge")
    # Chamfer type 0 (default)
    assert not (any(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION))
    assert box.edges[0].chamfer(left_distance=2)
    assert all(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION)
    aedt_app._odesign.Undo()
    assert box.edges[0].chamfer(left_distance=2, right_distance=3)
    aedt_app._odesign.Undo()
    # Chamfer type 1
    assert not (any(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION))
    assert box.edges[0].chamfer(left_distance=2, chamfer_type=1)
    assert all(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION)
    aedt_app._odesign.Undo()
    # Chamfer type 2
    assert not (any(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION))
    assert box.edges[0].chamfer(left_distance=2, angle=45, chamfer_type=2)
    assert all(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION)
    aedt_app._odesign.Undo()
    # Chamfer type 3
    assert not (any(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION))
    assert box.edges[0].chamfer(right_distance=2, angle=45, chamfer_type=3)
    assert all(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION)
    aedt_app._odesign.Undo()
    # Chamfer type 4 - not valid
    assert not box.edges[0].chamfer(chamfer_type=4)


def test_chamfer_called_on_box(aedt_app) -> None:
    box = create_copper_box(aedt_app, "ChamferOnBox")
    # Chamfer type 0 (default)
    assert not (any(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION))
    box.chamfer(edges=box.faces[0].edges[0], left_distance=2)
    assert all(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION)
    aedt_app._odesign.Undo()
    assert box.chamfer(edges=box.faces[0].edges[0], left_distance=2, right_distance=3)
    aedt_app._odesign.Undo()
    # Chamfer type 1
    assert not (any(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION))
    assert box.chamfer(edges=box.faces[0].edges[0], left_distance=2, chamfer_type=1)
    assert all(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION)
    aedt_app._odesign.Undo()
    # Chamfer type 2
    assert not (any(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION))
    assert box.chamfer(edges=box.faces[0].edges[0], left_distance=2, angle=45, chamfer_type=2)
    assert all(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION)
    aedt_app._odesign.Undo()
    # Chamfer type 3
    assert not (any(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION))
    assert box.chamfer(edges=box.faces[0].edges[0], right_distance=2, angle=45, chamfer_type=3)
    assert all(position in (v.position for v in box.vertices) for position in NEW_VERTICES_POSITION)
    aedt_app._odesign.Undo()
    # Chamfer type 4 - not valid
    assert not box.chamfer(edges=box.faces[0].edges[0], right_distance=2, chamfer_type=4)


def test_fillet(aedt_app) -> None:
    box = create_copper_box(aedt_app, "FilletTest")
    box_edges = box.edges
    assert len(box_edges) == 12
    test_fillet = box.edges[0].fillet(radius=0.2)
    assert test_fillet
    test_fillet = box.edges[1].fillet(radius=0.2, setback=0.1)
    assert test_fillet


def test_object_length(aedt_app) -> None:
    box = create_copper_box(aedt_app)
    test_edge = box.edges[0]
    assert isinstance(test_edge.length, float)
    start_point = box.edges[0].vertices[0]
    end_point = box.edges[0].vertices[1]
    sum_sq = 0
    for i in range(0, 3):
        sum_sq += (end_point.position[i] - start_point.position[i]) ** 2
    assert is_close(math.sqrt(sum_sq), test_edge.length)


def test_set_color(aedt_app) -> None:
    box = create_copper_box(aedt_app, "ColorTest")
    box.color = "Red"
    assert box.color == (255, 0, 0)
    box.color = "Green"
    assert box.color == (0, 128, 0)
    box.color = "Blue"
    assert box.color == (0, 0, 255)
    box.color = (255, 0, 0)
    assert box.color == (255, 0, 0)
    box.color = "(255 0 0)"
    assert box.color == (255, 0, 0)
    box.color = "(300 0 0)"
    assert box.color == (255, 0, 0)
    box.color = "(123 0 0 55)"
    assert box.color == (255, 0, 0)
    box.color = "InvalidString"
    assert box.color == (255, 0, 0)
    box.color = (255, "Invalid", 0)
    assert box.color == (255, 0, 0)


def test_print_object(aedt_app) -> None:
    box = create_copper_box(aedt_app)
    assert box.name in box.__repr__()
    test_face = box.faces[0]
    try:
        int(test_face.__str__())
        int(test_face.__repr__())
    except Exception:
        pytest.fail("Conversion to int failed for FacePrimitive __str__ or __repr__ outputs.")
    test_edge = test_face.edges[0]
    try:
        int(test_edge.__str__())
        int(test_edge.__repr__())
    except Exception:
        pytest.fail("Conversion to int failed for EdgePrimitive __str__ or __repr__ outputs.")
    test_vertex = test_face.vertices[0]
    try:
        int(test_vertex.__str__())
        int(test_vertex.__repr__())
    except Exception:
        pytest.fail("Conversion to int failed for VertexPrimitive __str__ or __repr__ outputs.")


def test_translate_box(aedt_app) -> None:
    box = create_copper_box(aedt_app)
    v0 = box.vertices[0].position
    box.move([1, 0, 0])
    v1 = box.vertices[0].position
    assert v1[0] == v0[0] + 1.0
    assert v1[1] == v0[1]
    assert v1[2] == v0[2]
    assert box.move([1, 0, 0])


def test_duplicate_around_axis_and_unite(aedt_app) -> None:
    turn = create_example_coil(aedt_app, "single_turn")
    added_objects = turn.duplicate_around_axis(axis="Z", angle=8, clones=19)
    turn.unite(added_objects)
    assert len(added_objects) == 18
    assert "single_turn" in aedt_app.modeler.line_names


def test_duplicate_along_line(aedt_app) -> None:
    turn = create_example_coil(aedt_app, "single_turn")
    added_objects = turn.duplicate_along_line([0, 0, 15], clones=3, attach=False)
    assert len(added_objects) == 2
    assert "single_turn" in aedt_app.modeler.line_names


def test_section(aedt_app) -> None:
    box = create_copper_box(aedt_app, "SectionBox")
    section = box.section(plane="YZ", create_new=True, section_cross_object=False)
    assert section


def test_create_spiral(aedt_app) -> None:
    spiral = aedt_app.modeler.create_spiral(name="ind")
    assert spiral
    assert spiral.name == "ind"
    assert len(spiral.points) == 78


def test_rotate(aedt_app) -> None:
    box = create_copper_box(aedt_app)
    assert box.rotate(axis="Y", angle=180)


def test_mirror(aedt_app) -> None:
    box = create_copper_box(aedt_app)
    assert box.mirror(origin=[-10, 0, 0], vector=[0, 1, 0])


def test_groups(aedt_app) -> None:
    box1 = create_copper_box(aedt_app, "GroupB1")
    box2 = create_copper_box(aedt_app, "GroupB2")
    assert box1.group_name == "Model"
    box1.group_name = "NewGroup"
    assert box1.group_name == "NewGroup"
    box2.group_name = "NewGroup"
    assert box2.group_name == "NewGroup"
    box2.group_name = "NewGroup2"
    assert box2.group_name == "NewGroup2"
    assert box1.group_name == "NewGroup"


def test_mass(aedt_app) -> None:
    aedt_app.modeler.model_units = "meter"
    box1 = aedt_app.modeler.create_box([0, 0, 0], [5, 10, 2], material="Copper")
    assert box1.mass == 893300.0
    new_material = aedt_app.materials.add_material("MyMaterial")
    box2 = aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10], material="MyMaterial")
    assert box2.mass == 0.0
    new_material.mass_density = 1
    assert is_close(box2.mass, 1000.0)
    box2.model = False
    assert box2.mass == 0.0
    rec = aedt_app.modeler.create_rectangle(0, [0, 0, 0], [5, 10])
    assert rec.mass == 0.0


def test_volume(aedt_app) -> None:
    box = aedt_app.modeler.create_box([10, 10, 10], [5, 10, 2], material="Copper")
    assert is_close(box.volume, 100)
    rec = aedt_app.modeler.create_rectangle(0, [0, 0, 0], [5, 10])
    assert rec.volume == 0.0


def test_filter_faces_by_area(aedt_app) -> None:
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    faces_equal = []
    for obj in aedt_app.modeler.object_list:
        if obj.faces_by_area(100):
            faces_equal.append(obj.faces_by_area(100))
    assert len(faces_equal) > 0  # otherwise, the test is invalid
    for face_object in faces_equal:
        for face in face_object:
            assert abs(face.area - 100) < 1e-12
    faces_greater_equal = []
    for obj in aedt_app.modeler.object_list:
        if obj.faces_by_area(100, ">="):
            faces_greater_equal.append(obj.faces_by_area(100, ">="))
    assert len(faces_greater_equal) > 0  # otherwise, the test is invalid
    for face_object in faces_greater_equal:
        for face in face_object:
            assert (face.area - 100) >= -1e-12
    faces_smaller_equal = []
    for obj in aedt_app.modeler.object_list:
        if obj.faces_by_area(100, "<="):
            faces_smaller_equal.append(obj.faces_by_area(100, "<="))
    assert len(faces_smaller_equal) > 0  # otherwise, the test is invalid
    for face_object in faces_smaller_equal:
        for face in face_object:
            assert (face.area - 100) <= 1e-12
    faces_greater = []
    for obj in aedt_app.modeler.object_list:
        if obj.faces_by_area(99, ">"):
            faces_greater.append(obj.faces_by_area(99, ">"))
    assert len(faces_greater) > 0  # otherwise, the test is invalid
    for face_object in faces_greater:
        for face in face_object:
            assert (face.area - 99) > 0
    faces_smaller = []
    for obj in aedt_app.modeler.object_list:
        if obj.faces_by_area(105, "<"):
            faces_smaller.append(obj.faces_by_area(105, "<"))
    assert len(faces_smaller) > 0  # otherwise, the test is invalid
    for face_object in faces_smaller:
        for face in face_object:
            assert (face.area - 105) < 0
    with pytest.raises(ValueError):
        aedt_app.modeler.object_list[0].faces_by_area(100, "<<")


def test_edges_by_length(aedt_app) -> None:
    aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    edges_equal = []
    for obj in aedt_app.modeler.object_list:
        if obj.edges_by_length(10):
            edges_equal.append(obj.edges_by_length(10))
    assert len(edges_equal) > 0  # otherwise, the test is invalid
    for edge_object in edges_equal:
        for edge in edge_object:
            assert abs(edge.length - 10) < 1e-12
    edges_greater_equal = []
    for obj in aedt_app.modeler.object_list:
        if obj.edges_by_length(10, ">="):
            edges_greater_equal.append(obj.edges_by_length(10, ">="))
    assert len(edges_greater_equal) > 0  # otherwise, the test is invalid
    for edge_object in edges_greater_equal:
        for edge in edge_object:
            assert (edge.length - 10) >= -1e-12
    edges_smaller_equal = []
    for obj in aedt_app.modeler.object_list:
        if obj.edges_by_length(10, "<="):
            edges_smaller_equal.append(obj.edges_by_length(10, "<="))
    assert len(edges_smaller_equal) > 0  # otherwise, the test is invalid
    for edge_object in edges_smaller_equal:
        for edge in edge_object:
            assert (edge.length - 10) <= 1e-12
    edges_greater = []
    for obj in aedt_app.modeler.object_list:
        if obj.edges_by_length(9, ">"):
            edges_greater.append(obj.edges_by_length(9, ">"))
    assert len(edges_greater) > 0  # otherwise, the test is invalid
    for edge_object in edges_greater:
        for edge in edge_object:
            assert (edge.length - 9) > 0
    edges_smaller = []
    for obj in aedt_app.modeler.object_list:
        if obj.edges_by_length(15, "<"):
            edges_smaller.append(obj.edges_by_length(15, "<"))
    assert len(edges_smaller) > 0  # otherwise, the test is invalid
    for edge_object in edges_smaller:
        for edge in edge_object:
            assert (edge.length - 15) < 0
    with pytest.raises(ValueError):
        aedt_app.modeler.object_list[0].edges_by_length(10, "<<")


def test_unclassified_object_and_delete(aedt_app) -> None:
    box1 = aedt_app.modeler.create_box([0, 0, 0], [2, 2, 2])
    box2 = aedt_app.modeler.create_box([2, 2, 2], [2, 2, 2])
    aedt_app.modeler.intersect([box1, box2])
    vArg1 = ["NAME:Selections", "Selections:=", ", ".join([box1.name, box2.name])]
    vArg2 = ["NAME:IntersectParameters", "KeepOriginals:=", False]
    aedt_app.modeler.oeditor.Intersect(vArg1, vArg2)
    assert box1.name in aedt_app.modeler.unclassified_names
    unclassified = aedt_app.modeler.unclassified_objects
    assert aedt_app.modeler.delete(unclassified)
    assert len(aedt_app.modeler.unclassified_objects) != unclassified
    assert len(aedt_app.modeler.unclassified_objects) == 0


def test_get_object_history_properties(aedt_app) -> None:
    box = create_copper_box(aedt_app, "box_history")
    cylinder = create_copper_cylinder(aedt_app)
    box_clone = box.clone()
    box_subtract = box_clone.subtract(cylinder)
    box_subtract.rotate(axis="Y", angle=180)
    box_subtract.split("XY")
    box_history = box.history()
    box_clone_history = box_clone.history()
    assert box_history._node == "box_history"
    assert box_history.command == "CreateBox"
    assert box_history.properties["Command"] == "CreateBox"
    assert box_history.children == {}
    assert box_clone_history._node == "box_history1"
    assert box_clone_history.command == box_history.command
    assert box_clone_history.properties["Command"] == box_history.properties["Command"]
    assert box_clone_history.properties["Position/X"] == box_history.properties["Position/X"]
    assert box_clone_history.properties["Position/Y"] == box_history.properties["Position/Y"]
    assert box_clone_history.properties["Position/Z"] == box_history.properties["Position/Z"]
    assert box_clone_history.properties["XSize"] == box_history.properties["XSize"]
    assert box_clone_history.properties["YSize"] == box_history.properties["YSize"]
    assert box_clone_history.properties["ZSize"] == box_history.properties["ZSize"]
    assert len(box_clone_history.children) == 3
    assert "Subtract:1" in box_clone_history.children.keys()
    assert "Rotate:1" in box_clone_history.children.keys()
    assert "SplitEdit:1" in box_clone_history.children.keys()
    assert box_clone_history.children["Subtract:1"].command == "Subtract"
    assert box_clone_history.children["Rotate:1"].command == "Rotate"
    assert box_clone_history.children["SplitEdit:1"].command == "SplitEdit"
    project_path = aedt_app.project_file
    aedt_app.close_project(save=True)
    aedt_app.load_project(project_path)
    subtract = aedt_app.modeler["box_history1"].history().children["Subtract:1"].children
    assert len(subtract) == 1
    for key in subtract.keys():
        assert subtract[key].command == subtract[key].properties["Command"]
        subtract_child = subtract[key].children
        for child in subtract_child.keys():
            assert subtract_child[child].command == subtract_child[child].properties["Command"]
            assert len(subtract_child[child].children) == 0


def test_object_history_suppress(aedt_app) -> None:
    box = create_copper_box(aedt_app, "history_test_box")
    cylinder = create_copper_cylinder(aedt_app)
    box = box.subtract(cylinder)
    box.rotate(axis="Y", angle=180)
    box.split("XY")
    assert box.history().suppress_all(aedt_app)
    assert box.history().unsuppress_all(aedt_app)


def test_object_history_jsonalize(aedt_app) -> None:
    box = create_copper_box(aedt_app, "history_test_box")
    cylinder = create_copper_cylinder(aedt_app)
    box = box.subtract(cylinder)
    box.rotate(axis="Y", angle=180)
    box.split("XY")
    assert box.history().jsonalize_tree()


def test_set_object_history_properties(aedt_app) -> None:
    aedt_app.modeler.model_units = "meter"
    box = aedt_app.modeler.create_box([10, 10, 10], [15, 15, 15], "box_history", material="Copper")
    cylinder = aedt_app.modeler.create_cylinder(
        orientation="Y",
        origin=[10, 10, 10],
        radius=5,
        height=20,
        num_sides=4,
        name="cylinder_history",
        material="Copper",
    )
    box = box.subtract(cylinder)
    box = box.rotate(axis="Y", angle=180)
    box = box.split("XY")
    history = aedt_app.modeler["box_history"].history()
    assert history.properties["Position/X"] == "10meter"
    history.properties["Position/X"] = "15meter"
    assert history.properties["Position/X"] == "15meter"
    assert history.properties["ZSize"] == "15meter"
    history.properties["ZSize"] = "10meter"
    assert history.properties["ZSize"] == "10meter"
    subtract = history.children["Subtract:1"].children
    subtract_child_prop_checked = False
    for key in subtract.keys():
        subtract_child = subtract[key].children
        for child in subtract_child.keys():
            if "CreateCylinder" in child:
                subtract_child_prop_checked = True
                assert subtract_child[child].properties["Center Position/X"] == "10meter"
                subtract_child[child].properties["Center Position/X"] = "15meter"
                assert subtract_child[child].properties["Center Position/X"] == "15meter"
                assert subtract_child[child].properties["Axis"] == "Y"
                subtract_child[child].properties["Axis"] = "Z"
                assert subtract_child[child].properties["Axis"] == "Z"
                assert subtract_child[child].properties["Radius"] == "5meter"
                subtract_child[child].properties["Radius"] = "8meter"
                assert subtract_child[child].properties["Radius"] == "8meter"
                assert subtract_child[child].properties["Height"] == "20meter"
                subtract_child[child].properties["Height"] = "24meter"
                assert subtract_child[child].properties["Height"] == "24meter"
    assert subtract_child_prop_checked  # otherwise, the test is invalid


def test_insert_nets(aedt_app) -> None:
    aedt_app.insert_design("nets")
    aedt_app.modeler.create_box([0, 0, 0], [5, 10, 10], material="copper")
    aedt_app.modeler.create_box([30, 0, 0], [5, 10, 10], material="copper")
    aedt_app.modeler.create_box([60, 0, 0], [5, 10, 10], material="vacuum")
    nets = aedt_app.identify_touching_conductors()
    assert len(nets) == 2


def test_heal_objects(aedt_app) -> None:
    aedt_app.insert_design("Heal_Objects")
    create_copper_box(aedt_app, "box_1")
    create_copper_box(aedt_app, "box_2")
    assert aedt_app.modeler.heal_objects(assignment="box_1")
    assert aedt_app.modeler.heal_objects(assignment="box_1,box_2")
    assert aedt_app.modeler.heal_objects(assignment="box_1, box_2 ")
    assert not aedt_app.modeler.heal_objects(assignment=["box_1", "box_2"])
    assert not aedt_app.modeler.heal_objects(assignment="box_1", simplify_type=3)
    assert aedt_app.modeler.heal_objects(assignment="box_1", max_stitch_tolerance="0.01")
    assert aedt_app.modeler.heal_objects(assignment="box_1", max_stitch_tolerance=0.01)
    assert aedt_app.modeler.heal_objects(assignment="box_1", geometry_simplification_tolerance=1.2)
    assert aedt_app.modeler.heal_objects(assignment="box_1", geometry_simplification_tolerance="1.2")
    assert aedt_app.modeler.heal_objects(assignment="box_1", tighten_gaps_width=0.001)
    assert aedt_app.modeler.heal_objects(assignment="box_1", tighten_gaps_width="0.001")
    assert aedt_app.modeler.heal_objects(assignment="box_1", silver_face_tolerance=1.2)
    assert aedt_app.modeler.heal_objects(assignment="box_1", silver_face_tolerance="1.2")
    assert not aedt_app.modeler.heal_objects(assignment=None)
    assert not aedt_app.modeler.heal_objects(assignment=1)


@pytest.mark.skipif(is_linux, reason="Crashing in linux")
def test_simplify_objects(aedt_app) -> None:
    create_copper_box(aedt_app, "box_1")
    create_copper_box(aedt_app, "box_2")
    assert aedt_app.modeler.simplify_objects(assignment="box_1")
    assert aedt_app.modeler.simplify_objects(assignment="box_1,box_2")
    assert aedt_app.modeler.simplify_objects(assignment="box_1, box_2")
    assert not aedt_app.modeler.simplify_objects(assignment=["box_1", "box_2"])
    assert aedt_app.modeler.simplify_objects(assignment="box_1", simplify_type="Primitive Fit")
    assert not aedt_app.modeler.simplify_objects(assignment="box_1", simplify_type="Invalid")
    assert not aedt_app.modeler.simplify_objects(assignment="box_1", simplify_type="Polygon Fit", extrusion_axis="U")
    assert not aedt_app.modeler.simplify_objects(assignment=None)
    assert not aedt_app.modeler.simplify_objects(assignment=1)


def test_rescale(aedt_app) -> None:
    aedt_app.modeler.model_units = "meter"
    box = aedt_app.modeler.create_box([0, 0, 0], [5, 10, 2], material="Copper")
    assert box.mass == 893300.0
    aedt_app.modeler.rescale_model = True
    aedt_app.modeler.model_units = "mm"
    assert round(box.mass, 5) == 0.00089
