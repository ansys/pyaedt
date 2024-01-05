# standard imports
import filecmp
import math
import os
import sys

import pytest

from pyaedt.generic.general_methods import is_linux
from pyaedt.generic.general_methods import isclose
from pyaedt.maxwell import Maxwell2d


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(design_name="2D_Primitives", application=Maxwell2d)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_01_model_units(self):
        model_units = self.aedtapp.modeler.model_units
        assert model_units == "mm"
        self.aedtapp.modeler.model_units = "cm"
        assert self.aedtapp.modeler.model_units == "cm"

    def test_02_boundingbox(self):
        bounding = self.aedtapp.modeler.obounding_box
        assert len(bounding) == 6

    def test_03_objects(self):
        assert self.aedtapp.modeler.oeditor
        assert self.aedtapp.modeler._odefinition_manager
        assert self.aedtapp.modeler._omaterial_manager

    def test_04_create_rectangle(self):
        test_color = (220, 90, 0)
        rect1 = self.aedtapp.modeler.create_rectangle([0, -2, -2], [3, 8])
        rect2 = self.aedtapp.modeler.create_rectangle(
            position=[10, -2, -2],
            dimension_list=[3, 10],
            name="MyRectangle",
            material_name="Copper",
            color=test_color,
        )
        assert rect1.solve_inside
        assert rect1.model
        assert rect1.material_name == "vacuum"
        assert rect2.color == test_color
        assert isclose(rect1.faces[0].area, 3.0 * 8.0)

        list_of_pos = [ver.position for ver in rect1.vertices]
        assert sorted(list_of_pos) == [[0.0, -2.0, -2.0], [0.0, 6.0, -2.0], [3.0, -2.0, -2.0], [3.0, 6.0, -2.0]]

        assert rect2.solve_inside
        assert rect2.model
        assert rect2.material_name == "copper"
        assert isclose(rect2.faces[0].area, 3.0 * 10.0)

        list_of_pos = [ver.position for ver in rect2.vertices]
        assert sorted(list_of_pos) == [[10.0, -2.0, -2.0], [10.0, 8.0, -2.0], [13.0, -2.0, -2.0], [13.0, 8.0, -2.0]]

    def test_05_create_rectangle_rz(self):
        self.aedtapp.solution_type = "MagnetostaticZ"
        rect1 = self.aedtapp.modeler.create_rectangle([1, 0, -2], [8, 3])
        rect2 = self.aedtapp.modeler.create_rectangle(
            position=[10, 0, -2], dimension_list=[10, 3], name="MyRectangle", matname="Copper"
        )
        list_of_pos = [ver.position for ver in rect1.vertices]
        assert sorted(list_of_pos) == [[1.0, 0.0, -2.0], [1.0, 0.0, 6.0], [4.0, 0.0, -2.0], [4.0, 0.0, 6.0]]

        list_of_pos = [ver.position for ver in rect2.vertices]
        assert sorted(list_of_pos) == [[10.0, 0.0, -2.0], [10.0, 0.0, 8.0], [13.0, 0.0, -2.0], [13.0, 0.0, 8.0]]

    def test_06_create_circle(self):
        circle1 = self.aedtapp.modeler.create_circle([0, -2, 0], 3)

        # TODO: deprecate "matname" as named argument, replace it with the Object3D property "material_name"
        circle2 = self.aedtapp.modeler.create_circle(
            position=[0, -2, -2],
            radius=3,
            num_sides=6,
            name="MyCircle",
            matname="Copper",
            display_wireframe=True,
        )
        assert circle1.solve_inside
        assert circle1.model
        assert circle1.material_name == "vacuum"
        assert isclose(circle1.faces[0].area, math.pi * 3.0 * 3.0)

        assert circle2.solve_inside
        assert circle2.model
        assert circle2.material_name == "copper"
        assert isclose(circle1.faces[0].area, math.pi * 3.0 * 3.0)
        circle3 = self.aedtapp.modeler.create_circle(
            position=[0, 4, -2],
            radius=2,
            num_sides=8,
            name="Circle3",
            material_name="Copper",
        )
        assert circle3.material_name == "copper"
        circle4 = self.aedtapp.modeler.create_circle(
            position=[0, -4, -2],
            radius=2.2,
            num_sides=6,
            name="NonModelCirc",
            model=False,
        )
        assert not circle4.model

    def test_06a_calculate_radius_2D(self):
        circle1 = self.aedtapp.modeler.create_circle([0, -2, 0], 3)
        radius = self.aedtapp.modeler.calculate_radius_2D(circle1.name)
        assert type(radius) is float
        radius = self.aedtapp.modeler.calculate_radius_2D(circle1.name, True)
        assert type(radius) is float

    def test_06b_radial_split(self):
        circle1 = self.aedtapp.modeler.create_circle([0, -2, 0], 3)
        radius = self.aedtapp.modeler.calculate_radius_2D(circle1.name)
        assert self.aedtapp.modeler.radial_split_2D(radius, circle1.name)

    def test_07_create_ellipse(self):
        ellipse1 = self.aedtapp.modeler.create_ellipse([0, -2, 0], 4.0, 3)
        ellipse2 = self.aedtapp.modeler.create_ellipse(
            position=[0, -2, 0], major_radius=4.0, ratio=3, name="MyEllipse", matname="Copper"
        )
        assert ellipse1.solve_inside
        assert ellipse1.model
        assert ellipse1.material_name == "vacuum"
        assert isclose(ellipse2.faces[0].area, math.pi * 4.0 * 4.0 * 3, rel_tol=0.1)

        assert ellipse2.solve_inside
        assert ellipse2.model
        assert ellipse2.material_name == "copper"
        assert isclose(ellipse2.faces[0].area, math.pi * 4.0 * 4.0 * 3, rel_tol=0.1)

    def test_08_create_regular_polygon(self):
        pg1 = self.aedtapp.modeler.create_regular_polygon([0, 0, 0], [0, 0, 2])
        pg2 = self.aedtapp.modeler.create_regular_polygon(
            position=[0, 0, 0], start_point=[0, 0, 2], num_sides=3, name="MyPolygon", matname="Copper"
        )
        assert pg1.solve_inside
        assert pg1.model
        assert pg1.material_name == "vacuum"
        assert not pg1.is_conductor
        assert isclose(pg1.faces[0].area, 10.392304845413264)

        assert pg2.solve_inside
        assert pg2.model
        assert pg2.material_name == "copper"
        assert pg2.is_conductor
        assert isclose(pg2.faces[0].area, 5.196152422706631)

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not running in ironpython")
    def test_09_plot(self):
        self.aedtapp.solution_type = "MagnetostaticZ"
        self.aedtapp.modeler.create_regular_polygon([0, 0, 0], [0, 0, 2])
        self.aedtapp.modeler.create_regular_polygon(
            position=[0, 0, 0], start_point=[0, 0, 2], num_sides=3, name="MyPolygon", matname="Copper"
        )
        obj = self.aedtapp.plot(show=False, export_path=os.path.join(self.local_scratch.path, "image.jpg"))
        assert os.path.exists(obj.image_file)
        obj2 = self.aedtapp.plot(show=False, export_path=os.path.join(self.local_scratch.path, "image.jpg"), view="xy")
        assert os.path.exists(obj2.image_file)
        obj3 = self.aedtapp.plot(show=False, export_path=os.path.join(self.local_scratch.path, "image.jpg"), view="xy1")
        assert filecmp.cmp(obj.image_file, obj3.image_file)

    def test_10_edit_menu_commands(self):
        rect1 = self.aedtapp.modeler.create_rectangle([1, 0, -2], [8, 3])
        assert self.aedtapp.modeler.mirror(rect1, [1, 0, 0], [1, 0, 0])
        assert self.aedtapp.modeler.move(rect1, [1, 1, 0])

    def test_11_move_edge(self):
        poly = self.aedtapp.modeler.create_regular_polygon([0, 0, 0], [0, 0, 2])
        assert poly.faces[0].edges[0].move_along_normal(1)
        assert self.aedtapp.modeler.move_edge([poly.edges[0], poly.edges[1]])

    def test_12_objects_in_bounding_box(self):
        self.aedtapp.solution_type = "MagnetostaticXY"
        bounding_box = [-52, -68, 35, 42]
        objects_xy_4 = self.aedtapp.modeler.objects_in_bounding_box(bounding_box=bounding_box)
        bounding_box = [-25, -36, -40, 20, 30, 10]
        objects_xy_6 = self.aedtapp.modeler.objects_in_bounding_box(bounding_box=bounding_box)
        assert type(objects_xy_4) is list
        assert type(objects_xy_6) is list
        self.aedtapp.solution_type = "MagnetostaticZ"
        bounding_box = [-52, -68, 35, 42]
        objects_z_4 = self.aedtapp.modeler.objects_in_bounding_box(bounding_box=bounding_box)
        bounding_box = [-25, -36, -40, 20, 30, 10]
        objects_z_6 = self.aedtapp.modeler.objects_in_bounding_box(bounding_box=bounding_box)
        assert type(objects_z_4) is list
        assert type(objects_z_6) is list
        with pytest.raises(ValueError):
            bounding_box = [3, 4, 5]
            self.aedtapp.modeler.objects_in_bounding_box(bounding_box)
        with pytest.raises(ValueError):
            bounding_box_5_elements = [1, 2, 3, 4, 5]
            self.aedtapp.modeler.objects_in_bounding_box(bounding_box_5_elements)

    def test_13_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_14_split(self):
        self.aedtapp.insert_design("split_test")
        rect1 = self.aedtapp.modeler.create_rectangle([0, -2, 0], [3, 8])
        poly1 = self.aedtapp.modeler.create_polyline(
            position_list=[[-2, 2, 0], [1, 5, 0], [5, 3, 0]], segment_type="Arc"
        )
        assert not self.aedtapp.modeler.split(objects=rect1)
        split = self.aedtapp.modeler.split(objects=rect1, plane=self.aedtapp.PLANE.ZX)
        assert isinstance(split, list)
        assert isinstance(split[0], str)
        obj_split = [obj for obj in self.aedtapp.modeler.object_list if obj.name == split[1]][0]
        assert not self.aedtapp.modeler.split(objects=obj_split, tool=poly1.edges[0])
