# standard imports
import gc
import math
import os

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
from pyaedt.generic.general_methods import isclose, time_fn
from pyaedt.modeler.Object3d import FacePrimitive, _to_boolean, _uname

from _unittest.conftest import scratch_path


class TestClass:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            test_projectfile = os.path.join(self.local_scratch.path, "test_object3d" + ".aedt")
            self.aedtapp = Hfss()
            self.aedtapp.save_project(project_file=test_projectfile)
            self.prim = self.aedtapp.modeler.primitives

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        self.aedtapp.close_project(name=self.aedtapp.project_name, saveproject=False)
        self.local_scratch.remove()
        gc.collect()

    def create_example_coil(self, name=None):
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

        if self.aedtapp.modeler.primitives[name]:
            self.aedtapp.modeler.primitives.delete(name)
        return self.aedtapp.modeler.primitives.create_polyline(position_list=pointsList1, name=name)

    def create_copper_box(self, name=None):
        if not name:
            name = "MyBox"
        o = self.aedtapp.modeler.primitives[name]
        if not o:
            o = self.aedtapp.modeler.primitives.create_box([0, 0, 0], [10, 10, 5], name, "Copper")
        return o

    def create_copper_box_test_performance(self):
        for o in range(10):
            o = self.aedtapp.modeler.primitives.create_box([0, 0, 0], [10, 10, 5], "MyboxLoop", "Copper")

    def create_copper_sphere(self, name=None):
        if not name:
            name = "Mysphere"
        if self.aedtapp.modeler.primitives[name]:
            self.aedtapp.modeler.primitives.delete(name)
        return self.aedtapp.modeler.primitives.create_sphere([0, 0, 0], radius=4, name=name, matname="Copper")

    def create_copper_cylinder(self, name=None):
        if not name:
            name = "MyCyl"
        if self.aedtapp.modeler.primitives[name]:
            self.aedtapp.modeler.primitives.delete(name)
        return self.aedtapp.modeler.primitives.create_cylinder(
            cs_axis="Y", position=[0, 0, 0], radius=1, height=20, numSides=8, name=name, matname="Copper"
        )

    def test_00_uname(self):
        test = _uname()
        assert test.startswith("NewObject")

    def test_00_object_performance(self):
        time_fn(self.create_copper_box_test_performance)

    def test_01_bounding_box(self):
        o = self.create_copper_box()
        a = o.color
        bb = o.bounding_box
        assert len(bb) == 6

    def test_01_delete_object(self):
        o = self.create_copper_box("DeleteBox")
        name = o.name
        o.delete()
        assert not self.aedtapp.modeler.primitives[name]
        assert not o.__dict__

    def test_01_subtract_object(self):
        o1 = self.create_copper_box("subtract_box")
        o2 = self.create_copper_sphere("subtract_sphere")
        o3 = self.create_copper_cylinder("subtract_cylinder")

        a = o1.clone()
        a.subtract(o2)

        b = o1.clone()
        b.subtract([o2, o3])

        assert len(a.faces) == 7
        assert len(b.faces) == 9

    def test_02_face_edge_vertex(self):
        o = self.create_copper_box("faces_box")
        object_faces = o.faces
        assert len(object_faces) == 6
        for face in object_faces:
            assert len(face.edges) == 4
            assert len(face.normal) == 3

        object_edges = o.edges
        for edge in object_edges:
            assert len(edge.vertices) == 2
            assert len(edge.midpoint) == 3

        object_vertices = o.vertices
        for vertex in object_vertices:
            assert len(vertex.position) == 3

    def test_03_FacePrimitive(self):
        o_box = self.create_copper_box("PrimitiveBox")
        o_sphere = self.create_copper_sphere("PrimitiveSphere")
        planar_face = o_box.faces[0]
        assert planar_face.center == [5.0, 5.0, 5.0]
        planar_face.move_with_offset(1)
        assert planar_face.center == [5.0, 5.0, 6.0]
        assert planar_face.normal == [0, 0, 1]
        assert planar_face.area == 100
        non_planar_face = o_sphere.faces[0]
        assert isclose(non_planar_face.area, 201.06192982974676)
        assert non_planar_face.move_with_offset(1)
        assert isclose(non_planar_face.area, 314.1592653589793)
        assert not non_planar_face.normal

    def test_04_object_material_property_invalid(self):
        o_box = self.create_copper_box("Invalid1")
        o_box.material_name = "Copper1234Invalid"
        assert o_box.material_name == "copper"

    def test_04_object_material_property_valid(self):
        o_box = self.create_copper_box("Valid2")
        o_box.material_name = "aluminum"
        assert o_box.material_name == "aluminum"

    def test_05_object3d_properties_transparency(self):
        o = self.create_copper_box("TransparencyBox")

        o.transparency = 50
        assert o.transparency == 1.0

        o.transparency = 0.67
        assert o.transparency == 0.67

        o.transparency = 0.0
        assert o.transparency == 0.0

        o.transparency = 1.0
        assert o.transparency == 1.0

        o.transparency = -1
        assert o.transparency == 0.0

    def test_06_object3d_properties_color(self):
        o = self.create_copper_box("color_box")
        o.color = (0, 0, 255)
        assert o.color == (0, 0, 255)

    def test_07_object_clone_and_get_properties(self):
        o = self.create_copper_box("Properties_Box")
        initial_object = o
        initial_object.transparency = 0.76
        new_object = initial_object.clone()
        assert new_object.name != initial_object.name
        assert new_object.material_name == initial_object.material_name
        assert new_object.solve_inside == initial_object.solve_inside
        assert new_object.model == initial_object.model
        assert new_object.display_wireframe == initial_object.display_wireframe
        assert new_object.part_coordinate_system == initial_object.part_coordinate_system
        assert new_object.transparency == 0.76
        assert new_object.color == initial_object.color
        assert new_object.bounding_box == initial_object.bounding_box
        assert len(new_object.vertices) == 8
        assert len(new_object.faces) == 6
        assert len(new_object.edges) == 12
        assert new_object.display_wireframe == initial_object.display_wireframe

    def test_08_set_model(self):
        o = self.create_copper_box()
        initial_object = o
        initial_object.model = False
        initial_object.draw_wireframe = True

    def test_08A_top_face(self):
        o = self.create_copper_box()
        assert isinstance(o.top_face_x, FacePrimitive)
        assert isinstance(o.top_face_y, FacePrimitive)
        assert isinstance(o.top_face_z, FacePrimitive)

    def test_08B_bottom_face(self):
        o = self.create_copper_box()
        assert isinstance(o.bottom_face_x, FacePrimitive)
        assert isinstance(o.bottom_face_y, FacePrimitive)
        assert isinstance(o.bottom_face_z, FacePrimitive)

    def test_09_to_boolean(self):
        assert _to_boolean(True)
        assert not _to_boolean(False)
        assert _to_boolean("d")
        assert not _to_boolean("f")
        assert not _to_boolean("no")

    def test_10_chamfer(self):
        initial_object = self.prim.create_box([0, 0, 0], [10, 10, 5], "ChamferTest", "Copper")
        object_edges = initial_object.edges
        assert len(object_edges) == 12
        test = initial_object.edges[0].chamfer(left_distance=0.2)
        assert test
        test = initial_object.edges[1].chamfer(left_distance=0.2, right_distance=0.4, angle=34, chamfer_type=2)
        assert test
        test = initial_object.edges[2].chamfer(left_distance=0.2, right_distance=0.4, chamfer_type=1)
        assert test
        # TODO Angle as string - general refactor !
        test = initial_object.edges[6].chamfer(left_distance=1, angle=45, chamfer_type=3)
        assert test
        test = initial_object.edges[4].chamfer(chamfer_type=4)
        assert not test

        self.aedtapp.modeler.primitives.delete(initial_object)

    def test_11_fillet(self):
        initial_object = self.prim.create_box([0, 0, 0], [10, 10, 5], "FilletTest", "Copper")
        object_edges = initial_object.edges
        assert len(object_edges) == 12
        test = initial_object.edges[0].fillet(radius=0.2)
        assert test
        test = initial_object.edges[1].fillet(radius=0.2, setback=0.1)
        assert not test
        self.aedtapp.modeler.primitives.delete(initial_object)

    def test_object_length(self):
        initial_object = self.prim.create_box([0, 0, 0], [10, 10, 5], "FilletTest", "Copper")
        test_edge = initial_object.edges[0]
        assert isinstance(test_edge.length, float)

        start_point = initial_object.edges[0].vertices[0]
        end_point = initial_object.edges[0].vertices[1]
        sum_sq = 0
        for i in range(0, 3):
            sum_sq += (end_point.position[i] - start_point.position[i]) ** 2
        assert isclose(math.sqrt(sum_sq), test_edge.length)
        self.aedtapp.modeler.primitives.delete(initial_object)

    def test_12_set_color(self):
        initial_object = self.prim.create_box([0, 0, 0], [10, 10, 5], "ColorTest")
        initial_object.color = "Red"
        assert initial_object.color == (255, 0, 0)
        initial_object.color = "Green"
        assert initial_object.color == (0, 128, 0)
        initial_object.color = "Blue"
        assert initial_object.color == (0, 0, 255)
        initial_object.color = (255, 0, 0)
        assert initial_object.color == (255, 0, 0)
        initial_object.color = "(255 0 0)"
        assert initial_object.color == (255, 0, 0)

        initial_object.color = "(300 0 0)"
        assert initial_object.color == (255, 0, 0)

        initial_object.color = "(123 0 0 55)"
        assert initial_object.color == (255, 0, 0)

        initial_object.color = "InvalidString"
        assert initial_object.color == (255, 0, 0)

        initial_object.color = (255, "Invalid", 0)
        assert initial_object.color == (255, 0, 0)

        self.aedtapp.modeler.primitives.delete("ColorTest")

    def test_print_object(self):
        o = self.create_copper_box()
        assert o.name in o.__str__()
        test_face = o.faces[0]
        assert "FaceId" in test_face.__repr__()
        assert "FaceId" in test_face.__str__()
        test_edge = test_face.edges[0]
        assert "EdgeId" in test_edge.__repr__()
        assert "EdgeId" in test_edge.__str__()
        test_vertex = test_face.vertices[0]
        assert "Vertex" in test_vertex.__repr__()
        assert "Vertex" in test_vertex.__str__()

    def test_13_delete_self(self):
        o = self.create_copper_box()
        my_name = o.name
        assert my_name in self.aedtapp.modeler.primitives.object_names
        o.delete()
        assert my_name not in self.aedtapp.modeler.primitives.object_names

    def test_14_translate_delete_self(self):
        o = self.create_copper_box()
        v0 = o.vertices[0].position
        o.translate([1, 0, 0])
        v1 = o.vertices[0].position
        assert v1[0] == v0[0] + 1.0
        assert v1[1] == v0[1]
        assert v1[2] == v0[2]

    def test_15_duplicate_around_axis_and_unite(self):
        turn = self.create_example_coil("single_turn")
        added_objects = turn.duplicate_around_axis(cs_axis="Z", angle=8, nclones=19)
        turn.unite(added_objects)
        assert len(added_objects) == 18
        assert "single_turn" in self.aedtapp.modeler.primitives.line_names

    def test_16_duplicate_around_axis_and_unite(self):
        turn = self.create_example_coil("single_turn")
        added_objects = turn.duplicate_along_line([0, 0, 15], nclones=3, attachObject=False)
        assert len(added_objects) == 2
        assert "single_turn" in self.aedtapp.modeler.primitives.line_names

    # TODO: Finish asserts anc check the boolean inputs - they are not present in the GUI ??
    def test_17_section_object(self):
        o = self.aedtapp.modeler.primitives.create_box([-10, 0, 0], [10, 10, 5], "SectionBox", "Copper")
        o.section(plane="YZ", create_new=True, section_cross_object=False)
