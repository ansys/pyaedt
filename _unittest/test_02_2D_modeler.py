# standard imports
import math
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path, BasisTest, pyaedt_unittest_check_desktop_error
from pyaedt.maxwell import Maxwell2d
from pyaedt.generic.general_methods import isclose

class TestClass(BasisTest):
    def setup_class(self):
        BasisTest.setup_class(self, project_name="test_primitives",
                              design_name="2D_Primitives", application=Maxwell2d)

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
        assert self.aedtapp.modeler.odefinition_manager
        assert self.aedtapp.modeler.omaterial_manager

    def test_create_rectangle(self):
        rect1 = self.aedtapp.modeler.primitives.create_rectangle([0, -2, -2], [3, 4])
        rect2 = self.aedtapp.modeler.primitives.create_rectangle(position=[0, -2, -2], dimension_list=[3, 4],
                                                                 name="MyRectangle", matname="Copper")
        assert rect1.solve_inside
        assert rect1.model
        assert rect1.material_name == "vacuum"
        assert isclose(rect1.faces[0].area, 3.0 * 4.0)

        assert rect2.solve_inside
        assert rect2.model
        assert rect2.material_name == "copper"
        assert isclose(rect1.faces[0].area, 3.0 * 4.0)

    def test_create_circle(self):
        circle1 = self.aedtapp.modeler.primitives.create_circle([0, -2, 0], 3)
        circle2 = self.aedtapp.modeler.primitives.create_circle(position=[0, -2, -2], radius=3, num_sides=6,
                                                 name="MyCircle", matname="Copper")
        assert circle1.solve_inside
        assert circle1.model
        assert circle1.material_name == "vacuum"
        assert isclose(circle1.faces[0].area, math.pi * 3.0 * 3.0)

        assert circle2.solve_inside
        assert circle2.model
        assert circle2.material_name == "copper"
        assert isclose(circle1.faces[0].area, math.pi * 3.0 * 3.0)

    def test_create_ellipse(self):
        ellipse1 = self.aedtapp.modeler.primitives.create_ellipse([0, -2, 0], 4.0, 0.2)
        ellipse2 = self.aedtapp.modeler.primitives.create_ellipse(position=[0, -2, 0], major_radius=4.0, ratio=0.2,
                                                                  name="MyEllipse", matname="Copper")
        assert ellipse1.solve_inside
        assert ellipse1.model
        assert ellipse1.material_name == "vacuum"
        assert isclose(ellipse2.faces[0].area, math.pi * 4.0 * 4.0 * 0.2)

        assert ellipse2.solve_inside
        assert ellipse2.model
        assert ellipse2.material_name == "copper"
        assert isclose(ellipse2.faces[0].area, math.pi * 4.0 * 4.0 * 0.2)

    def test_create_regular_polygon(self):
        pg1 = self.aedtapp.modeler.primitives.create_regular_polygon([0, 0, 0], [0, 2, 0])
        pg2 = self.aedtapp.modeler.primitives.create_regular_polygon(position=[0, 0, 0], start_point=[0, 2, 0],
                                                                     num_sides=3, name="MyPolygon", matname="Copper")
        assert pg1.solve_inside
        assert pg1.model
        assert pg1.material_name == "vacuum"
        assert isclose(pg1.faces[0].area, 10.392304845413264)

        assert pg2.solve_inside
        assert pg2.model
        assert pg2.material_name == "copper"
        assert isclose(pg2.faces[0].area, 5.196152422706631)


