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

# standard imports
import filecmp
import math
from pathlib import Path
import sys

import pytest

from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.numbers_utils import is_close
from ansys.aedt.core.maxwell import Maxwell2d


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Maxwell2d)
    yield app
    app.close_project(app.project_name, save=False)


def test_model_units(aedt_app):
    aedt_app.modeler.model_units = "cm"
    assert aedt_app.modeler.model_units == "cm"


def test_boundingbox(aedt_app):
    bounding = aedt_app.modeler.obounding_box
    assert len(bounding) == 6


def test_objects(aedt_app):
    assert aedt_app.modeler.oeditor
    assert aedt_app.modeler._odefinition_manager
    assert aedt_app.modeler._omaterial_manager


def test_create_rectangle(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    test_color = (220, 90, 0)
    rect1 = aedt_app.modeler.create_rectangle([0, -2, -2], [3, 8])
    rect2 = aedt_app.modeler.create_rectangle(
        origin=[10, -2, -2],
        sizes=[3, 10],
        name="MyRectangle",
        material="Copper",
        color=test_color,
    )
    assert rect1.solve_inside
    assert rect1.model
    assert rect1.material_name == "vacuum"
    assert rect2.color == test_color
    assert is_close(rect1.faces[0].area, 3.0 * 8.0)

    list_of_pos = [ver.position for ver in rect1.vertices]
    assert sorted(list_of_pos) == [[0.0, -2.0, -2.0], [0.0, 6.0, -2.0], [3.0, -2.0, -2.0], [3.0, 6.0, -2.0]]

    assert rect2.solve_inside
    assert rect2.model
    assert rect2.material_name == "copper"
    assert is_close(rect2.faces[0].area, 3.0 * 10.0)

    list_of_pos = [ver.position for ver in rect2.vertices]
    assert sorted(list_of_pos) == [[10.0, -2.0, -2.0], [10.0, 8.0, -2.0], [13.0, -2.0, -2.0], [13.0, 8.0, -2.0]]


def test_create_rectangle_material_array(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    materials = ["copper", "steel_1008"]
    material_array = []
    for m in materials:
        material_array.append('"' + m + '"')
    s = ", ".join(material_array)
    aedt_app["Materials"] = f"[{s}]"
    material_index = 1
    rect1 = aedt_app.modeler.create_rectangle(
        origin=[0, 0, 0], sizes=[6, 12], name="rect1", material=f"Materials[{material_index}]"
    )
    assert rect1.material_name == materials[material_index]
    rect2 = aedt_app.modeler.create_rectangle(origin=[0, 0, 0], sizes=[6, 12], name="rect2", material="test[0]")
    assert rect2.material_name == "vacuum"
    aedt_app["disp"] = 0
    rect3 = aedt_app.modeler.create_rectangle(
        origin=[0, 0, 0],
        sizes=[6, 12],
        name="rect3",
        material="Materials[if(disp<=2 && 2<=disp+9,0,1)]",
    )
    assert rect3.material_name == materials[0]


def test_create_rectangle_rz(aedt_app):
    aedt_app.solution_type = "MagnetostaticZ"
    rect1 = aedt_app.modeler.create_rectangle([1, 0, -2], [8, 3])
    rect2 = aedt_app.modeler.create_rectangle(origin=[10, 0, -2], sizes=[10, 3], name="MyRectangle", material="Copper")
    list_of_pos = [ver.position for ver in rect1.vertices]
    assert sorted(list_of_pos) == [[1.0, 0.0, -2.0], [1.0, 0.0, 6.0], [4.0, 0.0, -2.0], [4.0, 0.0, 6.0]]

    list_of_pos = [ver.position for ver in rect2.vertices]
    assert sorted(list_of_pos) == [[10.0, 0.0, -2.0], [10.0, 0.0, 8.0], [13.0, 0.0, -2.0], [13.0, 0.0, 8.0]]


def test_create_circle(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    circle1 = aedt_app.modeler.create_circle([0, -2, 0], 3)

    circle2 = aedt_app.modeler.create_circle(
        origin=[0, -2, -2],
        radius=3,
        num_sides=6,
        name="MyCircle",
        material="Copper",
        display_wireframe=True,
    )
    assert circle1.solve_inside
    assert circle1.model
    assert circle1.material_name == "vacuum"
    assert is_close(circle1.faces[0].area, math.pi * 3.0 * 3.0)

    assert circle2.solve_inside
    assert circle2.model
    assert circle2.material_name == "copper"
    assert is_close(circle1.faces[0].area, math.pi * 3.0 * 3.0)
    circle3 = aedt_app.modeler.create_circle(
        origin=[0, 4, -2],
        radius=2,
        num_sides=8,
        name="Circle3",
        material_name="Copper",
    )
    assert circle3.material_name == "copper"
    circle4 = aedt_app.modeler.create_circle(
        origin=[0, -4, -2],
        radius=2.2,
        num_sides=6,
        name="NonModelCirc",
        model=False,
    )
    assert not circle4.model


def test_calculate_radius_2D(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    circle1 = aedt_app.modeler.create_circle([0, -2, 0], 3)
    radius = aedt_app.modeler.calculate_radius_2D(circle1.name)
    assert isinstance(radius, float)
    radius = aedt_app.modeler.calculate_radius_2D(circle1.name, True)
    assert isinstance(radius, float)


def test_radial_split(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    circle1 = aedt_app.modeler.create_circle([0, -2, 0], 3)
    radius = aedt_app.modeler.calculate_radius_2D(circle1.name)
    assert aedt_app.modeler.radial_split_2D(radius, circle1.name)


def test_create_ellipse(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    ellipse1 = aedt_app.modeler.create_ellipse([0, -2, 0], 4.0, 3)
    ellipse2 = aedt_app.modeler.create_ellipse(
        origin=[0, -2, 0], major_radius=4.0, ratio=3, name="MyEllipse", material="Copper"
    )
    assert ellipse1.solve_inside
    assert ellipse1.model
    assert ellipse1.material_name == "vacuum"
    assert is_close(ellipse2.faces[0].area, math.pi * 4.0 * 4.0 * 3, relative_tolerance=0.1)

    assert ellipse2.solve_inside
    assert ellipse2.model
    assert ellipse2.material_name == "copper"
    assert is_close(ellipse2.faces[0].area, math.pi * 4.0 * 4.0 * 3, relative_tolerance=0.1)


def test_create_regular_polygon(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    pg1 = aedt_app.modeler.create_regular_polygon([0, 0, 0], [0, 2, 0])
    pg2 = aedt_app.modeler.create_regular_polygon(
        origin=[0, 0, 0], start_point=[0, 2, 0], num_sides=3, name="MyPolygon", material="Copper"
    )
    assert pg1.solve_inside
    assert pg1.model
    assert pg1.material_name == "vacuum"
    assert not pg1.is_conductor
    assert is_close(pg1.faces[0].area, 10.392304845413264)

    assert pg2.solve_inside
    assert pg2.model
    assert pg2.material_name == "copper"
    assert pg2.is_conductor
    assert is_close(pg2.faces[0].area, 5.196152422706631)


@pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not running in ironpython")
def test_plot(aedt_app, test_tmp_dir):
    aedt_app.solution_type = "MagnetostaticZ"
    aedt_app.modeler.create_regular_polygon([0, 0, 0], [0, 0, 2])
    aedt_app.modeler.create_regular_polygon(
        origin=[0, 0, 0], start_point=[0, 0, 2], num_sides=3, name="MyPolygon", material="Copper"
    )
    output_file = test_tmp_dir / "image.jpg"
    obj = aedt_app.plot(
        show=False,
        output_file=str(output_file),
        show_grid=True,
        show_bounding=True,
    )
    assert Path(obj.image_file).is_file()
    obj2 = aedt_app.plot(show=False, output_file=str(output_file), view="xy")
    assert Path(obj2.image_file).is_file()
    obj3 = aedt_app.plot(show=False, output_file=str(output_file), view="xy1")
    assert filecmp.cmp(obj.image_file, obj3.image_file)
    obj4 = aedt_app.plot(show=False)
    assert isinstance(obj4.point_cloud(), dict)


def test_edit_menu_commands(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    rect1 = aedt_app.modeler.create_rectangle([1, 0, -2], [8, 3])
    assert aedt_app.modeler.mirror(rect1, [1, 0, 0], [1, 0, 0])
    assert aedt_app.modeler.move(rect1, [1, 1, 0])


def test_move_edge(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    poly = aedt_app.modeler.create_regular_polygon([0, 0, 0], [0, 2, 0])
    assert poly.faces[0].edges[0].move_along_normal(1)
    assert aedt_app.modeler.move_edge([poly.edges[0], poly.edges[1]])


def test_objects_in_bounding_box(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    bounding_box = [-52, -68, 35, 42]
    objects_xy_4 = aedt_app.modeler.objects_in_bounding_box(bounding_box=bounding_box)
    bounding_box = [-25, -36, -40, 20, 30, 10]
    objects_xy_6 = aedt_app.modeler.objects_in_bounding_box(bounding_box=bounding_box)
    assert isinstance(objects_xy_4, list)
    assert isinstance(objects_xy_6, list)
    aedt_app.solution_type = "MagnetostaticZ"
    bounding_box = [-52, -68, 35, 42]
    objects_z_4 = aedt_app.modeler.objects_in_bounding_box(bounding_box=bounding_box)
    bounding_box = [-25, -36, -40, 20, 30, 10]
    objects_z_6 = aedt_app.modeler.objects_in_bounding_box(bounding_box=bounding_box)
    assert isinstance(objects_z_4, list)
    assert isinstance(objects_z_6, list)
    with pytest.raises(ValueError):
        bounding_box = [3, 4, 5]
        aedt_app.modeler.objects_in_bounding_box(bounding_box)
    with pytest.raises(ValueError):
        bounding_box_5_elements = [1, 2, 3, 4, 5]
        aedt_app.modeler.objects_in_bounding_box(bounding_box_5_elements)


def test_set_variable(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    aedt_app.variable_manager.set_variable("var_test", expression="123")
    aedt_app["var_test"] = "234"
    assert "var_test" in aedt_app.variable_manager.design_variable_names
    assert aedt_app.variable_manager.design_variables["var_test"].expression == "234"


def test_split(aedt_app):
    aedt_app.solution_type = "MagnetostaticXY"
    rect1 = aedt_app.modeler.create_rectangle([0, -2, 0], [3, 8])
    poly1 = aedt_app.modeler.create_polyline(points=[[-2, 2, 0], [1, 5, 0], [5, 3, 0]], segment_type="Arc")
    assert not aedt_app.modeler.split(assignment=rect1)
    split = aedt_app.modeler.split(assignment=rect1, plane=Plane.ZX)
    assert isinstance(split, list)
    assert isinstance(split[0], str)
    obj_split = [obj for obj in aedt_app.modeler.object_list if obj.name == split[1]][0]
    assert not aedt_app.modeler.split(assignment=obj_split, tool=poly1.edges[0])
