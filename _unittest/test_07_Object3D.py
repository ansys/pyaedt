# standard imports
import os
import math

# Setup paths for module imports
from .conftest import local_path, scratch_path

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
from pyaedt.modeler.Object3d import _to_boolean

import gc

class TestObject3D:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            test_projectfile = os.path.join(self.local_scratch.path, 'test_object3d' + '.aedt')
            self.aedtapp = Hfss()
            self.aedtapp.save_project(project_file=test_projectfile)
            self.prim = self.aedtapp.modeler.primitives

    def teardown_class(self):
        self.aedtapp.close_project(name=self.aedtapp.project_name, saveproject=False)
        self.local_scratch.remove()
        gc.collect()

    def test_01_bounding_box(self):
        id = self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")
        new_object = self.prim[id]
        bb = new_object.bounding_box
        assert len(bb) == 6

    def test_02_face_edge_vertex(self):
        if not self.prim["Mybox"]:
            self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")
        new_object = self.prim["Mybox"]
        object_faces = new_object.faces
        assert len(object_faces) == 6
        for face in object_faces:
            assert len(face.edges) == 4
            assert len(face.normal) == 3

        object_edges = new_object.edges
        for edge in object_edges:
            assert len(edge.vertices) == 2
            assert len(edge.midpoint) == 3

        object_vertices = new_object.vertices
        for vertex in object_vertices:
            assert len(vertex.position) == 3

    def test_03_FacePrimitive(self):
        if not self.prim["Mybox"]:
            self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")
        if not self.prim["MySphere"]:
            self.prim.create_sphere([0, 0, 0], radius="1mm", name="Mysphere", matname="Copper")
        planar_face = self.prim["Mybox"].faces[0]
        assert planar_face.center == [5.0, 5.0, 5.0]
        planar_face.move_with_offset(1)
        assert planar_face.center == [5.0, 5.0, 6.0]
        assert planar_face.normal == [0, 0, 1]
        assert planar_face.area == 100
        non_planar_face = self.prim["Mysphere"].faces[0]
        assert math.isclose(non_planar_face.area, 12.56637061435917)
        assert non_planar_face.move_with_offset(1)
        assert math.isclose(non_planar_face.area, 50.26548245743669)
        assert not non_planar_face.normal

    def test_04_object_material_property(self):
        id1 = self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper1234Invalid")
        assert self.prim[id1].material_name == "vacuum"

        id2 = self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "copper")
        assert self.prim[id2].material_name == "copper"

        # Property Setter with valid material
        self.prim[id2].material_name = "vacuum"
        assert self.prim[id2].material_name == "vacuum"

        # Property Setter with invalid material
        self.prim[id2].material_name = "SteelInvalid"
        assert self.prim[id2].material_name == "vacuum"

        pass

    def test_05_object3d_properties_transparency(self):
        if not self.prim["Mybox"]:
            self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")

        self.prim["Mybox"].transparency = 50
        assert self.prim["Mybox"].transparency == 1.0

        self.prim["Mybox"].transparency = 0.67
        assert self.prim["Mybox"].transparency == 0.67

        self.prim["Mybox"].transparency = 0.0
        assert self.prim["Mybox"].transparency == 0.0

        self.prim["Mybox"].transparency = 1.0
        assert self.prim["Mybox"].transparency == 1.0

        self.prim["Mybox"].transparency = -1
        assert self.prim["Mybox"].transparency == 0.0

    def test_06_object3d_properties_color(self):
        if not self.prim["Mybox"]:
            self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")

        self.prim["Mybox"].color = (0, 0, 255)
        assert self.prim["Mybox"].color == (0, 0, 255)

    def test_07_object_clone_and_get_properties(self):
        if not self.prim["Mybox"]:
            self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")
        initial_object = self.prim["Mybox"]
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

    def test_08_export_attributes(self):
        if not self.prim["Mybox"]:
            self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")
        initial_object = self.prim["Mybox"]
        attr_list = initial_object.export_attributes()
        attr_legacy_list = initial_object.export_attributes_legacy()

        attr_list_name = initial_object.export_attributes("some_name")
        attr_legacy_list_name = initial_object.export_attributes_legacy("some_name")

        assert "some_name" in attr_legacy_list_name
        assert not None in attr_legacy_list
        assert not None in attr_list
        assert "some_name" in attr_list_name

    def test_08_set_model(self):
        if not self.prim["Mybox"]:
            self.prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")
        initial_object = self.prim["Mybox"]
        initial_object.model = False
        initial_object.draw_wireframe = True

    def test_09_to_boolean(self):
        assert _to_boolean(True)
        assert not _to_boolean(False)
        assert _to_boolean("d")
        assert not _to_boolean("f")
        assert not _to_boolean("no")

    def test_10_chamfer(self):
        id = self.prim.create_box([0, 0, 0], [10, 10, 5], "ChamferTest", "Copper")
        initial_object = self.prim[id]
        object_edges = initial_object.edges
        assert len(object_edges) == 12
        test = initial_object.edges[0].chamfer(left_distance=0.2)
        assert test
        test = initial_object.edges[1].chamfer(left_distance=0.2, right_distance=0.4, angle=34, chamfer_type=2)
        assert test
        test = initial_object.edges[2].chamfer(left_distance=0.2, right_distance=0.4, chamfer_type=1)
        assert test
        self.aedtapp.modeler.primitives.delete(initial_object)

    def test_11_fillet(self):
        id = self.prim.create_box([0, 0, 0], [10, 10, 5], "FilletTest", "Copper")
        initial_object = self.prim[id]
        object_edges = initial_object.edges
        assert len(object_edges) == 12
        test = initial_object.edges[0].fillet(radius=0.2)
        assert test
        test = initial_object.edges[1].fillet(radius=0.2, setback=0.1)
        assert not test
        self.aedtapp.modeler.primitives.delete(initial_object)

    def test_12_set_color(self):
        id = self.prim.create_box([0, 0, 0], [10, 10, 5], "ColorTest")
        initial_object = self.prim[id]
        initial_object.color = "Red"
        assert initial_object.color == (255, 0, 0)
        initial_object.color = "Green"
        assert initial_object.color == (0, 128, 0)
        initial_object.color = "Blue"
        assert initial_object.color == (0, 0, 255)
        initial_object.color = (255, 0, 0)
        assert initial_object.color == (255, 0, 0)
        initial_object.color = '(255 0 0)'
        assert initial_object.color == (255, 0, 0)

        initial_object.color = '(300 0 0)'
        assert initial_object.color == (255, 0, 0)

        initial_object.color = '(123 0 0 55)'
        assert initial_object.color == (255, 0, 0)

        initial_object.color = 'InvalidString'
        assert initial_object.color == (255, 0, 0)

        initial_object.color = (255, "Invalid", 0)
        assert initial_object.color == (255, 0, 0)

        self.aedtapp.modeler.primitives.delete("ColorTest")