'''
    def test_05_split(self):
        box1 = self.aedtapp.modeler.primitives.create_rectangle([-10, -10, -10], [20, 20, 20], "box_to_split")
        assert self.aedtapp.modeler.split("box_to_split", 1)

    def test_06_duplicate_and_mirror(self):
        udp = self.aedtapp.modeler.Position(20, 20, 20)
        udp2 = self.aedtapp.modeler.Position(30, 40, 40)
        out = self.aedtapp.modeler.duplicate_and_mirror("outer", udp, udp2)
        assert out[0]

    def test_07_mirror(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(30, 40, 40)
        status = self.aedtapp.modeler.mirror("outer", udp, udp2)
        assert status

    def test_08_duplicate_around_axis(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        status, mirror = self.aedtapp.modeler.duplicate_around_axis("outer", udp, 45, 3)
        assert status
        assert type(mirror) is list

    def test_08_duplicate_along_line(self):
        udp = self.aedtapp.modeler.Position(5, 5, 5)
        status, mirror = self.aedtapp.modeler.duplicate_along_line("outer", udp, 5)
        assert status
        assert type(mirror) is list

    def test_09_thicken_sheet(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id5 = self.aedtapp.modeler.primitives.create_circle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 10,
                                                            name="sheet1")
        udp = self.aedtapp.modeler.Position(100, 100, 100)
        id6 = self.aedtapp.modeler.primitives.create_circle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 10,
                                                            name="sheet2")
        status = self.aedtapp.modeler.thicken_sheet(id5, 3)
        assert status
        status = self.aedtapp.modeler.automatic_thicken_sheets(id6, 3, False)
        assert status

    def test_11_split(self):
        udp1 = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(5, 0, 0)
        udp3 = self.aedtapp.modeler.Position(5, 5, 0)
        udp4 = self.aedtapp.modeler.Position(2, 5, 3)
        arrofpos = [udp1, udp2, udp3]
        id5 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="Poly1", xsection_type="Rectangle")
        assert self.aedtapp.modeler.split("Poly1", self.aedtapp.CoordinateSystemPlane.XYPlane, )

    def test_12_separate_Bodies(self):
        assert self.aedtapp.modeler.separate_bodies("Poly1")

    def test_13_rotate(self):
        assert self.aedtapp.modeler.rotate("Poly1", self.aedtapp.CoordinateSystemAxis.XAxis, 30)

    def test_14_subtract(self):
        assert self.aedtapp.modeler.subtract("outer_1", "outer_2")

    def test_15_purge_history(self):
        assert self.aedtapp.modeler.purge_history(["outer_3", "outer_4"])

    def test_16_get_model_bounding_box(self):
        assert len(self.aedtapp.modeler.get_model_bounding_box()) == 6

    def test_17_unite(self):
        assert self.aedtapp.modeler.unite(["outer_5", "outer_6"])

    def test_18_chamfer(self):
        # TODO
        assert True

    def test_19_clone(self):
        status, cloned = self.aedtapp.modeler.clone("Poly1")
        assert status
        assert type(cloned) is str

    def test_20_intersect(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [5, 10],
                                                               name="Rect1")
        id2 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [3, 12],
                                                               name="Rect2")
        assert self.aedtapp.modeler.intersect([id1, id2])

    def test_21_connect(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [5, 10])
        udp = self.aedtapp.modeler.Position(0, 0, 10)
        id2 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp,
                                                               [-3, 10])
        assert self.aedtapp.modeler.connect([id1, id2])

    def test_22_translate(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [5, 10])
        id2 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [3, 12])
        udp2 = self.aedtapp.modeler.Position(0, 20, 5)
        assert self.aedtapp.modeler.translate([id1, id2], udp2)

    def test_23_chassis_subtraction(self):
        # TODO
        assert True

    def test_24_check_plane(self):

        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.primitives.create_box(udp, [4, 5, 5])
        plane = self.aedtapp.modeler.check_plane(o.id, udp)
        planes = ["XY", "XZ", "YZ"]
        assert plane in planes

    def test_25_clean_object_name(self):
        # TODO
        assert True

    def test_26_create_airbox(self):
        o1 = self.aedtapp.modeler.create_airbox(10)
        o2 = self.aedtapp.modeler.create_airbox(50, "Relative", "Second_airbox")
        assert type(o1.id) is int
        assert type(o2.id) is int

    def test_27_create_region(self):
        assert self.aedtapp.modeler.create_air_region(*[20, 20, 30, 50, 50, 100])
        assert self.aedtapp.modeler.edit_region_dimensions([40, 30, 30, 50, 50, 100])

    def test_28_create_face_list(self):
        fl = self.aedtapp.modeler.primitives.get_object_faces("Second_airbox")
        assert self.aedtapp.modeler.create_face_list(fl, "my_face_list")

    def test_28B_create_object_list(self):
        assert self.aedtapp.modeler.create_object_list(["Second_airbox"], "my_object_list")

    def test_29_create_outer_face_list(self):
        assert self.aedtapp.modeler.create_outer_facelist(["Second_airbox"])

    def test_30_create_waveguide(self):
        position = self.aedtapp.modeler.Position(0, 0, 0)
        assert type(self.aedtapp.modeler.create_waveguide(position, self.aedtapp.CoordinateSystemAxis.XAxis,
                                                          wg_length=2000)) is tuple
        position = self.aedtapp.modeler.Position(0, 0, 0)
        wg9 = self.aedtapp.modeler.create_waveguide(position, self.aedtapp.CoordinateSystemAxis.ZAxis, wgmodel="WG9",
                                                    wg_length=1500, parametrize_h=True, create_sheets_on_openings=True)
        assert wg9[0].id > 0
        assert wg9[1].id > 0
        assert wg9[2].id > 0
        wgfail = self.aedtapp.modeler.create_waveguide(position, self.aedtapp.CoordinateSystemAxis.ZAxis,
                                                       wgmodel="MYMODEL",
                                                       wg_length=2000, parametrize_h=True)
        assert wgfail == None
        pass

    def test_31_set_objects_unmodel(self):
        assert self.aedtapp.modeler.set_object_model_state("Second_airbox", False)

    def test_32_get_object_bounding_box(self):
        id1 = self.aedtapp.modeler.primitives.create_box([10, 10, 10], [4, 5, 5])
        my_pos = self.aedtapp.modeler.get_object_bounding_box(id1)
        assert ((my_pos[0] + my_pos[1] + my_pos[2] - 30) < 1e-5)

    def test_33_duplicate_around_axis(self):
        id1 = self.aedtapp.modeler.primitives.create_box([10, 10, 10], [4, 5, 5])
        axis = self.aedtapp.CoordinateSystemAxis.XAxis
        _, obj_list = self.aedtapp.modeler.duplicate_around_axis(id1, cs_axis=axis, angle="180deg", nclones=2,
                                                                 create_new_objects=False)
        # if create_new_objects is set to False, there should be no new objects
        assert not obj_list

    def test_35_activate_variable_for_tuning(self):
        self.aedtapp["test_opti"]="10mm"
        self.aedtapp["$test_opti1"]="10mm"
        assert self.aedtapp.activate_variable_tuning("test_opti")
        assert self.aedtapp.activate_variable_tuning("$test_opti1", "1mm", "10mm")
        assert self.aedtapp.deactivate_variable_tuning("test_opti")

    def test_36_activate_variable_for_optimization(self):
        assert self.aedtapp.activate_variable_optimization("test_opti")
        assert self.aedtapp.activate_variable_optimization("$test_opti1", "2mm", "5mm")
        assert self.aedtapp.deactivate_variable_optimization("test_opti")

    def test_35_activate_variable_for_sensitivity(self):

        assert self.aedtapp.activate_variable_sensitivity("test_opti")
        assert self.aedtapp.activate_variable_sensitivity("$test_opti1", "1mm", "10mm")
        assert self.aedtapp.deactivate_variable_sensitivity("$test_opti1")

    def test_35_activate_variable_for_statistical(self):

        assert self.aedtapp.activate_variable_statistical("test_opti")
        assert self.aedtapp.activate_variable_statistical("$test_opti1", "1mm", "10mm", "3%", mean="2mm")
        assert self.aedtapp.deactivate_variable_statistical("test_opti")

    def test_36_create_coaxial(self):
        coax = self.aedtapp.modeler.create_coaxial([0, 0, 0], self.aedtapp.CoordinateSystemAxis.XAxis)
        assert isinstance(coax[0].id, int)
        assert isinstance(coax[1].id, int)
        assert isinstance(coax[2].id, int)

    def test_37_create_coordinate(self):
        cs = self.aedtapp.modeler.create_coordinate_system(name='tester')
        assert cs
        assert cs.update()
        assert cs.change_cs_mode(1)
        assert cs.change_cs_mode(2)
        assert not cs.change_cs_mode(3)
        assert cs.change_cs_mode(0)
        assert cs.delete()

    def test_38_rename_coordinate(self):
        cs = self.aedtapp.modeler.create_coordinate_system(name='oldname')
        assert cs.name == 'oldname'
        assert cs.rename('newname')
        assert cs.name == 'newname'

    def test_39_update_coordinate_system(self):
        for cs in self.aedtapp.modeler.coordinate_systems:
            cs.delete()
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="CS1", view="rotate")
        cs2 = self.aedtapp.modeler.create_coordinate_system(name="CS2", mode="view", view="iso")
        cs2.ref_cs = "CS1"
        assert cs2.update()
        cs1.props["OriginX"] = 10
        cs1.props["OriginY"] = 10
        cs1.props["OriginZ"] = 10
        assert cs1.update()
        assert cs2.change_cs_mode(2)
        cs2.props["Phi"] = 30
        cs2.props["Theta"] = 30
        assert cs2.update()
        cs2.ref_cs = "Global"
        cs2.update()
        assert self.aedtapp.modeler.oeditor.GetCoordinateSystems() == ('Global', 'CS1', 'CS2')
        assert len(self.aedtapp.modeler.coordinate_systems) == 2
        assert cs2.delete()

    def test_40_set_as_working_cs(self):
        for cs in self.aedtapp.modeler.coordinate_systems:
            cs.delete()
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="first")
        cs2 = self.aedtapp.modeler.create_coordinate_system(name="second", mode="view", view="iso")
        assert cs1.set_as_working_cs()
        assert cs2.set_as_working_cs()

    def test_41_set_working_coordinate_system(self):
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="new1")
        self.aedtapp.modeler.set_working_coordinate_system("Global")
        self.aedtapp.modeler.set_working_coordinate_system("new1")

    def test_42_sweep_around_axis(self):
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        arrofpos = [udp1, udp2]
        p1 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="poly_vector_1")
        p2 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="poly_vector_2")
        p3 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="poly_vector_3")
        assert self.aedtapp.modeler.sweep_around_axis(p1, self.aedtapp.CoordinateSystemAxis.YAxis)
        assert self.aedtapp.modeler.sweep_around_axis(p2.name, self.aedtapp.CoordinateSystemAxis.YAxis)
        assert self.aedtapp.modeler.sweep_around_axis(p3.id, self.aedtapp.CoordinateSystemAxis.YAxis)
        assert p1.object_type == "Sheet"
        assert p2.object_type == "Sheet"
        assert p3.object_type == "Sheet"
        assert self.aedtapp.modeler.sweep_around_axis(p1, self.aedtapp.CoordinateSystemAxis.ZAxis)
        assert p1.object_type == "Solid"
'''
