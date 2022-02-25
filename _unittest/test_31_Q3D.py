import os

# Setup paths for module imports
from _unittest.conftest import scratch_path, local_path, desktop_version
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
            self.aedtapp = Q3d(specified_version=desktop_version)
            example_project = os.path.join(local_path, "example_models", bondwire_project_name + ".aedt")
            self.test_project = self.local_scratch.copyfile(example_project)
            self.test_matrix = self.local_scratch.copyfile(os.path.join(local_path, "example_models", "q2d_q3d.aedt"))

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        assert self.aedtapp.close_project(self.aedtapp.project_name, saveproject=False)
        self.local_scratch.remove()
        gc.collect()

    def test_01_save(self):
        test_project = os.path.join(self.local_scratch.path, test_project_name + ".aedt")
        self.aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        o = self.aedtapp.modeler.create_cylinder(
            self.aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, matname="brass", name="MyCylinder"
        )
        assert isinstance(o.id, int)

    def test_03_get_properties(self):
        assert self.aedtapp.odefinition_manager
        assert self.aedtapp.omaterial_manager
        assert self.aedtapp.design_file

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()
        sweep = self.aedtapp.create_discrete_sweep(mysetup.name, sweepname="mysweep", freqstart=1, units="GHz")
        assert sweep
        assert sweep.props["RangeStart"] == "1GHz"

        # Create a discrete sweep with the same name of an existing sweep is not possible.
        assert not self.aedtapp.create_discrete_sweep(mysetup.name, sweepname="mysweep", freqstart=1, units="GHz")

    def test_06b_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()
        sweep2 = self.aedtapp.create_frequency_sweep(
            mysetup.name, sweepname="mysweep2", units="GHz", freqstart=1, freqstop=4
        )
        assert sweep2
        assert sweep2.props["RangeEnd"] == "4GHz"

    def test_06c_autoidentify(self):
        assert self.aedtapp.auto_identify_nets()
        pass

    def test_07_create_source_sinks(self):
        source = self.aedtapp.assign_source_to_objectface("MyCylinder", axisdir=0, source_name="Source1")
        sink = self.aedtapp.assign_sink_to_objectface("MyCylinder", axisdir=3, sink_name="Sink1")
        assert source.name == "Source1"
        assert sink.name == "Sink1"
        assert len(self.aedtapp.excitations) > 0

    def test_07B_create_source_tosheet(self):
        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [0, 0, 0], 4, name="Source1")
        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [10, 10, 10], 4, name="Sink1")

        source = self.aedtapp.assign_source_to_sheet("Source1", sourcename="Source3")
        sink = self.aedtapp.assign_sink_to_sheet("Sink1", sinkname="Sink3")
        assert source.name == "Source3"
        assert sink.name == "Sink3"

        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [0, 0, 0], 4, name="Source1")
        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [10, 10, 10], 4, name="Sink1")

        source = self.aedtapp.assign_source_to_sheet("Source1", netname="GND", objectname="Cylinder1")
        sink = self.aedtapp.assign_sink_to_sheet("Sink1", netname="GND", objectname="Cylinder1")
        assert source
        assert sink
        sink.name = "My_new_name"
        assert sink.update()
        assert sink.name == "My_new_name"
        assert len(self.aedtapp.nets) > 0
        assert len(self.aedtapp.net_sources("GND")) > 0
        assert len(self.aedtapp.net_sinks("GND")) > 0
        assert len(self.aedtapp.net_sources("PGND")) == 0
        assert len(self.aedtapp.net_sinks("PGND")) == 0

    def test_08_create_faceted_bondwire(self):
        self.aedtapp.load_project(self.test_project, close_active_proj=True)
        test = self.aedtapp.modeler.create_faceted_bondwire_from_true_surface(
            "bondwire_example", self.aedtapp.AXIS.Z, min_size=0.2, numberofsegments=8
        )
        assert test
        pass

    def test_10_q2d(self):
        q2d = Q2d(specified_version=desktop_version)
        assert q2d
        assert q2d.dim == "2D"
        pass

    def test_11_assign_net(self):
        box = self.aedtapp.modeler.create_box([30, 30, 30], [10, 10, 10], name="mybox")
        net_name = "my_net"
        net = self.aedtapp.assign_net(box, net_name)
        assert net
        assert net.name == net_name
        box = self.aedtapp.modeler.create_box([40, 30, 30], [10, 10, 10], name="mybox2")
        net = self.aedtapp.assign_net(box, None, "Ground")
        assert net
        box = self.aedtapp.modeler.create_box([60, 30, 30], [10, 10, 10], name="mybox3")
        net = self.aedtapp.assign_net(box, None, "Floating")
        assert net
        net.name = "new_net_name"
        assert net.update()
        assert net.name == "new_net_name"

    def test_12_mesh_settings(self):
        assert self.aedtapp.mesh.initial_mesh_settings
        assert self.aedtapp.mesh.initial_mesh_settings.props

    def test_13_matrix_reduction(self):
        q3d = Q3d(self.test_matrix, specified_version="2021.2")
        assert q3d.matrices[0].name == "Original"
        assert len(q3d.matrices[0].sources()) > 0
        assert len(q3d.matrices[0].sources(False)) > 0
        assert q3d.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest")
        assert q3d.matrices[1].name == "JointTest"
        assert q3d.insert_reduced_matrix("JoinParallel", ["Source1", "Source2"], "JointTest2")
        assert q3d.matrices[2].name == "JointTest2"
        assert q3d.insert_reduced_matrix("FloatInfinity", None, "JointTest3")
        assert q3d.matrices[3].name == "JointTest3"
        assert q3d.insert_reduced_matrix(q3d.MATRIXOPERATIONS.MoveSink, "Source2", "JointTest4")
        assert q3d.matrices[4].name == "JointTest4"
        assert q3d.insert_reduced_matrix(q3d.MATRIXOPERATIONS.ReturnPath, "Source2", "JointTest5")
        assert q3d.matrices[5].name == "JointTest5"
        assert q3d.insert_reduced_matrix(q3d.MATRIXOPERATIONS.GroundNet, "Box1", "JointTest6")
        assert q3d.matrices[6].name == "JointTest6"
        assert q3d.insert_reduced_matrix(q3d.MATRIXOPERATIONS.FloatTerminal, "Source2", "JointTest7")
        assert q3d.matrices[7].name == "JointTest7"
        assert q3d.matrices[7].delete()
        assert q3d.matrices[6].add_operation(q3d.MATRIXOPERATIONS.ReturnPath, "Source2")
        full_list = q3d.matrices[0].get_sources_for_plot()
        mutual_list = q3d.matrices[0].get_sources_for_plot(
            get_self_terms=False, category=q3d.matrices[0].CATEGORIES.Q3D.ACL
        )
        assert len(full_list) > len(mutual_list)
        assert q3d.matrices[0].get_sources_for_plot(first_element_filter="Box?", second_element_filter="B*2") == [
            "C(Box1,Box1_2)"
        ]
        self.aedtapp.close_project(q3d.project_name, False)
