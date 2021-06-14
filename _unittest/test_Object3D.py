# standard imports
import os
import math

# Setup paths for module imports
from .conftest import local_path, scratch_path

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch

import gc

class TestObject3D:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            test_projectfile = os.path.join(self.local_scratch.path, 'test_object3d' + '.aedt')
            self.aedtapp = Hfss(AlwaysNew=False)
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



