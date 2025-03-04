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

import ansys.aedt.core
from ansys.aedt.core import Q2d
import pytest

from tests import TESTS_GENERAL_PATH
from tests.system.general.conftest import config

test_project_name = "coax_Q2D"
test_subfolder = "T30"
q2d_q3d = "q2d_q3d_231"
q2d_solved_name = "q2d_solved"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Q2d)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def q2d_solved(add_app):
    app = add_app(
        project_name=q2d_solved_name,
        application=ansys.aedt.core.Q2d,
        subfolder=test_subfolder,
    )
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def q2d_matrix(add_app):
    app = add_app(
        project_name=q2d_q3d,
        application=ansys.aedt.core.Q2d,
        subfolder=test_subfolder,
    )
    yield app
    app.close_project(app.project_name)


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
        o = aedtapp.modeler.create_rectangle(udp, [5, 3], name="Rectangle1")
        assert isinstance(o.id, int)

    def test_02a_create_rectangle(self, aedtapp):
        o = aedtapp.create_rectangle((0, 0), [5, 3], name="Rectangle1")
        assert isinstance(o.id, int)

    def test_06a_create_setup(self, aedtapp):
        mysetup = aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()
        sweepName = "Q2D_Sweep1"
        qSweep = mysetup.add_sweep(sweepName)
        assert qSweep.add_subrange("LinearCount", 0.0, 100e6, 10)
        assert qSweep.add_subrange("LinearStep", 100e6, 2e9, 50e6)
        assert qSweep.add_subrange("LogScale", 100, 100e6, 10, clear=True)
        assert qSweep.add_subrange("LinearStep", 100, 100e6, 1e4, clear=True)
        assert qSweep.add_subrange("LinearCount", 100, 100e6, 10, clear=True)

    def test_07_single_signal_line(self, aedtapp):
        udp = aedtapp.modeler.Position(0, 0, 0)
        o = aedtapp.modeler.create_rectangle(udp, [5, 3], name="Rectangle1")
        assert aedtapp.assign_single_conductor(assignment=o, solve_option="SolveOnBoundary")

    def test_08_assign_huray_finitecond_to_edges(self, aedtapp):
        o = aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", material="Copper")
        aedtapp.assign_single_conductor(assignment=o, solve_option="SolveOnBoundary")
        assert aedtapp.assign_huray_finitecond_to_edges(o.edges, radius=0.5, ratio=2.9)

    def test_09_auto_assign(self, aedtapp):
        aedtapp.insert_design("test_auto")
        o = aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", material="Copper")
        o = aedtapp.create_rectangle([0, 0], [5, 3], name="Rectangle2", material="Copper")
        assert aedtapp.auto_assign_conductors()
        assert aedtapp.boundaries[0].properties
        assert len(aedtapp.boundaries) == 2
        assert aedtapp.toggle_conductor_type("Rectangle1", "ReferenceGround")
        assert not aedtapp.toggle_conductor_type("Rectangle3", "ReferenceGround")
        assert not aedtapp.toggle_conductor_type("Rectangle2", "ReferenceggGround")

    def test_11_matrix_reduction(self, q2d_solved):
        q2d = q2d_solved
        assert q2d.matrices[0].name == "Original"
        assert len(q2d.matrices[0].sources()) > 0
        assert len(q2d.matrices[0].sources(False)) > 0
        mm = q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Float, "Circle2", "Test1_m")
        assert mm.name == "Test1_m"
        mm = q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.AddGround, "Circle2", "Test2_m")
        assert mm.name == "Test2_m"
        mm = q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.SetReferenceGround, "Circle2", "Test3_m")
        assert mm.name == "Test3_m"
        mm = q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Parallel, ["Circle2", "Circle3"], "Test4_m")
        assert mm.name == "Test4_m"
        mm.delete()
        mm = q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Parallel, ["Circle2", "Circle3"], "Test4_m", "New_net")
        assert mm.name == "Test4_m"
        mm = q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.DiffPair, ["Circle2", "Circle3"], "Test5_m", "New_net")
        assert mm.name == "Test5_m"

    def test_12_edit_sources(self, q2d_matrix):
        q2d = q2d_matrix
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

    def test_13_get_all_conductors(self, aedtapp):
        aedtapp.insert_design("condcutors")
        o = aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", material="Copper")
        o1 = aedtapp.create_rectangle([7, 5], [5, 3], name="Rectangle2", material="aluminum")
        o3 = aedtapp.create_rectangle([27, 5], [5, 3], name="Rectangle3", material="air")
        conductors = aedtapp.get_all_conductors_names()
        assert sorted(conductors) == ["Rectangle1", "Rectangle2"]
        assert aedtapp.get_all_dielectrics_names() == ["Rectangle3"]

    def test_14_export_matrix_data(self, q2d_solved):
        q2d = q2d_solved
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
            os.path.join(self.local_scratch.path, "test_2d.txt"), problem_type="CG", setup="Setup1", sweep="Sweep1"
        )
        assert q2d.export_matrix_data(
            os.path.join(self.local_scratch.path, "test_2d.txt"),
            problem_type="CG",
            setup="Setup1",
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

    def test_15_export_equivalent_circuit(self, q2d_solved):
        q2d = q2d_solved
        q2d.insert_reduced_matrix(q2d.MATRIXOPERATIONS.Float, "Circle2", "Test4")
        assert q2d.matrices[-1].name == "Test4"
        assert len(q2d.setups[0].sweeps[0].frequencies) > 0
        assert q2d.setups[0].sweeps[0].basis_frequencies == []
        assert q2d.export_equivalent_circuit(os.path.join(self.local_scratch.path, "test_export_circuit.cir"))
        assert not q2d.export_equivalent_circuit(os.path.join(self.local_scratch.path, "test_export_circuit.doc"))
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup="Setup1",
            sweep="LastAdaptive",
        )
        assert not q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), setup="Setup2"
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup="Setup1",
            sweep="LastAdaptive",
            variations=["r1:0.3mm"],
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup="Setup1",
            sweep="LastAdaptive",
            variations=[" r1 : 0.3 mm "],
        )
        assert not q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            setup="Setup1",
            sweep="LastAdaptive",
            variations="r1:0.3mm",
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix="Original"
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), matrix="Test1"
        )
        assert not q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=2
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=0
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), coupling_limit_type=1
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            coupling_limit_type=0,
            ind_limit="12nH",
            res_limit="6Mohm",
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), lumped_length="34mm"
        )
        assert not q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), lumped_length="34nounits"
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            rise_time_value="1e-6",
            rise_time_unit="s",
        )
        assert not q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"),
            rise_time_value="23",
            rise_time_unit="m",
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), file_type="WELement"
        )
        assert not q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), file_type="test"
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), model=q2d_q3d
        )
        assert q2d.export_equivalent_circuit(
            output_file=os.path.join(self.local_scratch.path, "test_export_circuit.cir"), model="test"
        )

    def test_16_export_results_q2d(self, q2d_solved):
        exported_files = q2d_solved.export_results(analyze=False)
        assert len(exported_files) > 0

    def test_17_set_variable(self, aedtapp):
        aedtapp.variable_manager.set_variable("var_test", expression="123")
        aedtapp["var_test"] = "234"
        assert "var_test" in aedtapp.variable_manager.design_variable_names
        assert aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    def test_18_import_dxf(self, aedtapp):
        aedtapp.insert_design("dxf")
        dxf_file = os.path.join(TESTS_GENERAL_PATH, "example_models", "cad", "DXF", "dxf2.dxf")
        dxf_layers = aedtapp.get_dxf_layers(dxf_file)
        assert isinstance(dxf_layers, list)
        assert aedtapp.import_dxf(dxf_file, dxf_layers)
