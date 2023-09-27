import os

from _unittest_solvers.conftest import desktop_version
from _unittest_solvers.conftest import local_path
import pytest

from pyaedt import Q3d

test_project_name = "coax_Q3D"
if desktop_version > "2022.2":
    bondwire_project_name = "bondwireq3d_231.aedt"
    q2d_q3d = "q2d_q3d_231"

else:
    bondwire_project_name = "bondwireq3d.aedt"
    q2d_q3d = "q2d_q3d"

test_subfolder = "T31"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(application=Q3d)
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    example_project = os.path.join(local_path, "../_unittest_solvers/example_models", test_subfolder, bondwire_project_name)
    test_project = local_scratch.copyfile(example_project)
    test_matrix = local_scratch.copyfile(os.path.join(local_path, "../_unittest_solvers/example_models", test_subfolder, q2d_q3d + ".aedt"))
    return test_project, test_matrix


class TestClass:

    @pytest.fixture(autouse=True)
    def init(self, aedtapp, examples, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch
        self.test_project = examples[0]
        self.test_matrix = examples[1]

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
        assert mysetup.dc_enabled
        mysetup.dc_resistance_only = True
        assert mysetup.dc_resistance_only
        mysetup.dc_enabled = False
        mysetup.dc_enabled = True
        sweep = self.aedtapp.create_discrete_sweep(mysetup.name, sweepname="mysweep", freqstart=1, units="GHz")
        assert sweep
        assert sweep.props["RangeStart"] == "1GHz"

        # Create a discrete sweep with the same name of an existing sweep is not possible.
        assert not self.aedtapp.create_discrete_sweep(mysetup.name, sweepname="mysweep", freqstart=1, units="GHz")
        assert mysetup.create_linear_step_sweep(
            sweepname="StepFast",
            unit="GHz",
            freqstart=1,
            freqstop=20,
            step_size=0.1,
            sweep_type="Interpolating",
        )
        assert mysetup.create_single_point_sweep(
            save_fields=True,
        )
        assert mysetup.create_frequency_sweep(
            unit="GHz",
            sweepname="Sweep1",
            freqstart=9.5,
            freqstop="10.5GHz",
            sweep_type="Interpolating",
        )

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
        assert self.aedtapp.delete_all_nets()
        assert self.aedtapp.auto_identify_nets()
        pass

    def test_07_create_source_sinks(self):
        source = self.aedtapp.source("MyCylinder", axisdir=0, name="Source1")
        sink = self.aedtapp.sink("MyCylinder", axisdir=3, name="Sink1")
        assert source.name == "Source1"
        assert sink.name == "Sink1"
        assert len(self.aedtapp.excitations) > 0

    def test_07B_create_source_tosheet(self):
        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [0, 0, 0], 4, name="Source1")
        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [10, 10, 10], 4, name="Sink1")

        source = self.aedtapp.source("Source1", name="Source3")
        sink = self.aedtapp.sink("Sink1", name="Sink3")
        assert source.name == "Source3"
        assert sink.name == "Sink3"
        assert source.props["TerminalType"] == "ConstantVoltage"
        assert sink.props["TerminalType"] == "ConstantVoltage"

        self.aedtapp.modeler.delete("Source1")
        self.aedtapp.modeler.delete("Sink1")
        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [0, 0, 0], 4, name="Source1")
        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [10, 10, 10], 4, name="Sink1")
        source = self.aedtapp.source("Source1", name="Source3", terminal_type="current")
        sink = self.aedtapp.sink("Sink1", name="Sink3", terminal_type="current")
        assert source.props["TerminalType"] == "UniformCurrent"
        assert sink.props["TerminalType"] == "UniformCurrent"

        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [0, 0, 0], 4, name="Source1")
        self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, [10, 10, 10], 4, name="Sink1")

        source = self.aedtapp.source(["Source1", "Sink1"], net_name="GND", name="Cylinder1")
        source.props["Objects"] = ["Source1"]
        sink = self.aedtapp.sink("Sink1", net_name="GND")
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
        obj_list = self.aedtapp.objects_from_nets(self.aedtapp.nets[0])
        assert len(obj_list[self.aedtapp.nets[0]]) > 0
        obj_list = self.aedtapp.objects_from_nets(self.aedtapp.nets[0], "steel")
        assert len(obj_list[self.aedtapp.nets[0]]) == 0

    def test_08_create_faceted_bondwire(self):
        self.aedtapp.load_project(self.test_project, close_active_proj=True, save_active_project=False)
        test = self.aedtapp.modeler.create_faceted_bondwire_from_true_surface(
            "bondwire_example", self.aedtapp.AXIS.Z, min_size=0.2, numberofsegments=8
        )
        assert test
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

    def test_11a_set_material_thresholds(self):
        assert self.aedtapp.set_material_thresholds()
        insulator_threshold = 2000
        perfect_conductor_threshold = 2e30
        magnetic_threshold = 3
        assert self.aedtapp.set_material_thresholds(
            insulator_threshold, perfect_conductor_threshold, magnetic_threshold
        )
        insulator_threshold = 2000
        perfect_conductor_threshold = 200
        magnetic_threshold = 3
        assert not self.aedtapp.set_material_thresholds(
            insulator_threshold, perfect_conductor_threshold, magnetic_threshold
        )

    def test_12_mesh_settings(self):
        assert self.aedtapp.mesh.initial_mesh_settings
        assert self.aedtapp.mesh.initial_mesh_settings.props

    def test_13_matrix_reduction(self, add_app):
        q3d = add_app(application=Q3d, project_name=self.test_matrix, just_open=True)
        assert q3d.matrices[0].name == "Original"
        assert len(q3d.matrices[0].sources()) > 0
        assert len(q3d.matrices[0].sources(False)) > 0
        assert q3d.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest")
        assert q3d.matrices[1].name == "JointTest"
        q3d.matrices[1].delete()
        assert q3d.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest", "New_net")
        assert "New_net" in q3d.matrices[1].sources()
        assert q3d.insert_reduced_matrix("JoinParallel", ["Source1", "Source2"], "JointTest2")
        assert q3d.matrices[2].name == "JointTest2"
        assert q3d.matrices[2].delete()
        assert q3d.insert_reduced_matrix("JoinParallel", ["Box1", "Box1_1"], "JointTest2")
        assert q3d.matrices[2].name == "JointTest2"
        assert q3d.matrices[2].delete()
        assert q3d.insert_reduced_matrix(
            "JoinParallel", ["Box1", "Box1_1"], "JointTest2", "New_net", "New_source", "New_sink"
        )
        assert "New_net" in q3d.matrices[2].sources()
        assert q3d.matrices[2].add_operation(q3d.MATRIXOPERATIONS.JoinParallel, ["Box1_2", "New_net"])
        assert len(q3d.matrices[2].operations) == 2
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
        assert q3d.get_traces_for_plot() == q3d.matrices[0].get_sources_for_plot()
        assert len(full_list) > len(mutual_list)
        assert q3d.matrices[0].get_sources_for_plot(first_element_filter="Box?", second_element_filter="B*2") == [
            "C(Box1,Box1_2)"
        ]
        self.aedtapp.close_project(q3d.project_name, save_project=False)

    def test_14_edit_sources(self, add_app):
        q3d = add_app(application=Q3d, project_name=self.test_matrix, just_open=True)
        sources_cg = {"Box1": ("2V", "45deg"), "Box1_2": "4V"}
        sources_ac = {"Box1:Source1": "2A"}
        assert q3d.edit_sources(sources_cg, sources_ac)

        sources_cg = {"Box1": ("20V", "15deg"), "Box1_2": "40V"}
        sources_ac = {"Box1:Source1": "2A", "Box1_1:Source2": "20A"}
        sources_dc = {"Box1:Source1": "20V"}
        assert q3d.edit_sources(sources_cg, sources_ac, sources_dc)

        sources_cg = {"Box1": "2V"}
        sources_ac = {"Box1:Source1": "2", "Box1_1:Source2": "5V"}
        assert q3d.edit_sources(sources_cg, sources_ac)

        sources_cg = {"Box1": ["20V"], "Box1_2": "4V"}
        sources_ac = {"Box1:Source1": "2A"}
        assert q3d.edit_sources(sources_cg, sources_ac)

        sources_dc = {"Box1:Source1": "20"}
        assert q3d.edit_sources(dcrl=sources_dc)

        sources_cg = {"Box2": "2V"}
        assert not q3d.edit_sources(sources_cg)
        sources_ac = {"Box1:Source2": "2V"}
        assert not q3d.edit_sources(sources_ac)
        sources_dc = {"Box1:Source2": "2V"}
        assert not q3d.edit_sources(sources_dc)
        sources = q3d.get_all_sources()
        assert sources[0] == "Box1:Source1"
        self.aedtapp.close_project(q3d.project_name, save_project=False)

    def test_15_export_matrix_data(self, add_app):
        q3d = add_app(application=Q3d, project_name=self.test_matrix, just_open=True)
        q3d.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest")
        q3d.matrices[1].name == "JointTest"
        q3d.insert_reduced_matrix("JoinParallel", ["Source1", "Source2"], "JointTest2")
        q3d.matrices[2].name == "JointTest2"
        q3d.insert_reduced_matrix("FloatInfinity", None, "JointTest3")
        q3d.matrices[3].name == "JointTest3"
        sweep = q3d.setups[0].add_sweep()
        q3d.analyze_setup(q3d.active_setup, num_cores=6)
        assert len(sweep.frequencies) > 0
        assert sweep.basis_frequencies == []
        assert q3d.export_matrix_data(os.path.join(self.local_scratch.path, "test.txt"))
        assert not q3d.export_matrix_data(os.path.join(self.local_scratch.path, "test.pdf"))
        assert not q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), matrix_type="Test"
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"),
            problem_type="C",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"),
            problem_type="C",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert not q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"),
            problem_type="AC RL, DC RL",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), problem_type="AC RL, DC RL"
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"),
            problem_type="AC RL, DC RL",
            matrix_type="Maxwell, Couple",
        )
        assert not q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"),
            problem_type="AC",
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), setup_name="Setup1", sweep="LastAdaptive"
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), setup_name="Setup1", sweep="Last Adaptive"
        )
        assert not q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), setup_name="Setup", sweep="LastAdaptive"
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), reduce_matrix="Original"
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), reduce_matrix="JointTest"
        )
        assert not q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), reduce_matrix="JointTest4"
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"),
            setup_name="Setup1",
            sweep="LastAdaptive",
            freq=1,
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"),
            setup_name="Setup1",
            sweep="LastAdaptive",
            freq=1,
            freq_unit="kHz",
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), precision=16, field_width=22
        )
        assert not q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), precision=16.2)
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), use_sci_notation=True
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), use_sci_notation=False
        )
        assert q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), r_unit="mohm")
        assert not q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), r_unit="A")
        assert q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), l_unit="nH")
        assert not q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), l_unit="A")
        assert q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), c_unit="farad")
        assert not q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), c_unit="H")
        assert q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), g_unit="fSie")
        assert not q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), g_unit="A")
        self.aedtapp.close_project(q3d.project_name, save_project=False)

    def test_16_export_equivalent_circuit(self, add_app):
        test_matrix2 = self.local_scratch.copyfile(
            os.path.join(local_path, "../_unittest_solvers/example_models", test_subfolder, q2d_q3d + ".aedt"),
            os.path.join(self.local_scratch.path, "test_14.aedt"),
        )
        q3d = add_app(application=Q3d, project_name=test_matrix2, just_open=True)
        q3d.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest")
        assert q3d.matrices[1].name == "JointTest"
        q3d["d"] = "10mm"
        q3d.modeler.duplicate_along_line(objid="Box1", vector=[0, "d", 0])
        q3d.analyze_setup(q3d.active_setup, num_cores=6)
        assert q3d.export_equivalent_circuit(
            os.path.join(self.local_scratch.path, "test_export_circuit.cir"), variations=["d: 10mm"]
        )
        assert not q3d.export_equivalent_circuit(os.path.join(self.local_scratch.path, "test_export_circuit.doc"))

        assert not q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup_name="Setup1",
            sweep="LastAdaptive",
            variations=["c: 10mm", "d: 20mm"],
        )

        assert not q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), setup_name="Setup2"
        )
        assert not q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup_name="Setup1",
            sweep="Sweep1",
        )
        assert q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix_name="Original"
        )
        assert q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix_name="JointTest"
        )
        assert not q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix_name="JointTest1"
        )
        assert not q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=2
        )
        assert q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=0
        )
        assert q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=1
        )
        assert q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            coupling_limit_type=0,
            cond_limit="3Sie",
            cap_limit="4uF",
            ind_limit="9uH",
            res_limit="2ohm",
        )
        assert q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), model_name="test_14"
        )
        assert not q3d.export_equivalent_circuit(
            file_name=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), model_name="test"
        )
        self.aedtapp.close_project(q3d.project_name, save_project=False)

    def test_17_export_results_q3d(self, add_app):
        q3d = add_app(application=Q3d, project_name=self.test_matrix, just_open=True)
        exported_files = q3d.export_results()
        assert len(exported_files) == 0
        for setup_name in q3d.setup_names:
            q3d.analyze_setup(setup_name, num_cores=6)
        exported_files = q3d.export_results()
        assert len(exported_files) > 0
        q3d.setups[0].add_sweep()
        q3d.analyze(num_cores=6)
        exported_files = q3d.export_results()
        assert len(exported_files) > 0
        q3d.close_project(q3d.project_name, save_project=False)

    def test_18_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"
