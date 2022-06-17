import os

from _unittest.conftest import BasisTest
from _unittest.conftest import desktop_version
from _unittest.conftest import local_path
from pyaedt import Q2d

test_project_name = "coax_Q2D"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, application=Q2d)
        self.test_matrix = self.local_scratch.copyfile(os.path.join(local_path, "example_models", "q2d_q3d.aedt"))

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_save(self):
        test_project = os.path.join(self.local_scratch.path, test_project_name + ".aedt")
        self.aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.create_rectangle(udp, [5, 3], name="Rectangle1")
        assert isinstance(o.id, int)

    def test_02a_create_rectangle(self):
        o = self.aedtapp.create_rectangle((0, 0), [5, 3], name="Rectangle1")
        assert isinstance(o.id, int)

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()
        sweepName = "Q2D_Sweep1"
        qSweep = mysetup.add_sweep(sweepName)
        assert qSweep.add_subrange("LinearCount", 0.0, 100e6, 10)
        assert qSweep.add_subrange("LinearStep", 100e6, 2e9, 50e6)
        assert qSweep.add_subrange("LogScale", 100, 100e6, 10, clear=True)
        assert qSweep.add_subrange("LinearStep", 100, 100e6, 1e4, clear=True)
        assert qSweep.add_subrange("LinearCount", 100, 100e6, 10, clear=True)

    def test_07_single_signal_line(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.create_rectangle(udp, [5, 3], name="Rectangle1")
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
        q2d = Q2d(self.test_matrix, specified_version=desktop_version)
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

    def test_12_edit_sources(self):
        q2d = Q2d(self.test_matrix, specified_version=desktop_version)
        sources_cg = {"Circle2": ("10V", "45deg"), "Circle3": "4A"}
        assert q2d.edit_sources(sources_cg)

        sources_cg = {"Circle2": "1V", "Circle3": "4A"}
        sources_ac = {"Circle3": "40A"}
        assert q2d.edit_sources(sources_cg, sources_ac)

        sources_cg = {"Circle2": ["10V"], "Circle3": "4A"}
        sources_ac = {"Circle3": ("100A", "5deg")}
        assert q2d.edit_sources(sources_cg, sources_ac)

        sources_ac = {"Circle5": "40A"}
        assert not q2d.edit_sources(sources_cg, sources_ac)
        self.aedtapp.close_project(q2d.project_name, False)

    def test_13_get_all_conductors(self):
        self.aedtapp.insert_design("condcutors")
        o = self.aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", matname="Copper")
        o1 = self.aedtapp.create_rectangle([7, 5], [5, 3], name="Rectangle2", matname="aluminum")
        o3 = self.aedtapp.create_rectangle([27, 5], [5, 3], name="Rectangle3", matname="air")
        conductors = self.aedtapp.get_all_conductors_names()
        assert sorted(conductors) == ["Rectangle1", "Rectangle2"]
        assert self.aedtapp.get_all_dielectrics_names() == ["Rectangle3"]
