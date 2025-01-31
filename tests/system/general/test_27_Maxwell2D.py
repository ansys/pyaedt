#!/ekm/software/anaconda3/bin/python

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
import shutil

import ansys.aedt.core
from ansys.aedt.core.generic.constants import SOLUTIONS
import pytest

from tests import TESTS_GENERAL_PATH
from tests.system.general.conftest import config

test_subfolder = "TMaxwell"

test_name = "Maxwell_2D_Tests"
design_name = "Basis_Model_For_Test"

ctrl_prg = "TimeStepCtrl"
ctrl_prg_file = "timestep_only.py"

m2d_export_fields = "maxwell_e_line_export_field"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(
        project_name=test_name,
        design_name=design_name,
        application=ansys.aedt.core.Maxwell2d,
        subfolder=test_subfolder,
    )
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def m2d_fields(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d, project_name=m2d_export_fields, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def m2d_ctrl_prg(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d, project_name=ctrl_prg, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def m2d_app(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d)
    yield app
    app.close_project(app.project_name)


class TestClass:

    def test_assign_initial_mesh_from_slider(self, aedtapp):
        assert aedtapp.mesh.assign_initial_mesh_from_slider(4)
        with pytest.raises(ValueError):
            aedtapp.mesh.assign_initial_mesh_from_slider(method="dummy")
        with pytest.raises(ValueError):
            aedtapp.mesh.assign_initial_mesh(method="dummy")

    def test_assign_winding(self, aedtapp):
        bounds = aedtapp.assign_winding(assignment=["Coil"], current=20e-3)
        assert bounds
        o = aedtapp.modeler.create_rectangle([0, 0, 0], [3, 1], name="Rectangle", material="copper")
        bounds = aedtapp.assign_winding(assignment=o.id, current=20e-3)
        assert bounds
        bounds = aedtapp.assign_winding(assignment=["Coil"], current="20e-3A")
        assert bounds
        bounds = aedtapp.assign_winding(assignment=["Coil"], resistance="1ohm")
        assert bounds
        bounds = aedtapp.assign_winding(assignment=["Coil"], inductance="1H")
        assert bounds
        bounds = aedtapp.assign_winding(assignment=["Coil"], voltage="10V")
        assert bounds
        bounds_name = ansys.aedt.core.generate_unique_name("Coil")
        bounds = aedtapp.assign_winding(assignment=["Coil"], name=bounds_name)
        assert bounds_name == bounds.name

    def test_assign_coil(self, aedtapp):
        bound = aedtapp.assign_coil(assignment=["Coil"])
        assert bound
        polarity = "Positive"
        bound = aedtapp.assign_coil(assignment=["Coil"], polarity=polarity)
        assert bound.props["PolarityType"] == polarity.lower()
        polarity = "Negative"
        bound = aedtapp.assign_coil(assignment=["Coil"], polarity=polarity)
        assert bound.props["PolarityType"] == polarity.lower()
        bound_name = ansys.aedt.core.generate_unique_name("Coil")
        bound = aedtapp.assign_coil(assignment=["Coil"], name=bound_name)
        assert bound_name == bound.name

    def test_create_vector_potential(self, aedtapp):
        region = aedtapp.modeler["Region"]
        edge_object = region.edges[0]
        bounds = aedtapp.assign_vector_potential(edge_object.id, 3)
        assert bounds
        assert bounds.props["Value"] == "3"
        bounds["Value"] = "2"
        assert bounds.props["Value"] == "2"
        line = aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="myline")
        bound2 = aedtapp.assign_vector_potential(line.id, 2)
        assert bound2
        assert bound2.props["Value"] == "2"
        assert bound2.update()

    def test_create_setup(self, aedtapp):
        mysetup = aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()

    def test_assign_balloon(self, aedtapp):
        region = aedtapp.modeler["Region"]
        aedtapp.assign_balloon(region.edges)

    def test_generate_design_data(self, aedtapp):
        assert aedtapp.generate_design_data()
        assert aedtapp.read_design_data()

    def test_assign_torque(self, aedtapp):
        torque = aedtapp.assign_torque("Rotor_Section1")
        assert torque.type == "Torque"
        assert torque.props["Objects"][0] == "Rotor_Section1"
        assert torque.props["Is Positive"]
        assert torque.delete()
        torque = aedtapp.assign_torque(assignment="Rotor_Section1", is_positive=False, torque_name="Torque_Test")
        assert torque.name == "Torque_Test"
        assert not torque.props["Is Positive"]
        assert torque.props["Objects"][0] == "Rotor_Section1"

    def test_assign_force(self, aedtapp):
        force = aedtapp.assign_force("Magnet2_Section1")
        assert force.type == "Force"
        assert force.props["Objects"][0] == "Magnet2_Section1"
        assert force.props["Reference CS"] == "Global"
        assert force.delete()
        force = aedtapp.assign_force(assignment="Magnet2_Section1", force_name="Force_Test")
        assert force.name == "Force_Test"

    def test_assign_current_source(self, aedtapp):
        coil = aedtapp.modeler.create_circle(
            position=[0, 0, 0], radius=5, num_sides="8", is_covered=True, name="Coil", material="Copper"
        )
        assert aedtapp.assign_current([coil])
        assert not aedtapp.assign_current([coil.faces[0].id])

    def test_assign_master_slave(self, aedtapp):
        aedtapp.modeler.create_rectangle([1, 1, 1], [3, 1], name="Rectangle1", material="copper")
        mas, slave = aedtapp.assign_master_slave(
            aedtapp.modeler["Rectangle1"].edges[0].id,
            aedtapp.modeler["Rectangle1"].edges[2].id,
        )
        assert mas.properties["Type"] == "Independent"
        assert slave.properties["Type"] == "Dependent"
        assert mas.props["Edges"][0] == aedtapp.modeler["Rectangle1"].edges[0].id
        assert slave.props["Edges"][0] == aedtapp.modeler["Rectangle1"].edges[2].id
        mas, slave = aedtapp.assign_master_slave(
            aedtapp.modeler["Rectangle1"].edges[0].id, aedtapp.modeler["Rectangle1"].edges[2].id, boundary="my_bound"
        )
        assert mas.name == "my_bound"
        assert slave.name == "my_bound_dep"
        assert not aedtapp.assign_master_slave(
            aedtapp.modeler["Rectangle1"].edges[0].id,
            aedtapp.modeler["Rectangle1"].edges[1].id,
        )

    def test_check_design_preview_image(self, local_scratch, aedtapp):
        jpg_file = os.path.join(local_scratch.path, "file.jpg")
        assert aedtapp.export_design_preview_to_jpg(jpg_file)

    def test_model_depth(self, aedtapp):
        assert aedtapp.change_design_settings({"ModelDepth": "3mm"})

    def test_apply_skew(self, aedtapp):
        assert aedtapp.apply_skew()
        assert not aedtapp.apply_skew(skew_type="Invalid")
        assert not aedtapp.apply_skew(skew_part="Invalid")
        assert not aedtapp.apply_skew(
            skew_type="Continuous", skew_part="Stator", skew_angle="0.5", skew_angle_unit="Invalid"
        )
        assert not aedtapp.apply_skew(
            skew_type="User Defined", number_of_slices="4", custom_slices_skew_angles=["1", "2", "3"]
        )
        assert aedtapp.apply_skew(
            skew_type="User Defined", number_of_slices="4", custom_slices_skew_angles=["1", "2", "3", "4"]
        )

    def test_assign_movement(self, aedtapp):
        aedtapp.xy_plane = True
        aedtapp.modeler.create_circle([0, 0, 0], 10, name="Circle_inner")
        aedtapp.modeler.create_circle([0, 0, 0], 30, name="Circle_outer")
        bound = aedtapp.assign_rotate_motion("Circle_outer", positive_limit=300, mechanical_transient=True)
        assert bound
        assert bound.props["PositivePos"] == "300deg"
        assert bound.props["Objects"][0] == "Circle_outer"

    def test_change_inductance_computation(self, aedtapp):
        assert aedtapp.change_inductance_computation()
        assert aedtapp.change_inductance_computation(True, False)
        assert aedtapp.change_inductance_computation(False, False)

    def test_initial_mesh_settings(self, aedtapp):
        assert aedtapp.mesh.initial_mesh_settings
        assert aedtapp.mesh.initial_mesh_settings.props

    def test_assign_end_connection(self, aedtapp):
        rect = aedtapp.modeler.create_rectangle([0, 0, 0], [5, 5], material="aluminum")
        rect2 = aedtapp.modeler.create_rectangle([15, 20, 0], [5, 5], material="aluminum")
        bound = aedtapp.assign_end_connection([rect, rect2])
        assert bound
        assert bound.props["ResistanceValue"] == "0ohm"
        bound.props["InductanceValue"] = "5H"
        assert bound.props["InductanceValue"] == "5H"
        assert not aedtapp.assign_end_connection([rect])
        aedtapp.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticXY
        assert not aedtapp.assign_end_connection([rect, rect2])

    def test_setup_y_connection(self, aedtapp):
        aedtapp.set_active_design("Y_Connections")
        assert aedtapp.setup_y_connection(["PhaseA", "PhaseB", "PhaseC"])
        assert aedtapp.setup_y_connection(["PhaseA", "PhaseB"])
        assert aedtapp.setup_y_connection()

    def test_change_symmetry_multiplier(self, aedtapp):
        assert aedtapp.change_symmetry_multiplier(2)

    def test_eddy_effects_on(self, aedtapp):
        assert aedtapp.eddy_effects_on(["Coil_1"], enable_eddy_effects=True)
        assert aedtapp.oboundary.GetEddyEffect("Coil_1")
        aedtapp.eddy_effects_on(["Coil_1"], enable_eddy_effects=False)
        assert not aedtapp.oboundary.GetEddyEffect("Coil_1")

    def test_assign_symmetry(self, aedtapp):
        region = [x for x in aedtapp.modeler.object_list if x.name == "Region"]
        band = [x for x in aedtapp.modeler.object_list if x.name == "Band"]
        assert aedtapp.assign_symmetry([region[0].edges[0], band[0].edges[0]], "Symmetry_Test_IsOdd")
        assert aedtapp.assign_symmetry([region[0].edges[0], band[0].edges[0]])
        assert aedtapp.assign_symmetry([region[0].edges[0], band[0].edges[0]], "Symmetry_Test_IsEven", False)
        assert aedtapp.assign_symmetry([9556, 88656])
        assert not aedtapp.assign_symmetry([])
        for bound in aedtapp.boundaries:
            if bound.name == "Symmetry_Test_IsOdd":
                assert bound.type == "Symmetry"
                assert bound.props["IsOdd"]
            if bound.name == "Symmetry_Test_IsEven":
                assert bound.type == "Symmetry"
                assert not bound.props["IsOdd"]

    def test_export_rl_matrix(self, local_scratch, aedtapp):
        aedtapp.set_active_design("Sinusoidal")
        assert not aedtapp.export_rl_matrix("Test1", " ")
        aedtapp.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        aedtapp.assign_matrix(assignment=["PM_I1_1_I0", "PM_I1_I0"], matrix_name="Test1")
        aedtapp.assign_matrix(assignment=["Phase_A", "Phase_B", "Phase_C"], matrix_name="Test2")
        setup_name = "setupTestMatrixRL"
        setup = aedtapp.create_setup(name=setup_name)
        setup.props["MaximumPasses"] = 2
        export_path_1 = os.path.join(local_scratch.path, "export_rl_matrix_Test1.txt")
        assert not aedtapp.export_rl_matrix("Test1", export_path_1)
        assert not aedtapp.export_rl_matrix("Test2", export_path_1, False, 10, 3, True)
        aedtapp.validate_simple()
        aedtapp.analyze_setup(setup_name)
        assert aedtapp.export_rl_matrix("Test1", export_path_1)
        assert not aedtapp.export_rl_matrix("abcabc", export_path_1)
        assert os.path.exists(export_path_1)
        export_path_2 = os.path.join(local_scratch.path, "export_rl_matrix_Test2.txt")
        assert aedtapp.export_rl_matrix("Test2", export_path_2, False, 10, 3, True)
        assert os.path.exists(export_path_2)

    def test_assign_current_density(self, aedtapp):
        aedtapp.set_active_design("Sinusoidal")
        bound = aedtapp.assign_current_density("Coil", "CurrentDensity_1")
        assert bound
        assert bound.props["Objects"] == ["Coil"]
        assert bound.props["Value"] == "0"
        assert bound.props["CoordinateSystem"] == ""
        bound2 = aedtapp.assign_current_density("Coil", "CurrentDensity_2", "40deg", current_density_2d="2")
        assert bound2
        assert bound2.props["Objects"] == ["Coil"]
        assert bound2.props["Value"] == "2"
        assert bound2.props["CoordinateSystem"] == ""
        bound_group = aedtapp.assign_current_density(["Coil", "Coil_1"], "CurrentDensityGroup_1")
        assert bound_group
        assert bound_group.props[bound_group.props["items"][0]]["Objects"] == ["Coil", "Coil_1"]
        assert bound_group.props[bound_group.props["items"][0]]["Value"] == "0"
        assert bound_group.props[bound_group.props["items"][0]]["CoordinateSystem"] == ""
        assert not aedtapp.assign_current_density("Circle_inner", "CurrentDensity_1")

    def test_set_variable(self, aedtapp):
        aedtapp.variable_manager.set_variable("var_test", expression="123")
        aedtapp["var_test"] = "234"
        assert "var_test" in aedtapp.variable_manager.design_variable_names
        assert aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_cylindrical_gap(self, aedtapp):
        assert not aedtapp.mesh.assign_cylindrical_gap("Band")
        [
            x.delete()
            for x in aedtapp.mesh.meshoperations[:]
            if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
        ]
        assert aedtapp.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test")
        assert not aedtapp.mesh.assign_cylindrical_gap(["Band", "Region"])
        assert not aedtapp.mesh.assign_cylindrical_gap("Band")
        [
            x.delete()
            for x in aedtapp.mesh.meshoperations[:]
            if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
        ]
        assert aedtapp.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test", band_mapping_angle=2)

    def test_skin_depth(self, aedtapp):
        edge = aedtapp.modeler["Rotor_Section1"].edges[0]
        mesh = aedtapp.mesh.assign_skin_depth(assignment=edge, skin_depth="0.3mm", layers_number=3)
        assert mesh
        assert mesh.type == "SkinDepthBased"
        assert mesh.props["Edges"][0] == edge.id
        assert mesh.props["SkinDepth"] == "0.3mm"
        assert mesh.props["NumLayers"] == 3
        edge1 = aedtapp.modeler["Rotor_Section1"].edges[1]
        mesh = aedtapp.mesh.assign_skin_depth(assignment=edge1.id, skin_depth="0.3mm", layers_number=3)
        assert mesh
        assert mesh.type == "SkinDepthBased"
        assert mesh.props["Edges"][0] == edge1.id
        assert mesh.props["SkinDepth"] == "0.3mm"
        assert mesh.props["NumLayers"] == 3

    def test_start_continue_from_previous_setup(self, local_scratch, aedtapp):
        assert aedtapp.setups[0].start_continue_from_previous_setup(
            design="Y_Connections", solution="Setup1 : Transient"
        )
        assert aedtapp.setups[0].props["PrevSoln"]["Project"] == "This Project*"
        assert aedtapp.setups[0].props["PrevSoln"]["Design"] == "Y_Connections"
        assert aedtapp.setups[0].props["PrevSoln"]["Soln"] == "Setup1 : Transient"
        assert not aedtapp.setups[0].start_continue_from_previous_setup(design="", solution="Setup1 : Transient")
        assert not aedtapp.setups[0].start_continue_from_previous_setup(design="Y_Connections", solution="")
        assert not aedtapp.setups[0].start_continue_from_previous_setup(design="", solution="")
        example_project = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, test_name + ".aedt")
        example_project_copy = os.path.join(local_scratch.path, test_name + "_copy.aedt")
        shutil.copyfile(example_project, example_project_copy)
        assert os.path.exists(example_project_copy)
        aedtapp.create_setup(name="test_setup")
        assert aedtapp.setups[1].start_continue_from_previous_setup(
            design="Y_Connections", solution="Setup1 : Transient", project=example_project_copy
        )
        assert aedtapp.setups[1].props["PrevSoln"]["Project"] == example_project_copy
        assert aedtapp.setups[1].props["PrevSoln"]["Design"] == "Y_Connections"
        assert aedtapp.setups[1].props["PrevSoln"]["Soln"] == "Setup1 : Transient"

    def test_design_excitations_by_type(self, aedtapp):
        coils = aedtapp.excitations_by_type["Coil"]
        assert coils
        assert len(coils) == len([bound for bound in aedtapp.excitation_objects.values() if bound.type == "Coil"])
        currents = aedtapp.excitations_by_type["Current"]
        assert currents
        assert len(currents) == len([bound for bound in aedtapp.excitation_objects.values() if bound.type == "Current"])
        wdg_group = aedtapp.excitations_by_type["Winding Group"]
        assert wdg_group
        assert len(wdg_group) == len(
            [bound for bound in aedtapp.excitation_objects.values() if bound.type == "Winding Group"]
        )

    def test_boundaries_by_type(self, aedtapp):
        coils = aedtapp.boundaries_by_type["Coil"]
        assert coils
        assert len(coils) == len([bound for bound in aedtapp.boundaries if bound.type == "Coil"])
        currents = aedtapp.boundaries_by_type["Current"]
        assert currents
        assert len(currents) == len([bound for bound in aedtapp.boundaries if bound.type == "Current"])
        wdg_group = aedtapp.boundaries_by_type["Winding Group"]
        assert wdg_group
        assert len(wdg_group) == len([bound for bound in aedtapp.boundaries if bound.type == "Winding Group"])

    def test_export_field_file(self, local_scratch, m2d_fields):
        output_file = os.path.join(local_scratch.path, "e_tang_field.fld")
        assert m2d_fields.post.export_field_file(
            quantity="E_Line", output_file=output_file, assignment="Poly1", objects_type="Line"
        )
        assert os.path.exists(output_file)

    def test_control_program(self, m2d_ctrl_prg):
        user_ctl_path = "user.ctl"
        ctrl_prg_path = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, ctrl_prg_file)
        assert m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path)
        assert m2d_ctrl_prg.setups[0].enable_control_program(
            control_program_path=ctrl_prg_path, control_program_args="3"
        )
        assert not m2d_ctrl_prg.setups[0].enable_control_program(
            control_program_path=ctrl_prg_path, control_program_args=3
        )
        assert m2d_ctrl_prg.setups[0].enable_control_program(
            control_program_path=ctrl_prg_path, call_after_last_step=True
        )
        invalid_ctrl_prg_path = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "invalid.py")
        assert not m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=invalid_ctrl_prg_path)
        m2d_ctrl_prg.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        assert not m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path)
        if os.path.exists(user_ctl_path):
            os.unlink(user_ctl_path)

    @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    def test_import_dxf(self, m2d_app):
        dxf_file = os.path.join(TESTS_GENERAL_PATH, "example_models", "cad", "DXF", "dxf2.dxf")
        dxf_layers = m2d_app.get_dxf_layers(dxf_file)
        assert isinstance(dxf_layers, list)
        assert m2d_app.import_dxf(dxf_file, dxf_layers)
        dxf_layers = ["invalid", "invalid1"]
        assert not m2d_app.import_dxf(dxf_file, dxf_layers)

    def test_assign_floating(self, m2d_app):
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.ElectroStaticXY
        rect = m2d_app.modeler.create_rectangle([0, 0, 0], [3, 1])
        floating = m2d_app.assign_floating(assignment=rect, charge_value=3, name="floating_test")
        assert floating
        assert floating.name == "floating_test"
        assert floating.props["Objects"][0] == rect.name
        assert floating.props["Value"] == "3"
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticXY
        floating = m2d_app.assign_floating(assignment=rect, charge_value=3, name="floating_test1")
        assert not floating

    def test_matrix(self, m2d_app):
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticXY
        m2d_app.modeler.create_rectangle([0, 1.5, 0], [8, 3], is_covered=True, name="Coil_1", material="vacuum")
        m2d_app.modeler.create_rectangle([8.5, 1.5, 0], [8, 3], is_covered=True, name="Coil_2", material="vacuum")
        m2d_app.modeler.create_rectangle([16, 1.5, 0], [8, 3], is_covered=True, name="Coil_3", material="vacuum")
        m2d_app.modeler.create_rectangle([32, 1.5, 0], [8, 3], is_covered=True, name="Coil_4", material="vacuum")
        m2d_app.assign_current("Coil_1", amplitude=1, swap_direction=False, name="Current1")
        m2d_app.assign_current("Coil_2", amplitude=1, swap_direction=True, name="Current2")
        m2d_app.assign_current("Coil_3", amplitude=1, swap_direction=True, name="Current3")
        m2d_app.assign_current("Coil_4", amplitude=1, swap_direction=True, name="Current4")
        matrix = m2d_app.assign_matrix(assignment="Current1")
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["Source"] == "Current1"
        assert matrix.delete()
        matrix = m2d_app.assign_matrix(
            assignment=["Current1", "Current2"], matrix_name="Test1", turns=2, return_path="Current3"
        )
        assert len(matrix.props["MatrixEntry"]["MatrixEntry"]) == 2
        matrix = m2d_app.assign_matrix(
            assignment=["Current1", "Current2"], matrix_name="Test2", turns=[2, 1], return_path=["Current3", "Current4"]
        )
        assert matrix.props["MatrixEntry"]["MatrixEntry"][1]["ReturnPath"] == "Current4"
        matrix = m2d_app.assign_matrix(
            assignment=["Current1", "Current2"], matrix_name="Test3", turns=[2, 1], return_path=["Current1", "Current1"]
        )
        assert not matrix
        group_sources = {"Group1_Test": ["Current3", "Current2"]}
        matrix = m2d_app.assign_matrix(
            assignment=["Current3", "Current2"],
            matrix_name="Test4",
            turns=[2, 1],
            return_path=["Current4", "Current1"],
            group_sources=group_sources,
        )
        assert matrix.name == "Test4"
        group_sources = {"Group1_Test": ["Current3", "Current2"], "Group2_Test": ["Current1", "Current2"]}
        matrix = m2d_app.assign_matrix(
            assignment=["Current1", "Current2"],
            matrix_name="Test5",
            turns=[2, 1],
            return_path="infinite",
            group_sources=group_sources,
        )
        assert matrix.props["MatrixGroup"]["MatrixGroup"]
        group_sources = {"Group1_Test": ["Current1", "Current3"], "Group2_Test": ["Current2", "Current4"]}
        matrix = m2d_app.assign_matrix(
            assignment=["Current1", "Current2", "Current3", "Current4"],
            matrix_name="Test6",
            turns=2,
            group_sources=group_sources,
            branches=3,
        )
        assert matrix.props["MatrixGroup"]["MatrixGroup"][0]["GroupName"] == "Group1_Test"
        group_sources = {"Group1_Test": ["Current1", "Current3"], "Group2_Test": ["Current2", "Current4"]}
        matrix = m2d_app.assign_matrix(
            assignment=["Current1", "Current2", "Current3", "Current4"],
            matrix_name="Test7",
            turns=[5, 1],
            group_sources=group_sources,
            branches=[3, 2, 1],
        )
        assert len(matrix.props["MatrixGroup"]["MatrixGroup"]) == 2
        group_sources = {"Group1_Test": ["Current1", "Current3", "Current2"], "Group2_Test": ["Current2", "Current4"]}
        matrix = m2d_app.assign_matrix(
            assignment=["Current1", "Current2", "Current3"],
            matrix_name="Test8",
            turns=[2, 1, 2, 3],
            return_path=["infinite", "infinite", "Current4"],
            group_sources=group_sources,
            branches=[3, 2],
        )
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] == 2
        matrix.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] = 3
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] == 3
        group_sources = {"Group1_Test": ["Current1", "Current3"], "Group2_Test": ["Current2", "Current4"]}
        matrix = m2d_app.assign_matrix(
            assignment=["Current1", "Current2", "Current3", "Current4"],
            matrix_name="Test9",
            turns=[5, 1, 2, 3],
            group_sources=group_sources,
            branches=[3, 2],
        )
        for l in matrix.props["MatrixEntry"]["MatrixEntry"]:
            assert l["ReturnPath"] == "infinite"

    def test_solution_types_setup(self, m2d_app):
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.TransientXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.TransientZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.ElectroStaticXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.ElectroStaticZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.DCConductionXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.DCConductionZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.ACConductionXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.ACConductionZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()

    def test_create_external_circuit(self, local_scratch, m2d_app):
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        m2d_app.modeler.create_circle([0, 0, 0], 10, name="Coil1")
        m2d_app.modeler.create_circle([20, 0, 0], 10, name="Coil2")

        m2d_app.assign_coil(assignment=["Coil1"])
        m2d_app.assign_coil(assignment=["Coil2"])

        m2d_app.assign_winding(assignment=["Coil1"])
        m2d_app.assign_winding(assignment=["Coil2"])

        assert m2d_app.create_external_circuit()
        assert m2d_app.create_external_circuit(circuit_design="test_cir")
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticXY
        assert not m2d_app.create_external_circuit()
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        for w in m2d_app.excitations_by_type["Winding"]:
            w.delete()
        m2d_app.save_project()
        assert not m2d_app.create_external_circuit()

    def test_assign_voltage(self, local_scratch, m2d_app):
        m2d_app.solution_type = SOLUTIONS.Maxwell2d.ElectroStaticZ

        region_id = m2d_app.modeler.create_region(pad_value=[500, 50, 50])
        v1 = m2d_app.assign_voltage(assignment=region_id, amplitude=0, name="GRD1")
        assert v1.properties["Value"] == "0mV"
        assert len(m2d_app.boundaries) == 1
        assert m2d_app.assign_voltage(assignment=region_id.edges[0], amplitude=1, name="GRD2")
        assert m2d_app.assign_voltage(assignment=[region_id.name, region_id.edges], amplitude=2, name="GRD3")
        assert len(m2d_app.boundaries) == 3
