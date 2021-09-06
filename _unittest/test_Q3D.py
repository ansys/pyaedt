import os
# Setup paths for module imports
from _unittest.conftest import scratch_path, local_path
import gc
# Import required modules
from pyaedt import Q3d, Q2d
from pyaedt.generic.filesystem import Scratch

test_project_name = "coax_Q3D"
bondwire_project_name = "bondwireq3d"

class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Q3d()
            example_project = os.path.join(
                local_path, 'example_models', bondwire_project_name + '.aedt')
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
        o = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                                     matname="brass", name="MyCylinder")
        assert isinstance(o.id, int)

    def test_03_get_properties(self):
        assert self.aedtapp.odefinition_manager
        assert self.aedtapp.omaterial_manager
        assert self.aedtapp.design_file

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()
        sweep = self.aedtapp.create_discrete_sweep(
            mysetup.name, sweepname="mysweep", freqstart=1, units="GHz")
        assert sweep
        assert sweep.props["RangeStart"] == "1GHz"

    def test_06b_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()
        sweep2 = self.aedtapp.create_frequency_sweep(
            mysetup.name, sweepname="mysweep2",units="GHz",freqstart=1, freqstop=4)
        assert sweep2
        assert sweep2.props["RangeEnd"] == "4GHz"

    def test_07_create_source_sinks(self):
        source = self.aedtapp.assign_source_to_objectface(
            "MyCylinder", axisdir=0, source_name="Source1")
        sink = self.aedtapp.assign_sink_to_objectface("MyCylinder", axisdir=3, sink_name="Sink1")
        assert source.name =="Source1"
        assert sink.name =="Sink1"

    def test_07B_create_source_tosheet(self):
        self.aedtapp.modeler.primitives.create_circle(
            self.aedtapp.CoordinateSystemPlane.XYPlane,[0,0,0],4,name="Source1")
        self.aedtapp.modeler.primitives.create_circle(
            self.aedtapp.CoordinateSystemPlane.XYPlane,[10,10,10],4,name="Sink1")

        source = self.aedtapp.assign_source_to_sheet("Source1", sourcename="Source3")
        sink = self.aedtapp.assign_sink_to_sheet("Sink1", sinkname="Sink3")
        assert source.name =="Source3"
        assert sink.name =="Sink3"

        self.aedtapp.modeler.primitives.create_circle(
            self.aedtapp.CoordinateSystemPlane.XYPlane,[0,0,0],4,name="Source1")
        self.aedtapp.modeler.primitives.create_circle(
            self.aedtapp.CoordinateSystemPlane.XYPlane,[10,10,10],4,name="Sink1")

        source = self.aedtapp.assign_source_to_sheet(
            "Source1", netname="GND", objectname="Cylinder1")
        sink = self.aedtapp.assign_sink_to_sheet("Sink1", netname="GND", objectname="Cylinder1")
        assert source
        assert sink

    def test_08_create_faceted_bondwire(self):
        self.aedtapp.load_project(self.test_project, close_active_proj=True)
        test = self.aedtapp.modeler.create_faceted_bondwire_from_true_surface("bondwire_example",
                                                                              self.aedtapp.CoordinateSystemAxis.ZAxis,
                                                                              min_size=0.2, numberofsegments=8)
        assert test
        pass

    def test_09_autoidentify(self):
        assert self.aedtapp.auto_identify_nets()
        pass

    def test_10_q2d(self):
        q2d = Q2d()
        assert q2d
        assert q2d.dim == '2D'
        pass
