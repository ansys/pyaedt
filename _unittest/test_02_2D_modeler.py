# standard imports
import math
import os

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import isclose
from pyaedt.maxwell import Maxwell2d

# Setup paths for module imports

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, design_name="2D_Primitives", application=Maxwell2d)

    def teardown_class(self):
        BasisTest.my_teardown(self)

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

    def test_create_rectangle(self):
        rect1 = self.aedtapp.modeler.create_rectangle([0, -2, -2], [3, 8])
        rect2 = self.aedtapp.modeler.create_rectangle(
            position=[10, -2, -2], dimension_list=[3, 10], name="MyRectangle", matname="Copper"
        )
        assert rect1.solve_inside
        assert rect1.model
        assert rect1.material_name == "vacuum"
        assert isclose(rect1.faces[0].area, 3.0 * 8.0)

        list_of_pos = [ver.position for ver in rect1.vertices]
        assert sorted(list_of_pos) == [[0.0, -2.0, -2.0], [0.0, 6.0, -2.0], [3.0, -2.0, -2.0], [3.0, 6.0, -2.0]]

        assert rect2.solve_inside
        assert rect2.model
        assert rect2.material_name == "copper"
        assert isclose(rect2.faces[0].area, 3.0 * 10.0)

        list_of_pos = [ver.position for ver in rect2.vertices]
        assert sorted(list_of_pos) == [[10.0, -2.0, -2.0], [10.0, 8.0, -2.0], [13.0, -2.0, -2.0], [13.0, 8.0, -2.0]]

    def test_create_rectangle_rz(self):
        self.aedtapp.solution_type = "MagnetostaticZ"
        rect1 = self.aedtapp.modeler.create_rectangle([1, 0, -2], [8, 3])
        rect2 = self.aedtapp.modeler.create_rectangle(
            position=[10, 0, -2], dimension_list=[10, 3], name="MyRectangle", matname="Copper"
        )
        list_of_pos = [ver.position for ver in rect1.vertices]
        assert sorted(list_of_pos) == [[1.0, 0.0, -2.0], [1.0, 0.0, 6.0], [4.0, 0.0, -2.0], [4.0, 0.0, 6.0]]

        list_of_pos = [ver.position for ver in rect2.vertices]
        assert sorted(list_of_pos) == [[10.0, 0.0, -2.0], [10.0, 0.0, 8.0], [13.0, 0.0, -2.0], [13.0, 0.0, 8.0]]

    def test_create_circle(self):
        circle1 = self.aedtapp.modeler.create_circle([0, -2, 0], 3)
        circle2 = self.aedtapp.modeler.create_circle(
            position=[0, -2, -2], radius=3, num_sides=6, name="MyCircle", matname="Copper"
        )
        assert circle1.solve_inside
        assert circle1.model
        assert circle1.material_name == "vacuum"
        assert isclose(circle1.faces[0].area, math.pi * 3.0 * 3.0)

        assert circle2.solve_inside
        assert circle2.model
        assert circle2.material_name == "copper"
        assert isclose(circle1.faces[0].area, math.pi * 3.0 * 3.0)

    def test_create_ellipse(self):
        ellipse1 = self.aedtapp.modeler.create_ellipse([0, -2, 0], 4.0, 0.2)
        ellipse2 = self.aedtapp.modeler.create_ellipse(
            position=[0, -2, 0], major_radius=4.0, ratio=0.2, name="MyEllipse", matname="Copper"
        )
        assert ellipse1.solve_inside
        assert ellipse1.model
        assert ellipse1.material_name == "vacuum"
        assert isclose(ellipse2.faces[0].area, math.pi * 4.0 * 4.0 * 0.2)

        assert ellipse2.solve_inside
        assert ellipse2.model
        assert ellipse2.material_name == "copper"
        assert isclose(ellipse2.faces[0].area, math.pi * 4.0 * 4.0 * 0.2)

    def test_create_regular_polygon(self):
        pg1 = self.aedtapp.modeler.create_regular_polygon([0, 0, 0], [0, 0, 2])
        pg2 = self.aedtapp.modeler.create_regular_polygon(
            position=[0, 0, 0], start_point=[0, 0, 2], num_sides=3, name="MyPolygon", matname="Copper"
        )
        assert pg1.solve_inside
        assert pg1.model
        assert pg1.material_name == "vacuum"
        assert isclose(pg1.faces[0].area, 10.392304845413264)

        assert pg2.solve_inside
        assert pg2.model
        assert pg2.material_name == "copper"
        assert isclose(pg2.faces[0].area, 5.196152422706631)

    @pytest.mark.skipif(config["build_machine"] or is_ironpython, reason="Not running in ironpython")
    def test_plot(self):
        self.aedtapp.modeler.create_regular_polygon([0, 0, 0], [0, 0, 2])
        self.aedtapp.modeler.create_regular_polygon(
            position=[0, 0, 0], start_point=[0, 0, 2], num_sides=3, name="MyPolygon", matname="Copper"
        )
        obj = self.aedtapp.plot(show=False, export_path=os.path.join(self.local_scratch.path, "image.jpg"))
        assert os.path.exists(obj.image_file)

    def test_edit_menu_commands(self):
        rect1 = self.aedtapp.modeler.create_rectangle([1, 0, -2], [8, 3])
        assert self.aedtapp.modeler.mirror(rect1, [1, 0, 0], [1, 0, 0])
        assert self.aedtapp.modeler.move(rect1, [1, 1, 0])
