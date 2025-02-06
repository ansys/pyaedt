# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

from ansys.aedt.core import Q3d
import pytest

q3d_solved_file = "Q3d_solved"
q3d_solved2_file = "q3d_solved2"
test_project_name = "coax_Q3D"
bondwire_project_name = "bondwireq3d_231"
q2d_q3d = "q2d_q3d_231"


mutual_coupling = "coupling"

test_subfolder = "T31"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Q3d)
    yield app
    app.close_project(save=False)


@pytest.fixture(scope="class")
def coupling(add_app):
    app = add_app(application=Q3d, project_name=mutual_coupling, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def bond(add_app):
    app = add_app(project_name=bondwire_project_name, subfolder=test_subfolder, application=Q3d)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def q3d_solved(add_app):
    app = add_app(project_name=q3d_solved_file, subfolder=test_subfolder, application=Q3d)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def q3d_solved2(add_app):
    app = add_app(project_name=q3d_solved2_file, subfolder=test_subfolder, application=Q3d)
    yield app
    app.close_project(save=False)


class TestClass:

    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_01_save(self, aedtapp):
        test_project = os.path.join(self.local_scratch.path, test_project_name + ".aedt")
        aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_create_primitive(self, aedtapp):
        udp = aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        o = aedtapp.modeler.create_cylinder(
            aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, name="MyCylinder", material="brass"
        )
        assert isinstance(o.id, int)

    def test_03_get_properties(self, aedtapp):
        assert aedtapp.odefinition_manager
        assert aedtapp.omaterial_manager
        assert aedtapp.design_file

    def test_06a_create_setup(self, aedtapp):
        mysetup = aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()
        assert mysetup.dc_enabled
        mysetup.dc_resistance_only = True
        assert mysetup.dc_resistance_only
        mysetup.dc_enabled = False
        mysetup.dc_enabled = True
        sweep = aedtapp.create_discrete_sweep(mysetup.name, sweepname="mysweep", freqstart=1, units="GHz")
        assert sweep
        assert sweep.props["RangeStart"] == "1GHz"

        # Create a discrete sweep with the same name of an existing sweep is not possible.
        assert not aedtapp.create_discrete_sweep(mysetup.name, sweepname="mysweep", freqstart=1, units="GHz")
        assert mysetup.create_linear_step_sweep(
            name="StepFast",
            unit="GHz",
            start_frequency=1,
            stop_frequency=20,
            step_size=0.1,
            sweep_type="Interpolating",
        )
        assert mysetup.create_linear_step_sweep(
            unit="GHz",
            start_frequency=1,
            stop_frequency=20,
            step_size=0.1,
            sweep_type="Interpolating",
        )
        with pytest.raises(AttributeError) as execinfo:
            mysetup.create_linear_step_sweep(
                name="invalid_sweep",
                unit="GHz",
                start_frequency=1,
                stop_frequency=20,
                step_size=0.1,
                sweep_type="Invalid",
            )
            assert (
                execinfo.args[0]
                == "Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'"
            )
        assert mysetup.create_single_point_sweep(
            save_fields=True,
        )
        assert mysetup.create_frequency_sweep(
            unit="GHz",
            name="Sweep1",
            freqstart=9.5,
            freqstop="10.5GHz",
            sweep_type="Interpolating",
        )

    def test_06b_create_setup(self, aedtapp):
        mysetup = aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()
        sweep2 = mysetup.create_frequency_sweep(name="mysweep2", unit="GHz", start_frequency=1, stop_frequency=4)
        assert sweep2
        sweep2_1 = mysetup.create_frequency_sweep(name="mysweep2", unit="GHz", start_frequency=1, stop_frequency=4)
        assert sweep2_1
        assert sweep2.name != sweep2_1.name
        assert sweep2.props["RangeEnd"] == "4GHz"
        sweep3 = mysetup.create_frequency_sweep(unit="GHz", start_frequency=1, stop_frequency=4)
        assert sweep3
        with pytest.raises(AttributeError) as execinfo:
            mysetup.create_frequency_sweep(
                name="mysweep4", unit="GHz", start_frequency=1, stop_frequency=4, sweep_type="Invalid"
            )
            assert (
                execinfo.args[0]
                == "Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'"
            )

    def test_06c_auto_identify(self, aedtapp):
        aedtapp.modeler.create_box([0, 0, 0], [1, 1, 20], material="brass")
        aedtapp.modeler.create_box([20, 5, 0], [1, 1, 20], material="brass")

        assert aedtapp.auto_identify_nets()
        assert aedtapp.delete_all_nets()
        assert aedtapp.auto_identify_nets()

    def test_07_create_source_sinks(self, aedtapp):
        udp = aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        aedtapp.modeler.create_cylinder(
            aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, name="MyCylinder", material="brass"
        )
        source = aedtapp.source("MyCylinder", direction=0, name="Source1")
        sink = aedtapp.sink("MyCylinder", direction=3, name="Sink1")
        assert source.name == "Source1"
        assert sink.name == "Sink1"
        assert len(aedtapp.excitations) > 0

    def test_07b_create_source_to_sheet(self, aedtapp):

        udp = aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        aedtapp.modeler.create_cylinder(
            aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, name="MyCylinder", material="brass"
        )

        udp = aedtapp.modeler.Position(10, 10, 0)
        coax_dimension = 30
        aedtapp.modeler.create_cylinder(aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, name="GND", material="brass")

        aedtapp.auto_identify_nets()
        aedtapp.modeler.create_circle(aedtapp.PLANE.XY, [0, 0, 0], 4, name="Source1")
        aedtapp.modeler.create_circle(aedtapp.PLANE.XY, [0, 0, coax_dimension], 4, name="Sink1")

        aedtapp.modeler.create_circle(aedtapp.PLANE.XY, [10, 10, 0], 4, name="Source2")
        aedtapp.modeler.create_circle(aedtapp.PLANE.XY, [10, 10, coax_dimension], 4, name="Sink2")

        source = aedtapp.source("Source1", name="Source3")
        sink = aedtapp.sink("Sink1", name="Sink3")

        assert source.name == "Source3"
        assert sink.name == "Sink3"
        assert source.props["TerminalType"] == "ConstantVoltage"
        assert sink.props["TerminalType"] == "ConstantVoltage"

        aedtapp.modeler.delete("Source1")
        aedtapp.modeler.delete("Sink1")

        aedtapp.modeler.create_circle(aedtapp.PLANE.XY, [0, 0, 0], 4, name="Source1")
        aedtapp.modeler.create_circle(aedtapp.PLANE.XY, [0, 0, coax_dimension], 4, name="Sink1")

        source = aedtapp.source("Source1", name="Source3", terminal_type="current")
        sink = aedtapp.sink("Sink1", name="Sink3", terminal_type="current")

        assert source.props["TerminalType"] == "UniformCurrent"
        assert sink.props["TerminalType"] == "UniformCurrent"

        source = aedtapp.source("Source2", name="Cylinder1", net_name="GND")
        source.props["Objects"] = ["Source2"]
        sink = aedtapp.sink("Sink2", net_name="GND")

        assert source
        assert sink
        sink.name = "My_new_name"
        assert sink.update()
        assert sink.name == "My_new_name"
        assert len(aedtapp.nets) > 0
        assert len(aedtapp.net_sources("GND")) > 0
        assert len(aedtapp.net_sinks("GND")) > 0
        assert len(aedtapp.net_sources("PGND")) == 0
        assert len(aedtapp.net_sinks("PGND")) == 0
        obj_list = aedtapp.objects_from_nets(aedtapp.nets[0])
        assert len(obj_list[aedtapp.nets[0]]) > 0
        obj_list = aedtapp.objects_from_nets(aedtapp.nets[0], "steel")
        assert len(obj_list[aedtapp.nets[0]]) == 0

    def test_08_create_faceted_bondwire(self, bond):
        test = bond.modeler.create_faceted_bondwire_from_true_surface(
            "bondwire_example", bond.AXIS.Z, min_size=0.2, number_of_segments=8
        )
        assert test

    def test_11_assign_net(self, aedtapp):
        box = aedtapp.modeler.create_box([30, 30, 30], [10, 10, 10], name="mybox")
        net_name = "my_net"
        net = aedtapp.assign_net(box, net_name)
        assert net
        assert net.name == net_name
        box = aedtapp.modeler.create_box([40, 30, 30], [10, 10, 10], name="mybox2")
        net = aedtapp.assign_net(box, None, "Ground")
        assert net
        box = aedtapp.modeler.create_box([60, 30, 30], [10, 10, 10], name="mybox3")
        net = aedtapp.assign_net(box, None, "Floating")
        assert net
        net.name = "new_net_name"
        assert net.update()
        assert net.name == "new_net_name"

    def test_11a_set_material_thresholds(self, aedtapp):
        assert aedtapp.set_material_thresholds()
        insulator_threshold = 2000
        perfect_conductor_threshold = 2e30
        magnetic_threshold = 3
        assert aedtapp.set_material_thresholds(insulator_threshold, perfect_conductor_threshold, magnetic_threshold)
        insulator_threshold = 2000
        perfect_conductor_threshold = 200
        magnetic_threshold = 3
        assert not aedtapp.set_material_thresholds(insulator_threshold, perfect_conductor_threshold, magnetic_threshold)

    def test_12_mesh_settings(self, aedtapp):
        assert aedtapp.mesh.initial_mesh_settings
        assert aedtapp.mesh.initial_mesh_settings.props

    def test_13_matrix_reduction(self, q3d_solved):
        q3d = q3d_solved
        assert q3d.matrices[0].name == "Original"
        assert len(q3d.matrices[0].sources()) > 0
        assert len(q3d.matrices[0].sources(False)) > 0
        mm = q3d.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest_mm")
        assert mm.name == "JointTest_mm"
        mm.delete()
        mm = q3d.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest_mm", "New_net")
        assert "New_net" in mm.sources()
        mm = q3d.insert_reduced_matrix("JoinParallel", ["Source1", "Source2"], "JointTest2_mm")
        assert mm.name == "JointTest2_mm"
        assert mm.delete()
        mm = q3d.insert_reduced_matrix("JoinParallel", ["Box1", "Box1_1"], "JointTest2_mm")
        assert mm.name == "JointTest2_mm"
        assert q3d.matrices[2].delete()
        mm = q3d.insert_reduced_matrix(
            "JoinParallel", ["Box1", "Box1_1"], "JointTest2", "New_net", "New_source", "New_sink"
        )
        assert "New_net" in mm.sources()
        assert mm.add_operation(q3d.MATRIXOPERATIONS.JoinParallel, ["Box1_2", "New_net"])
        assert len(mm.operations) == 2
        mm = q3d.insert_reduced_matrix("FloatInfinity", None, "JointTest3_mm")
        assert mm.name == "JointTest3_mm"
        mm = q3d.insert_reduced_matrix(q3d.MATRIXOPERATIONS.MoveSink, "Source2", "JointTest4_mm")
        assert mm.name == "JointTest4_mm"
        mm = q3d.insert_reduced_matrix(q3d.MATRIXOPERATIONS.ReturnPath, "Source2", "JointTest5")
        assert mm.name == "JointTest5"
        mm = q3d.insert_reduced_matrix(q3d.MATRIXOPERATIONS.GroundNet, "Box1", "JointTest6")
        assert mm.name == "JointTest6"
        assert mm.add_operation(q3d.MATRIXOPERATIONS.ReturnPath, "Source2")
        mm = q3d.insert_reduced_matrix(q3d.MATRIXOPERATIONS.FloatTerminal, "Source2", "JointTest7")
        assert mm.name == "JointTest7"
        assert mm.delete()
        full_list = q3d.matrices[0].get_sources_for_plot()
        mutual_list = q3d.matrices[0].get_sources_for_plot(
            get_self_terms=False, category=q3d.matrices[0].CATEGORIES.Q3D.ACL
        )
        assert q3d.get_traces_for_plot() == q3d.matrices[0].get_sources_for_plot()
        assert len(full_list) > len(mutual_list)
        assert q3d.matrices[0].get_sources_for_plot(first_element_filter="Box?", second_element_filter="B*2") == [
            "C(Box1,Box1_2)"
        ]

    def test_14_edit_sources(self, q3d_solved):
        sources_cg = {"Box1": ("2V", "45deg"), "Box1_2": "4V"}
        sources_ac = {"Box1:Source1": "2A"}
        assert q3d_solved.edit_sources(sources_cg, sources_ac)

        sources_cg = {"Box1": ("20V", "15deg"), "Box1_2": "40V"}
        sources_ac = {"Box1:Source1": "2A", "Box1_1:Source2": "20A"}
        sources_dc = {"Box1:Source1": "20V"}
        assert q3d_solved.edit_sources(sources_cg, sources_ac, sources_dc)

        sources_cg = {"Box1": "2V"}
        sources_ac = {"Box1:Source1": ["2"], "Box1_1:Source2": "5V"}
        assert q3d_solved.edit_sources(sources_cg, sources_ac)

        sources_cg = {"Box1": ["20V"], "Box1_2": "4V"}
        sources_ac = {"Box1:Source1": "2A"}
        assert q3d_solved.edit_sources(sources_cg, sources_ac)

        sources_dc = {"Box1:Source1": "20"}
        assert q3d_solved.edit_sources()

        sources_cg = {"Box2": "2V"}
        assert not q3d_solved.edit_sources(sources_cg)
        sources_ac = {"Box1:Source2": "2V"}
        assert not q3d_solved.edit_sources(sources_ac)
        sources_dc = {"Box1:Source2": "2V"}
        assert not q3d_solved.edit_sources(sources_dc)
        sources = q3d_solved.get_all_sources()
        assert sources[0] == "Box1:Source1"

        sources_dc = {"Box1:Source1": ["20v"]}
        assert q3d_solved.edit_sources(None, None, sources_dc)

    def test_15_insert_reduced(self, q3d_solved):
        q3d = q3d_solved
        mm = q3d.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest_r")
        assert mm.name == "JointTest_r"
        mm = q3d.insert_reduced_matrix("JoinParallel", ["Source1", "Source2"], "JointTest2_r")
        assert mm.name == "JointTest2_r"
        mm = q3d.insert_reduced_matrix("FloatInfinity", None, "JointTest3_r")
        assert mm.name == "JointTest3_r"

    def test_15_export_matrix_data(self, q3d_solved):
        q3d = q3d_solved
        sweep = q3d.setups[0].sweeps[0]
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
        assert q3d.export_matrix_data(file_name=os.path.join(self.local_scratch.path, "test.txt"), problem_type="C")
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
            file_name=os.path.join(self.local_scratch.path, "test.txt"), problem_type="AC"
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), setup="Setup1", sweep="LastAdaptive"
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), setup="Setup1", sweep="Last Adaptive"
        )
        assert not q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), setup="Setup", sweep="LastAdaptive"
        )
        assert not q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"), setup="Setup1", sweep="Last Adaptive Invented"
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
            file_name=os.path.join(self.local_scratch.path, "test.txt"), setup="Setup1", sweep="LastAdaptive", freq=1
        )
        assert q3d.export_matrix_data(
            file_name=os.path.join(self.local_scratch.path, "test.txt"),
            setup="Setup1",
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

    def test_equivalent_circuit(self, q3d_solved2):
        q3d = q3d_solved2
        exported_files = q3d_solved2.export_results()
        assert len(exported_files) > 0
        assert q3d.export_equivalent_circuit(
            os.path.join(self.local_scratch.path, "test_export_circuit.cir"), variations=["d: 10mm"]
        )
        assert not q3d.export_equivalent_circuit(os.path.join(self.local_scratch.path, "test_export_circuit.doc"))

        assert not q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup="Setup1",
            sweep="LastAdaptive",
            variations=["c: 10mm", "d: 20mm"],
        )

        assert not q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), setup="Setup2"
        )
        assert not q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), setup="Setup1", sweep="Sweep1"
        )
        assert q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix="Original"
        )
        assert q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix="JointTest"
        )
        assert not q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix="JointTest1"
        )
        assert not q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=2
        )
        assert q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=0
        )
        assert q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=1
        )
        assert q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            coupling_limit_type=0,
            cap_limit="4uF",
            ind_limit="9uH",
            res_limit="2ohm",
            cond_limit="3Sie",
        )
        assert q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), model="test_14"
        )
        assert q3d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), model="test"
        )

    def test_18_set_variable(self, aedtapp):
        aedtapp.variable_manager.set_variable("var_test", expression="123")
        aedtapp["var_test"] = "234"
        assert "var_test" in aedtapp.variable_manager.design_variable_names
        assert aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_19_assign_thin_conductor(self, aedtapp):
        q3d = aedtapp
        box = q3d.modeler.create_box([1, 1, 1], [10, 10, 10])
        assert q3d.assign_thin_conductor(box.top_face_z, material="copper", thickness=1, name="Thin1")
        rect = q3d.modeler.create_rectangle("X", [1, 1, 1], [10, 10])
        assert q3d.assign_thin_conductor(rect, material="aluminum", thickness="3mm", name="")
        assert not q3d.assign_thin_conductor(box, material="aluminum", thickness="3mm", name="")

    def test_20_auto_identify_no_metal(self, aedtapp):
        q3d = aedtapp
        q3d.modeler.create_box([0, 0, 0], [10, 20, 30], material="vacuum")
        assert q3d.auto_identify_nets()
        assert not q3d.nets

    def test_21_mutual_coupling(self, coupling):
        data1 = coupling.get_mutual_coupling("a1", "a2", "b2", "b1", setup_sweep_name="Setup1 : Sweep1")
        assert data1
        assert len(coupling.matrices) == 3
        data2 = coupling.get_mutual_coupling("a2", "a1", "b2", "b3")
        assert data2
        assert len(coupling.matrices) == 4

        data3 = coupling.get_mutual_coupling("a2", "a1", "a3", "a1")
        assert data3
        assert len(coupling.matrices) == 5

        assert not coupling.get_mutual_coupling("ac2", "a1", "a3", "a1")
        assert not coupling.get_mutual_coupling("a1", "a2", "b2", "b1", calculation="ACL2")
