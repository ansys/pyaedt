# standard imports
import os
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



