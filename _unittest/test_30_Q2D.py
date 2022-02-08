import os

# Setup paths for module imports
from _unittest.conftest import scratch_path, local_path, desktop_version
import gc

# Import required modules
from pyaedt import Q2d
from pyaedt.generic.filesystem import Scratch

test_project_name = "coax_Q2D"


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Q2d(specified_version=desktop_version)
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
        o = self.aedtapp.modeler.primitives.create_rectangle(udp, [5, 3], name="Rectangle1")
        assert isinstance(o.id, int)

    def test_02a_create_rectangle(self):
        o = self.aedtapp.create_rectangle((0, 0), [5, 3], name="Rectangle1")
        assert isinstance(o.id, int)

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()

    def test_07_single_signal_line(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.primitives.create_rectangle(udp, [5, 3], name="Rectangle1")
        assert self.aedtapp.assign_single_conductor(target_objects=o, solve_option="SolveOnBoundary")

    def test_08_assign_huray_finitecond_to_edges(self):
        o = self.aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", matname="Copper")
        self.aedtapp.assign_single_conductor(target_objects=o, solve_option="SolveOnBoundary")
        assert self.aedtapp.assign_huray_finitecond_to_edges(o.edges, radius=0.5, ratio=2.9)

    def test_09_auto_assign(self):
        self.aedtapp.insert_design("test_auto")
        o = self.aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", matname="Copper")
        o = self.aedtapp.create_rectangle([0, 0], [5, 3], name="Rectangle2", matname="Copper")
        assert self.aedtapp.auto_assign_conductors()
        assert len(self.aedtapp.boundaries) == 2

    def test_10_toggle_condcutor(self):
        assert self.aedtapp.toggle_conductor_type("Rectangle1", "ReferenceGround")
        assert not self.aedtapp.toggle_conductor_type("Rectangle3", "ReferenceGround")
        assert not self.aedtapp.toggle_conductor_type("Rectangle2", "ReferenceggGround")

    def test_11_matrix_reduction(self):
        q2d = Q2d(self.test_matrix, specified_version="2021.2")
        assert q2d.matrices[0].name == "Original"
        assert len(q2d.matrices[0].sources()) > 0
        assert len(q2d.matrices[0].sources(False)) > 0
        assert q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Float, "Circle2", "Test1")
        assert q2d.matrices[1].name == "Test1"
        assert q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.AddGround, "Circle2", "Test2")
        assert q2d.matrices[2].name == "Test2"
        assert q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.SetReferenceGround, "Circle2", "Test3")
        assert q2d.matrices[3].name == "Test3"
        assert q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Parallel, ["Circle2", "Circle3"], "Test4")
        assert q2d.matrices[4].name == "Test4"
        assert q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.DiffPair, ["Circle2", "Circle3"], "Test5")
        assert q2d.matrices[5].name == "Test5"
        self.aedtapp.close_project(q2d.project_name, False)
