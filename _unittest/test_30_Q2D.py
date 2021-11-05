import os

# Setup paths for module imports
from _unittest.conftest import scratch_path
import gc

# Import required modules
from pyaedt import Q2d
from pyaedt.generic.filesystem import Scratch

test_project_name = "coax_Q2D"


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Q2d()

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
        self.aedtapp.assign_single_conductor(target_objects=o, solve_option="SolveOnBoundary")

    def test_08_assign_huray_finitecond_to_edges(self):
        o = self.aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", matname="Copper")
        self.aedtapp.assign_single_conductor(target_objects=o, solve_option="SolveOnBoundary")
        assert self.aedtapp.assign_huray_finitecond_to_edges(o.edges, radius=0.5, ratio=2.9)
