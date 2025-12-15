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

from pathlib import Path

import pytest

from ansys.aedt.core import Q3d
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import MatrixOperationsQ3D
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.constants import PlotCategoriesQ3D
from ansys.aedt.core.internal.errors import AEDTRuntimeError

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


@pytest.fixture()
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
    def test_design_file(self, aedtapp):
        assert aedtapp.design_file

    def test_create_discrete_sweep(self, aedtapp):
        setup = aedtapp.create_setup()
        setup.props["SaveFields"] = True
        assert setup.update()
        assert setup.dc_enabled
        setup.dc_resistance_only = True
        assert setup.dc_resistance_only
        setup.dc_enabled = False
        setup.dc_enabled = True
        sweep = setup.create_frequency_sweep(sweep="mysweep", start_frequency=1, units="GHz")
        assert sweep
        assert sweep.props["RangeStart"] == "1GHz"

        assert not setup.create_frequency_sweep(name="mysweep", start_frequency=1, units="GHz")
        assert setup.create_linear_step_sweep(
            name="StepFast",
            unit="GHz",
            start_frequency=1,
            stop_frequency=20,
            step_size=0.1,
            sweep_type="Interpolating",
        )

    def test_create_linear_sweep(self, aedtapp):
        setup = aedtapp.create_setup()
        assert setup.create_linear_step_sweep(
            unit="GHz",
            start_frequency=1,
            stop_frequency=20,
            step_size=0.1,
            sweep_type="Interpolating",
        )
        with pytest.raises(AttributeError) as execinfo:
            setup.create_linear_step_sweep(
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

    def test_create_single_point_sweep(self, aedtapp):
        setup = aedtapp.create_setup()
        assert setup.create_single_point_sweep(
            save_fields=True,
        )

    def test_create_frequency_sweep(self, aedtapp):
        setup = aedtapp.create_setup()
        setup.props["SaveFields"] = True
        assert setup.update()
        assert setup.create_frequency_sweep(
            unit="GHz",
            name="Sweep1",
            start_frequency=9.5,
            stop_frequency="10.5GHz",
            sweep_type="Interpolating",
        )
        sweep2 = setup.create_frequency_sweep(name="mysweep2", unit="GHz", start_frequency=1, stop_frequency=4)
        assert sweep2
        sweep2_1 = setup.create_frequency_sweep(name="mysweep2", unit="GHz", start_frequency=1, stop_frequency=4)
        assert sweep2_1
        assert sweep2.name != sweep2_1.name
        assert sweep2.props["RangeEnd"] == "4GHz"
        sweep3 = setup.create_frequency_sweep(unit="GHz", start_frequency=1, stop_frequency=4)
        assert sweep3
        with pytest.raises(AttributeError) as execinfo:
            setup.create_frequency_sweep(
                name="mysweep4", unit="GHz", start_frequency=1, stop_frequency=4, sweep_type="Invalid"
            )
            assert (
                execinfo.args[0]
                == "Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'"
            )

    def test_auto_identify_nets(self, aedtapp):
        aedtapp.modeler.create_box([0, 0, 0], [1, 1, 20], material="brass")
        aedtapp.modeler.create_box([20, 5, 0], [1, 1, 20], material="brass")
        assert aedtapp.auto_identify_nets()
        assert len(aedtapp.net_names) == 2
        assert aedtapp.delete_all_nets()
        assert len(aedtapp.net_names) == 0
        assert aedtapp.auto_identify_nets()
        nets = aedtapp.net_names
        assert "SignalNet" in aedtapp.nets_by_type
        net1 = aedtapp.design_nets[nets[0]]
        net2 = aedtapp.design_nets[nets[1]]
        new_net1 = aedtapp.toggle_net(net1, "Floating")
        assert new_net1.type == "FloatingNet"
        net1_1 = aedtapp.design_nets[nets[0]]
        assert net1_1.type == "FloatingNet"
        net1_2 = aedtapp.design_nets[nets[0]]
        assert net1_2.type == "FloatingNet"
        assert "FloatingNet" in list(aedtapp.nets_by_type.keys())
        new_net2 = aedtapp.toggle_net(net2.name, "Ground")
        assert new_net2.type == "GroundNet"
        net2_1 = aedtapp.design_nets[nets[1]]
        assert net2_1.type == "GroundNet"
        net2_2 = aedtapp.design_nets[nets[1]]
        assert net2_2.type == "GroundNet"
        assert "GroundNet" in list(aedtapp.nets_by_type.keys())

    def test_autoidentify_no_nets(self, aedtapp):
        aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30], material="vacuum")
        assert aedtapp.auto_identify_nets()
        assert not aedtapp.net_names

    def test_create_source_sinks(self, aedtapp):
        aedtapp.modeler.create_cylinder(Plane.XY, [0, 0, 0], 3, 30, 0, name="MyCylinder", material="brass")
        source = aedtapp.source("MyCylinder", direction=0, name="Source1")
        sink = aedtapp.sink("MyCylinder", direction=3, name="Sink1")
        assert source.name == "Source1"
        assert sink.name == "Sink1"
        assert len(aedtapp.excitation_names) > 0

    def test_objects_from_nets(self, aedtapp):
        aedtapp.modeler.create_cylinder(Plane.XY, [0, 0, 0], 3, 30, 0, name="MyCylinder", material="brass")
        aedtapp.modeler.create_cylinder(Plane.XY, [10, 10, 10], 3, 30, 0, name="GND", material="brass")
        aedtapp.auto_identify_nets()
        aedtapp.modeler.create_circle(Plane.XY, [0, 0, 0], 4, name="Source1")
        aedtapp.modeler.create_circle(Plane.XY, [0, 0, 30], 4, name="Sink1")
        aedtapp.modeler.create_circle(Plane.XY, [10, 10, 0], 4, name="Source2")
        aedtapp.modeler.create_circle(Plane.XY, [10, 10, 30], 4, name="Sink2")
        source = aedtapp.source("Source1", name="Source3")
        sink = aedtapp.sink("Sink1", name="Sink3")
        assert source.name == "Source3"
        assert sink.name == "Sink3"
        assert source.props["TerminalType"] == "ConstantVoltage"
        assert sink.props["TerminalType"] == "ConstantVoltage"
        aedtapp.modeler.delete("Source1")
        aedtapp.modeler.delete("Sink1")
        aedtapp.modeler.create_circle(Plane.XY, [0, 0, 0], 4, name="Source1")
        aedtapp.modeler.create_circle(Plane.XY, [0, 0, 30], 4, name="Sink1")
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
        assert len(aedtapp.net_names) > 0
        assert len(aedtapp.net_sources("GND")) > 0
        assert len(aedtapp.net_sinks("GND")) > 0
        assert len(aedtapp.net_sources("PGND")) == 0
        assert len(aedtapp.net_sinks("PGND")) == 0
        obj_list = aedtapp.objects_from_nets(aedtapp.net_names[0])
        assert len(obj_list[aedtapp.net_names[0]]) > 0
        obj_list = aedtapp.objects_from_nets(aedtapp.net_names[0], "steel")
        assert len(obj_list[aedtapp.net_names[0]]) == 0

    def test_create_faceted_bondwire(self, bond):
        bondwire = bond.modeler.create_faceted_bondwire_from_true_surface(
            "bondwire_example", Axis.Z, min_size=0.2, number_of_segments=8
        )
        assert bondwire

    def test_assign_net(self, aedtapp):
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

    def test_set_material_thresholds(self, aedtapp):
        assert aedtapp.set_material_thresholds()
        insulator_threshold = 2000
        perfect_conductor_threshold = 2e30
        magnetic_threshold = 3
        assert aedtapp.set_material_thresholds(insulator_threshold, perfect_conductor_threshold, magnetic_threshold)
        insulator_threshold = 2000
        perfect_conductor_threshold = 200
        magnetic_threshold = 3
        assert not aedtapp.set_material_thresholds(insulator_threshold, perfect_conductor_threshold, magnetic_threshold)

    def test_matrix_reduction(self, q3d_solved):
        assert q3d_solved.matrices[0].name == "Original"
        assert len(q3d_solved.matrices[0].sources()) > 0
        assert len(q3d_solved.matrices[0].sources(False)) > 0
        mm = q3d_solved.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest_mm")
        assert mm.name == "JointTest_mm"
        mm.delete()
        mm = q3d_solved.insert_reduced_matrix("JoinSeries", ["Source1", "Sink4"], "JointTest_mm", "New_net")
        assert "New_net" in mm.sources()
        mm = q3d_solved.insert_reduced_matrix("JoinParallel", ["Source1", "Source2"], "JointTest2_mm")
        assert mm.name == "JointTest2_mm"
        assert mm.delete()
        mm = q3d_solved.insert_reduced_matrix("JoinParallel", ["Box1", "Box1_1"], "JointTest2_mm")
        assert mm.name == "JointTest2_mm"
        assert q3d_solved.matrices[2].delete()
        mm = q3d_solved.insert_reduced_matrix(
            "JoinParallel", ["Box1", "Box1_1"], "JointTest2", "New_net", "New_source", "New_sink"
        )
        assert "New_net" in mm.sources()
        assert mm.add_operation(MatrixOperationsQ3D.JoinParallel, ["Box1_2", "New_net"])
        assert len(mm.operations) == 2
        mm = q3d_solved.insert_reduced_matrix("FloatInfinity", None, "JointTest3_mm")
        assert mm.name == "JointTest3_mm"
        mm = q3d_solved.insert_reduced_matrix(MatrixOperationsQ3D.MoveSink, "Source2", "JointTest4_mm")
        assert mm.name == "JointTest4_mm"
        mm = q3d_solved.insert_reduced_matrix(MatrixOperationsQ3D.ReturnPath, "Source2", "JointTest5")
        assert mm.name == "JointTest5"
        mm = q3d_solved.insert_reduced_matrix(MatrixOperationsQ3D.GroundNet, "Box1", "JointTest6")
        assert mm.name == "JointTest6"
        assert mm.add_operation(MatrixOperationsQ3D.ReturnPath, "Source2")
        mm = q3d_solved.insert_reduced_matrix(MatrixOperationsQ3D.FloatTerminal, "Source2", "JointTest7")
        assert mm.name == "JointTest7"
        assert mm.delete()

    def test_get_sources_for_plot(self, q3d_solved):
        full_list = q3d_solved.matrices[0].get_sources_for_plot()
        mutual_list = q3d_solved.matrices[0].get_sources_for_plot(get_self_terms=False, category=PlotCategoriesQ3D.ACL)
        assert q3d_solved.get_traces_for_plot() == q3d_solved.matrices[0].get_sources_for_plot()
        assert len(full_list) > len(mutual_list)
        assert q3d_solved.matrices[0].get_sources_for_plot(
            first_element_filter="Box?", second_element_filter="B*2"
        ) == ["C(Box1,Box1_2)"]

    def test_edit_sources(self, q3d_solved):
        sources_cg = {"Box1": ("2V", "45deg"), "Box1_2": "4V"}
        sources_ac = {"Box1:Source1": "2A"}
        assert q3d_solved.edit_sources(sources_cg, sources_ac)
        sources_cg = {"Box1": ("20V", "15deg"), "Box1_2": "40V"}
        sources_ac = {"Box1:Source1": "2A", "Box1_1:Source2": "20A"}
        sources_dc = {"Box1:Source1": "20V"}
        assert q3d_solved.edit_sources(sources_cg, sources_ac, sources_dc)
        sources_cg = {"Box1": "2V"}
        sources_ac = {"Box1:Source1": "2", "Box1_1:Source2": "5V"}
        assert q3d_solved.edit_sources(sources_cg, sources_ac)
        sources_cg = {"Box1": "20V", "Box1_2": "4V"}
        sources_ac = {"Box1:Source1": "2A"}
        assert q3d_solved.edit_sources(sources_cg, sources_ac)
        assert q3d_solved.edit_sources()
        sources_cg = {"Box2": "2V"}
        assert not q3d_solved.edit_sources(sources_cg)
        sources_ac = {"Box1:Source2": "2V"}
        assert not q3d_solved.edit_sources(sources_ac)
        sources_dc = {"Box1:Source2": "2V"}
        assert not q3d_solved.edit_sources(sources_dc)
        sources = q3d_solved.get_all_sources()
        assert sources[0] == "Box1:Source1"
        sources_dc = {"Box1:Source1": "20v"}
        assert q3d_solved.edit_sources(None, None, sources_dc)
        real_dataset = q3d_solved.design_datasets["ds1"].name
        imag_dataset = q3d_solved.design_datasets["ds2"].name
        harmonic_loss = {"Box1:Source1": (real_dataset, imag_dataset)}
        assert q3d_solved.edit_sources(harmonic_loss=harmonic_loss)
        harmonic_loss = {"invalid": (real_dataset, imag_dataset)}
        assert not q3d_solved.edit_sources(harmonic_loss=harmonic_loss)
        harmonic_loss = {"Box1:Source1": real_dataset}
        assert not q3d_solved.edit_sources(harmonic_loss=harmonic_loss)

    def test_export_matrix_data(self, q3d_solved, local_scratch):
        file_path = Path(local_scratch.path) / "test.txt"
        sweep = q3d_solved.setups[0].sweeps[0]
        assert len(sweep.frequencies) > 0
        assert sweep.basis_frequencies == []
        assert q3d_solved.export_matrix_data(file_path)
        assert not q3d_solved.export_matrix_data(Path(local_scratch.path) / "test.pdf")
        assert not q3d_solved.export_matrix_data(file_name=file_path, matrix_type="Test")
        assert q3d_solved.export_matrix_data(
            file_name=file_path,
            problem_type="C",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert q3d_solved.export_matrix_data(
            file_name=file_path,
            problem_type="C",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert q3d_solved.export_matrix_data(file_name=file_path, problem_type="C")
        assert not q3d_solved.export_matrix_data(
            file_name=file_path,
            problem_type="AC RL, DC RL",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert q3d_solved.export_matrix_data(file_name=file_path, problem_type="AC RL, DC RL")
        assert q3d_solved.export_matrix_data(
            file_name=file_path,
            problem_type="AC RL, DC RL",
            matrix_type="Maxwell, Couple",
        )
        assert not q3d_solved.export_matrix_data(file_name=file_path, problem_type="AC")
        assert q3d_solved.export_matrix_data(file_name=file_path, setup="Setup1", sweep="LastAdaptive")
        assert q3d_solved.export_matrix_data(file_name=file_path, setup="Setup1", sweep="Last Adaptive")
        assert not q3d_solved.export_matrix_data(file_name=file_path, setup="Setup", sweep="LastAdaptive")
        assert not q3d_solved.export_matrix_data(file_name=file_path, setup="Setup1", sweep="Last Adaptive Invented")
        assert q3d_solved.export_matrix_data(file_name=file_path, reduce_matrix="Original")
        assert q3d_solved.export_matrix_data(file_name=file_path, reduce_matrix="JointTest")
        assert not q3d_solved.export_matrix_data(file_name=file_path, reduce_matrix="JointTest4")
        assert q3d_solved.export_matrix_data(file_name=file_path, setup="Setup1", sweep="LastAdaptive", freq=1)
        assert q3d_solved.export_matrix_data(
            file_name=file_path,
            setup="Setup1",
            sweep="LastAdaptive",
            freq=1,
            freq_unit="kHz",
        )
        assert q3d_solved.export_matrix_data(file_name=file_path, precision=16, field_width=22)
        assert not q3d_solved.export_matrix_data(file_name=file_path, precision=16.2)
        assert q3d_solved.export_matrix_data(file_name=file_path, use_sci_notation=True)
        assert q3d_solved.export_matrix_data(file_name=file_path, use_sci_notation=False)
        assert q3d_solved.export_matrix_data(file_name=file_path, r_unit="mohm")
        assert not q3d_solved.export_matrix_data(file_name=file_path, r_unit="A")
        assert q3d_solved.export_matrix_data(file_name=file_path, l_unit="nH")
        assert not q3d_solved.export_matrix_data(file_name=file_path, l_unit="A")
        assert q3d_solved.export_matrix_data(file_name=file_path, c_unit="farad")
        assert not q3d_solved.export_matrix_data(file_name=file_path, c_unit="H")
        assert q3d_solved.export_matrix_data(file_name=file_path, g_unit="fSie")
        assert not q3d_solved.export_matrix_data(file_name=file_path, g_unit="A")

    def test_equivalent_circuit(self, q3d_solved2, local_scratch):
        exported_files = q3d_solved2.export_results()
        file_path = Path(local_scratch.path) / "test_export_circuit.cir"
        assert len(exported_files) > 0
        assert q3d_solved2.export_equivalent_circuit(file_path, variations=["d: 10mm"])
        with pytest.raises(AEDTRuntimeError):
            q3d_solved2.export_equivalent_circuit(Path(local_scratch.path) / "test_export_circuit.doc")
        with pytest.raises(AEDTRuntimeError):
            q3d_solved2.export_equivalent_circuit(
                output_file=file_path,
                setup="Setup1",
                sweep="LastAdaptive",
                variations=["c: 10mm", "d: 20mm"],
            )
        with pytest.raises(AEDTRuntimeError):
            q3d_solved2.export_equivalent_circuit(output_file=file_path, setup="Setup2")
        with pytest.raises(AEDTRuntimeError):
            q3d_solved2.export_equivalent_circuit(
                output_file=file_path,
                setup="Setup1",
                sweep="Sweep1",
            )
        assert q3d_solved2.export_equivalent_circuit(
            output_file=file_path,
            matrix="Original",
            cells=1,
            include_acr=True,
            include_acl=True,
            include_cap=True,
            include_cond=True,
            include_cpp=True,
        )
        assert q3d_solved2.export_equivalent_circuit(output_file=file_path, matrix="Original")
        assert q3d_solved2.export_equivalent_circuit(output_file=file_path, matrix="JointTest")
        with pytest.raises(AEDTRuntimeError):
            q3d_solved2.export_equivalent_circuit(output_file=file_path, matrix="JointTest1")
        with pytest.raises(AEDTRuntimeError):
            q3d_solved2.export_equivalent_circuit(output_file=file_path, coupling_limit_type=2)
        assert q3d_solved2.export_equivalent_circuit(output_file=file_path, coupling_limit_type=0)
        assert q3d_solved2.export_equivalent_circuit(output_file=file_path, coupling_limit_type=1)
        assert q3d_solved2.export_equivalent_circuit(
            output_file=file_path,
            coupling_limit_type=0,
            cap_limit="4uF",
            ind_limit="9uH",
            res_limit="2ohm",
            cond_limit="3Sie",
        )
        assert q3d_solved2.export_equivalent_circuit(output_file=file_path, model="test_14")
        assert q3d_solved2.export_equivalent_circuit(output_file=file_path, model="test")

    def test_assign_thin_conductor(self, aedtapp):
        box = aedtapp.modeler.create_box([1, 1, 1], [10, 10, 10])
        assert aedtapp.assign_thin_conductor(box.top_face_z, material="copper", thickness=1, name="Thin1")
        rect = aedtapp.modeler.create_rectangle("X", [1, 1, 1], [10, 10])
        assert aedtapp.assign_thin_conductor(rect, material="aluminum", thickness="3mm", name="")
        assert not aedtapp.assign_thin_conductor(box, material="aluminum", thickness="3mm", name="")

    def test_mutual_coupling(self, coupling):
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

    def test_toggle_net_with_sources(self, aedtapp):
        aedtapp.modeler.create_cylinder(Plane.XY, [0, 0, 0], 3, 30, 0, name="MyCylinder", material="brass")
        aedtapp.source("MyCylinder", direction=0, name="Source1")
        aedtapp.sink("MyCylinder", direction=3, name="Sink1")
        aedtapp.auto_identify_nets()
        net = aedtapp.net_names[0]
        assert len(aedtapp.excitation_objects) == 3
        assert len(aedtapp.design_excitations) == 3
        assert "SignalNet" in aedtapp.nets_by_type
        sources = aedtapp.net_sources(net)
        sinks = aedtapp.net_sinks(net)
        with pytest.raises(ValueError):
            aedtapp.toggle_net(net_name="invented")
        new_net = aedtapp.toggle_net(net, "Ground")
        assert new_net.type == "GroundNet"
        assert len(aedtapp.boundaries) == 1
        assert len(aedtapp.net_names) == 1
        new_sources = aedtapp.net_sources(net)
        new_sinks = aedtapp.net_sinks(net)
        assert len(sources) != len(new_sources)
        assert len(sinks) != len(new_sinks)
        assert "GroundNet" in aedtapp.nets_by_type
        assert "SignalNet" not in aedtapp.nets_by_type

    def test_em_field_line(self, aedtapp):
        with pytest.raises(ValueError):
            aedtapp.insert_em_field_line(assignment="my_line")

        line = aedtapp.modeler.create_polyline(points=[[0, 0, 0], [1, 0, 0]], segment_type="Line", name="my_line")

        with pytest.raises(AEDTRuntimeError):
            aedtapp.insert_em_field_line(assignment="my_line")

        _ = aedtapp.create_setup()
        line_nf = aedtapp.insert_em_field_line(assignment=line.name, points=100)
        assert line_nf.name in aedtapp.field_setup_names
        assert aedtapp.field_setups
        assert line_nf.properties["Num Points"] == 100

    def test_em_field_rectangle(self, aedtapp):
        with pytest.raises(AEDTRuntimeError):
            aedtapp.insert_em_field_rectangle()

        _ = aedtapp.create_setup()
        rectangle_nf = aedtapp.insert_em_field_rectangle(u_length=200)
        assert rectangle_nf.name in aedtapp.field_setup_names
        assert aedtapp.field_setups
        assert rectangle_nf.properties["U Size"] == "200mm"

        cs = aedtapp.modeler.create_coordinate_system()
        rectangle_nf2 = aedtapp.insert_em_field_rectangle(custom_coordinate_system=cs.name)
        assert rectangle_nf2.name in aedtapp.field_setup_names
        assert len(aedtapp.field_setups) == 2

    def test_em_field_box(self, aedtapp):
        with pytest.raises(AEDTRuntimeError):
            aedtapp.insert_em_field_box()

        _ = aedtapp.create_setup()
        box_nf = aedtapp.insert_em_field_box(u_length=200)
        assert box_nf.name in aedtapp.field_setup_names
        assert aedtapp.field_setups
        assert box_nf.properties["U Size"] == "200mm"

        cs = aedtapp.modeler.create_coordinate_system()
        box_nf2 = aedtapp.insert_em_field_box(custom_coordinate_system=cs.name)
        assert box_nf2.name in aedtapp.field_setup_names
        assert len(aedtapp.field_setups) == 2

    def test_em_field_sphere(self, aedtapp):
        with pytest.raises(AEDTRuntimeError):
            aedtapp.insert_em_field_sphere("25mm")

        _ = aedtapp.create_setup()
        sphere_nf = aedtapp.insert_em_field_sphere("27mm", x_start=5.0)
        assert sphere_nf.name in aedtapp.field_setup_names
        assert aedtapp.field_setups
        assert sphere_nf.properties["Radius"] == "27mm"
        assert sphere_nf.properties["Start Theta"] == "5deg"

        cs = aedtapp.modeler.create_coordinate_system()
        sphere_nf2 = aedtapp.insert_em_field_sphere("50mm", custom_coordinate_system=cs.name)
        assert sphere_nf2.name in aedtapp.field_setup_names
        assert len(aedtapp.field_setups) == 2

    def test_create_report_em_fields(self, aedtapp):
        line = aedtapp.modeler.create_polyline(points=[[0, 0, 0], [1, 0, 0]], segment_type="Line", name="my_line")

        setup = aedtapp.create_setup()
        setup.props["SaveFields"] = True
        aedtapp.insert_em_field_line(assignment=line.name, points=100)
        variations = aedtapp.available_variations.nominal_values
        my_plots = aedtapp.post.create_report(
            expressions="re(EY)",
            variations=variations,
            primary_sweep_variable="NormalizedDistance",
            report_category="Static EM Fields",
            plot_type="Rectangular Plot",
            context=line.name,
            plot_name="my_plot",
        )
        assert my_plots
        assert my_plots.matrix == line.name
        assert my_plots.expressions == ["re(EY)"]
