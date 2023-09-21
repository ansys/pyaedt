import os

from _unittest.conftest import config
from _unittest.conftest import desktop_version
from _unittest.conftest import local_path
import pytest

from pyaedt import Q2d

test_project_name = "coax_Q2D"
test_subfolder = "T30"
if desktop_version > "2022.2":
    q2d_q3d = "q2d_q3d_231"

else:
    q2d_q3d = "q2d_q3d"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(application=Q2d)
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    test_matrix = local_scratch.copyfile(os.path.join(local_path, "example_models", test_subfolder, q2d_q3d + ".aedt"))
    return test_matrix, None


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, examples, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch
        self.test_matrix = examples[0]

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
        assert self.aedtapp.boundaries[0].object_properties
        assert len(self.aedtapp.boundaries) == 2

    def test_10_toggle_conductor(self):
        assert self.aedtapp.toggle_conductor_type("Rectangle1", "ReferenceGround")
        assert not self.aedtapp.toggle_conductor_type("Rectangle3", "ReferenceGround")
        assert not self.aedtapp.toggle_conductor_type("Rectangle2", "ReferenceggGround")

    def test_11_matrix_reduction(self, add_app):
        q2d = add_app(application=Q2d, project_name=self.test_matrix, just_open=True)
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
        q2d.matrices[4].delete()
        assert q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Parallel, ["Circle2", "Circle3"], "Test4", "New_net")
        assert q2d.matrices[4].name == "Test4"
        assert q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.DiffPair, ["Circle2", "Circle3"], "Test5", "New_net")
        assert q2d.matrices[5].name == "Test5"
        self.aedtapp.close_project(q2d.project_name, save_project=False)

    def test_12_edit_sources(self, add_app):
        q2d = add_app(application=Q2d, project_name=self.test_matrix, just_open=True)
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
        self.aedtapp.close_project(q2d.project_name, save_project=False)

    def test_13_get_all_conductors(self):
        self.aedtapp.insert_design("condcutors")
        o = self.aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", matname="Copper")
        o1 = self.aedtapp.create_rectangle([7, 5], [5, 3], name="Rectangle2", matname="aluminum")
        o3 = self.aedtapp.create_rectangle([27, 5], [5, 3], name="Rectangle3", matname="air")
        conductors = self.aedtapp.get_all_conductors_names()
        assert sorted(conductors) == ["Rectangle1", "Rectangle2"]
        assert self.aedtapp.get_all_dielectrics_names() == ["Rectangle3"]

    def test_14_export_matrix_data(self, add_app):
        q2d = add_app(application=Q2d, project_name=self.test_matrix, just_open=True)
        q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Float, "Circle2", "Test1")
        q2d.matrices[1].name == "Test1"
        q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.AddGround, "Circle2", "Test2")
        q2d.matrices[2].name == "Test2"
        q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.SetReferenceGround, "Circle2", "Test3")
        q2d.matrices[3].name == "Test3"
        q2d.analyze_setup(q2d.active_setup)
        q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"))
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), problem_type="CG")
        assert q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"),
            problem_type="CG",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert not q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"),
            problem_type="RL",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"), problem_type="RL", matrix_type="Maxwell, Couple"
        )
        assert q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"), problem_type="CG", setup_name="Setup1", sweep="Sweep1"
        )
        assert q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"),
            problem_type="CG",
            setup_name="Setup1",
            sweep="LastAdaptive",
        )
        assert q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"), problem_type="CG", reduce_matrix="Test1"
        )
        assert q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"), problem_type="CG", reduce_matrix="Test3"
        )
        assert not q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"), problem_type="CG", reduce_matrix="Test4"
        )
        assert q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"), precision=16, field_width=22
        )
        assert not q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), precision=16.2)
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), freq="1", freq_unit="GHz")
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), freq="3", freq_unit="GHz")
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), freq="3", freq_unit="Hz")
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), use_sci_notation=True)
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), use_sci_notation=False)
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), r_unit="mohm")
        assert not q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), r_unit="A")
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), l_unit="nH")
        assert not q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), l_unit="A")
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), c_unit="farad")
        assert not q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), c_unit="H")
        assert q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), g_unit="fSie")
        assert not q2d.export_matrix_data(os.path.join(self.local_scratch.path, "test_2d.txt"), g_unit="A")
        self.aedtapp.close_project(q2d.project_name, save_project=True)

    def test_15_export_equivalent_circuit(self, add_app):
        q2d = add_app(application=Q2d, project_name=self.test_matrix, just_open=True)
        q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Float, "Circle2", "Test4")
        assert q2d.matrices[4].name == "Test4"
        assert len(q2d.setups[0].sweeps[0].frequencies) > 0
        assert q2d.setups[0].sweeps[0].basis_frequencies == []
        assert q2d.export_equivalent_circuit(os.path.join(self.local_scratch.path, "test_export_circuit.cir"))
        assert not q2d.export_equivalent_circuit(os.path.join(self.local_scratch.path, "test_export_circuit.doc"))
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup_name="Setup1",
            sweep="LastAdaptive",
        )
        assert not q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), setup_name="Setup2"
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup_name="Setup1",
            sweep="LastAdaptive",
            variations=["r1:0.3mm"],
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup_name="Setup1",
            sweep="LastAdaptive",
            variations=[" r1 : 0.3 mm "],
        )
        assert not q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup_name="Setup1",
            sweep="LastAdaptive",
            variations="r1:0.3mm",
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix_name="Original"
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix_name="Test1"
        )
        assert not q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=2
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=0
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=1
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            coupling_limit_type=0,
            res_limit="6Mohm",
            ind_limit="12nH",
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), lumped_length="34mm"
        )
        assert not q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), lumped_length="34nounits"
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            rise_time_value="1e-6",
            rise_time_unit="s",
        )
        assert not q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            rise_time_value="23",
            rise_time_unit="m",
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), file_type="WELement"
        )
        assert not q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), file_type="test"
        )
        assert q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), model_name=q2d_q3d
        )
        assert not q2d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), model_name="test"
        )
        self.aedtapp.close_project(q2d.project_name, save_project=False)

    def test_16_export_results_q2d(self, add_app):
        q2d = add_app(application=Q2d, project_name=self.test_matrix, just_open=True)
        exported_files = q2d.export_results(analyze=True)
        assert len(exported_files) > 0
        self.aedtapp.close_project(q2d.project_name, save_project=False)

    def test_17_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    def test_18_import_dxf(self):
        self.aedtapp.insert_design("dxf")
        dxf_file = os.path.join(local_path, "example_models", "cad", "DXF", "dxf2.dxf")
        dxf_layers = self.aedtapp.get_dxf_layers(dxf_file)
        assert isinstance(dxf_layers, list)
        assert self.aedtapp.import_dxf(dxf_file, dxf_layers)
