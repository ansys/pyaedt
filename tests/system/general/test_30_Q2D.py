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
from pathlib import Path

import pytest

import ansys.aedt.core
from ansys.aedt.core import Q2d
from ansys.aedt.core.generic.constants import MatrixOperationsQ2D
from ansys.aedt.core.generic.file_utils import get_dxf_layers
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH
from tests.conftest import config

test_subfolder = "T30"
q2d_q3d = "q2d_q3d_231"
q2d_solved_name = "q2d_solved"
q2d_solved_sweep = "q2d_solved_sweep"
q2d_solved_nominal = "q2d_solved_nominal"


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


@pytest.fixture()
def q2d_solved_sweep_app(add_app):
    app = add_app(application=Q2d, project_name=q2d_solved_sweep, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def q2d_solved_nominal_app(add_app):
    app = add_app(application=Q2d, project_name=q2d_solved_nominal, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


class TestClass:
    def test_add_sweep(self, aedtapp):
        setup = aedtapp.create_setup()
        setup.props["SaveFields"] = True
        assert setup.update()
        sweep = setup.add_sweep("Q2D_Sweep1")
        assert sweep.add_subrange("LinearCount", 0.0, 100e6, 10)
        assert sweep.add_subrange("LinearStep", 100e6, 2e9, 50e6)
        assert sweep.add_subrange("LogScale", 100, 100e6, 10, clear=True)
        assert sweep.add_subrange("LinearStep", 100, 100e6, 1e4, clear=True)
        assert sweep.add_subrange("LinearCount", 100, 100e6, 10, clear=True)

    def test_assign_single_signal_line(self, aedtapp):
        rect = aedtapp.modeler.create_rectangle([0, 0, 0], [5, 3], name="Rectangle1")
        assert aedtapp.assign_single_conductor(assignment=rect, solve_option="SolveOnBoundary")

    def test_assign_huray_finitecond_to_edges(self, aedtapp):
        rect = aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", material="Copper")
        aedtapp.assign_single_conductor(assignment=rect, solve_option="SolveOnBoundary")
        assert aedtapp.assign_huray_finitecond_to_edges(rect.edges, radius=0.5, ratio=2.9)

    def test_auto_assign_conductors(self, aedtapp):
        aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", material="Copper")
        aedtapp.create_rectangle([0, 0], [5, 3], name="Rectangle2", material="Copper")
        assert aedtapp.auto_assign_conductors()
        assert aedtapp.boundaries[0].properties
        assert len(aedtapp.boundaries) == 2
        assert aedtapp.toggle_conductor_type("Rectangle1", "ReferenceGround")
        assert not aedtapp.toggle_conductor_type("Rectangle3", "ReferenceGround")
        assert not aedtapp.toggle_conductor_type("Rectangle2", "ReferenceggGround")

    def test_matrix_reduction(self, q2d_solved):
        assert q2d_solved.matrices[0].name == "Original"
        assert len(q2d_solved.matrices[0].sources()) > 0
        assert len(q2d_solved.matrices[0].sources(False)) > 0
        mm = q2d_solved.insert_reduced_matrix(MatrixOperationsQ2D.Float, "Circle2", "Test1_m")
        assert mm.name == "Test1_m"
        mm = q2d_solved.insert_reduced_matrix(MatrixOperationsQ2D.AddGround, "Circle2", "Test2_m")
        assert mm.name == "Test2_m"
        mm = q2d_solved.insert_reduced_matrix(MatrixOperationsQ2D.SetReferenceGround, "Circle2", "Test3_m")
        assert mm.name == "Test3_m"
        mm = q2d_solved.insert_reduced_matrix(MatrixOperationsQ2D.Parallel, ["Circle2", "Circle3"], "Test4_m")
        assert mm.name == "Test4_m"
        mm.delete()
        mm = q2d_solved.insert_reduced_matrix(
            MatrixOperationsQ2D.Parallel, ["Circle2", "Circle3"], "Test4_m", "New_net"
        )
        assert mm.name == "Test4_m"
        mm = q2d_solved.insert_reduced_matrix(
            MatrixOperationsQ2D.DiffPair, ["Circle2", "Circle3"], "Test5_m", "New_net"
        )
        assert mm.name == "Test5_m"

    def test_edit_sources(self, q2d_matrix):
        sources_cg = {"Circle2": ("10V", "45deg"), "Circle3": "4A"}
        assert q2d_matrix.edit_sources(sources_cg)
        sources_cg = {"Circle2": "1V", "Circle3": "4A"}
        sources_ac = {"Circle3": "40A"}
        assert q2d_matrix.edit_sources(sources_cg, sources_ac)
        sources_cg = {"Circle2": "10V", "Circle3": "4A"}
        sources_ac = {"Circle3": ("100A", "5deg")}
        assert q2d_matrix.edit_sources(sources_cg, sources_ac)
        sources_ac = {"Circle5": "40A"}
        assert not q2d_matrix.edit_sources(sources_cg, sources_ac)

    def test_get_all_conductors(self, aedtapp):
        aedtapp.create_rectangle([6, 6], [5, 3], name="Rectangle1", material="Copper")
        aedtapp.create_rectangle([7, 5], [5, 3], name="Rectangle2", material="aluminum")
        aedtapp.create_rectangle([27, 5], [5, 3], name="Rectangle3", material="air")
        conductors = aedtapp.get_all_conductors_names()
        assert sorted(conductors) == ["Rectangle1", "Rectangle2"]
        assert aedtapp.get_all_dielectrics_names() == ["Rectangle3"]

    def test_export_matrix_data(self, q2d_solved, local_scratch):
        file_path = Path(local_scratch.path) / "test_2d.txt"
        assert q2d_solved.export_matrix_data(file_path)
        assert q2d_solved.export_matrix_data(file_path, problem_type="CG")
        assert q2d_solved.export_matrix_data(
            file_path,
            problem_type="CG",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert not q2d_solved.export_matrix_data(
            file_path,
            problem_type="RL",
            matrix_type="Maxwell, Spice, Couple",
        )
        assert q2d_solved.export_matrix_data(file_path, problem_type="RL", matrix_type="Maxwell, Couple")
        assert q2d_solved.export_matrix_data(file_path, problem_type="CG", setup="Setup1", sweep="Sweep1")
        assert q2d_solved.export_matrix_data(
            file_path,
            problem_type="CG",
            setup="Setup1",
            sweep="LastAdaptive",
        )
        assert q2d_solved.export_matrix_data(file_path, problem_type="CG", reduce_matrix="Test1")
        assert q2d_solved.export_matrix_data(file_path, problem_type="CG", reduce_matrix="Test3")
        assert not q2d_solved.export_matrix_data(file_path, problem_type="CG", reduce_matrix="Test4")
        assert q2d_solved.export_matrix_data(file_path, precision=16, field_width=22)
        assert not q2d_solved.export_matrix_data(file_path, precision=16.2)
        assert q2d_solved.export_matrix_data(file_path, freq="3", freq_unit="Hz")
        assert q2d_solved.export_matrix_data(file_path, use_sci_notation=True)
        assert q2d_solved.export_matrix_data(file_path, use_sci_notation=False)
        assert q2d_solved.export_matrix_data(file_path, r_unit="mohm")
        assert not q2d_solved.export_matrix_data(file_path, r_unit="A")
        assert q2d_solved.export_matrix_data(file_path, l_unit="nH")
        assert not q2d_solved.export_matrix_data(file_path, l_unit="A")
        assert q2d_solved.export_matrix_data(file_path, c_unit="farad")
        assert not q2d_solved.export_matrix_data(file_path, c_unit="H")
        assert q2d_solved.export_matrix_data(file_path, g_unit="fSie")
        assert not q2d_solved.export_matrix_data(file_path, g_unit="A")

    def test_export_equivalent_circuit(self, q2d_solved, local_scratch):
        q2d_solved.insert_reduced_matrix(MatrixOperationsQ2D.Float, "Circle2", "Test4")
        assert q2d_solved.matrices[-1].name == "Test4"
        assert len(q2d_solved.setups[0].sweeps[0].frequencies) > 0
        assert q2d_solved.setups[0].sweeps[0].basis_frequencies == []
        file_path = Path(local_scratch.path) / "test_export_circuit.sml"
        assert q2d_solved.export_equivalent_circuit(file_path)
        assert os.path.isfile(file_path)
        with pytest.raises(AEDTRuntimeError):
            q2d_solved.export_equivalent_circuit(os.path.join(local_scratch.path, "test_export_circuit.cir"))
        with pytest.raises(AEDTRuntimeError):
            q2d_solved.export_equivalent_circuit(
                output_file=os.path.join(local_scratch.path, "test_export_circuit.cir"),
                setup="Setup1",
                sweep="LastAdaptive",
            )
        with pytest.raises(AEDTRuntimeError):
            q2d_solved.export_equivalent_circuit(
                output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), setup="Setup2"
            )

        file_path = os.path.join(local_scratch.path, "test_export_circuit2.sml")
        assert q2d_solved.export_equivalent_circuit(
            output_file=file_path,
            setup="Setup1",
            sweep="LastAdaptive",
            variations=["r1:0.3mm"],
        )
        assert os.path.isfile(file_path)

        file_path = os.path.join(local_scratch.path, "test_export_circuit3.sml")
        assert q2d_solved.export_equivalent_circuit(
            output_file=file_path,
            setup="Setup1",
            sweep="LastAdaptive",
            variations=[" r1 : 0.3 mm "],
        )
        with pytest.raises(AEDTRuntimeError):
            q2d_solved.export_equivalent_circuit(
                output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"),
                setup="Setup1",
                sweep="LastAdaptive",
                variations="r1:0.3mm",
            )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), matrix="Original"
        )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), matrix="Test1"
        )
        with pytest.raises(AEDTRuntimeError):
            q2d_solved.export_equivalent_circuit(
                output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), coupling_limit_type=2
            )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), coupling_limit_type=0
        )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), coupling_limit_type=1
        )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"),
            coupling_limit_type=0,
            ind_limit="12nH",
            res_limit="6Mohm",
        )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), lumped_length="34mm"
        )
        with pytest.raises(AEDTRuntimeError):
            q2d_solved.export_equivalent_circuit(
                output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), lumped_length="34nounits"
            )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"),
            rise_time_value="1e-6",
            rise_time_unit="s",
        )
        with pytest.raises(AEDTRuntimeError):
            q2d_solved.export_equivalent_circuit(
                output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"),
                rise_time_value="23",
                rise_time_unit="m",
            )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), file_type="WELement"
        )
        with pytest.raises(AEDTRuntimeError):
            q2d_solved.export_equivalent_circuit(
                output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), file_type="test"
            )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), model=q2d_q3d
        )
        assert q2d_solved.export_equivalent_circuit(
            output_file=os.path.join(local_scratch.path, "test_export_circuit.sml"), model="test"
        )

    def test_export_results(self, q2d_solved):
        exported_files = q2d_solved.export_results(analyze=False)
        assert len(exported_files) > 0

    @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    def test_import_dxf(self, aedtapp):
        dxf_file = Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "DXF" / "dxf1.dxf"
        dxf_layers = get_dxf_layers(dxf_file)
        assert isinstance(dxf_layers, list)
        assert aedtapp.import_dxf(dxf_file, dxf_layers)

    def test_export_w_elements_from_sweep(self, q2d_solved_sweep_app, local_scratch):
        export_folder = Path(local_scratch.path) / "export_folder"
        files = q2d_solved_sweep_app.export_w_elements(False, export_folder)
        assert len(files) == 3
        for file in files:
            ext = Path(file).suffix
            assert ext == ".sp"
            assert Path(file).is_file()

    def test_export_w_elements_from_nominal(self, q2d_solved_nominal_app, local_scratch):
        export_folder = Path(local_scratch.path) / "export_folder"
        files = q2d_solved_nominal_app.export_w_elements(False, export_folder)
        assert len(files) == 1
        for file in files:
            ext = Path(file).suffix
            assert ext == ".sp"
            assert Path(file).is_file()

        files = q2d_solved_nominal_app.export_w_elements(False)
        assert len(files) == 1
        for file in files:
            ext = Path(file).suffix
            assert ext == ".sp"
            assert Path(file).is_file()
            file_dir = Path(file).parent.absolute()
            assert file_dir == Path(q2d_solved_nominal_app.working_directory).absolute()
