import os
# Setup paths for module imports
from .conftest import scratch_path, local_path
import gc
# Import required modules
from pyaedt.core import Q3d
from pyaedt.core.generic.filesystem import Scratch

test_project_name = "coax_Q3D"
bondwire_project_name = "bondwireq3d"

class TestQ3D:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Q3d()
            example_project = os.path.join(local_path, 'example_models', bondwire_project_name + '.aedt')
            self.test_project = self.local_scratch.copyfile(example_project)

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_save(self):
        test_project = os.path.join(self.local_scratch.path, test_project_name + ".aedt")
        self.aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        id1 = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                                     matname="brass", name="MyCylinder")
        assert isinstance(id1, int)


    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()


    def test_07_create_source_sinks(self):
        source = self.aedtapp.assign_source_to_objectface("MyCylinder", axisdir=0, source_name="Source1")
        sink = self.aedtapp.assign_sink_to_objectface("MyCylinder", axisdir=3, sink_name="Sink1")
        assert source.name =="Source1"
        assert sink.name =="Sink1"

    def test_08_create_source_sinks(self):
        self.aedtapp.load_project(self.test_project, close_active_proj=True)
        assert self.aedtapp.modeler.create_faceted_bondwire_from_true_surface("bondwire_example",
                                                                              self.aedtapp.CoordinateSystemAxis.ZAxis,
                                                                              min_size=0.2, numberofsegments=8)
        pass



