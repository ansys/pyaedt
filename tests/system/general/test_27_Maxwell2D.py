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

from pathlib import Path
import shutil

import pytest

import ansys.aedt.core
from ansys.aedt.core.generic.constants import SolutionsMaxwell2D
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH
from tests.conftest import config

test_subfolder = "TMaxwell"

test_name = "Maxwell_2D_Tests"
design_name = "Basis_Model_For_Test"

ctrl_prg = "TimeStepCtrl"
ctrl_prg_file = "timestep_only.py"

m2d_export_fields = "maxwell_e_line_export_field"
sinusoidal_name = "Sinusoidal"

m2d_transient_ec = "Setup_Transient_EC"

export_rl_c_matrix = "export_matrix"


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
def sinusoidal(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d, project_name=sinusoidal_name, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def m2d_ctrl_prg(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d, project_name=ctrl_prg, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def m2d_export_matrix(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d, project_name=export_rl_c_matrix, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def m2d_app(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def m2d_setup(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d, project_name=m2d_transient_ec, subfolder=test_subfolder)
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
        aedtapp.solution_type = "Electrostatic"
        aedtapp.assign_balloon(region.edges, is_voltage=True)

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

    def test_assign_current_source(self, m2d_app):
        coil = m2d_app.modeler.create_circle(
            position=[0, 0, 0], radius=5, num_sides="8", is_covered=True, name="Coil", material="Copper"
        )
        assert m2d_app.assign_current([coil])
        m2d_app.solution_type = SolutionsMaxwell2D.EddyCurrentXY
        assert m2d_app.assign_current([coil], phase="-120deg")
        with pytest.raises(ValueError, match="Input must be a 2D object."):
            m2d_app.assign_current([coil.faces[0].id])

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
        with pytest.raises(AEDTRuntimeError, match=r"Failed to create boundary Dependent Dependent_[A-Za-z0-9]*$"):
            aedtapp.assign_master_slave(
                aedtapp.modeler["Rectangle1"].edges[0].id,
                aedtapp.modeler["Rectangle1"].edges[1].id,
            )

    def test_check_design_preview_image(self, local_scratch, aedtapp):
        jpg_file = Path(local_scratch.path) / "file.jpg"
        assert aedtapp.export_design_preview_to_jpg(jpg_file)

    def test_model_depth(self, aedtapp):
        assert aedtapp.change_design_settings({"ModelDepth": "3mm"})

    def test_apply_skew(self, aedtapp):
        assert aedtapp.apply_skew()
        with pytest.raises(ValueError, match="Invalid skew type."):
            assert not aedtapp.apply_skew(skew_type="Invalid")
        with pytest.raises(ValueError, match="Invalid skew angle unit."):
            aedtapp.apply_skew(skew_type="Continuous", skew_part="Stator", skew_angle="0.5", skew_angle_unit="Invalid")
        with pytest.raises(ValueError, match="Please provide skew angles for each slice."):
            aedtapp.apply_skew(
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

    def test_delete_motion_setup(self, aedtapp):
        aedtapp.xy_plane = True
        aedtapp.modeler.create_circle([0, 0, 0], 10, name="Circle_inner")
        aedtapp.modeler.create_circle([0, 0, 0], 30, name="Circle_outer")
        bound = aedtapp.assign_rotate_motion("Circle_outer", positive_limit=300, mechanical_transient=True)
        assert bound
        assert len(aedtapp.boundaries_by_type["Band"]) == 2
        bound.delete()
        assert len(aedtapp.boundaries_by_type["Band"]) == 1

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
        with pytest.raises(AEDTRuntimeError, match="At least 2 objects are needed."):
            aedtapp.assign_end_connection([rect])
        aedtapp.solution_type = SolutionsMaxwell2D.MagnetostaticXY
        with pytest.raises(AEDTRuntimeError):
            aedtapp.assign_end_connection([rect, rect2])

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
        with pytest.raises(ValueError, match="At least one edge must be provided."):
            aedtapp.assign_symmetry([])
        for bound in aedtapp.boundaries:
            if bound.name == "Symmetry_Test_IsOdd":
                assert bound.type == "Symmetry"
                assert bound.props["IsOdd"]
            if bound.name == "Symmetry_Test_IsEven":
                assert bound.type == "Symmetry"
                assert not bound.props["IsOdd"]

    def test_assign_current_density(self, sinusoidal):
        sinusoidal.set_active_design("Sinusoidal")
        bound = sinusoidal.assign_current_density("Coil", "CurrentDensity_1")
        assert bound
        assert bound.props["Objects"] == ["Coil"]
        assert bound.props["Value"] == "0"
        assert bound.props["CoordinateSystem"] == ""
        bound2 = sinusoidal.assign_current_density("Coil", "CurrentDensity_2", "40deg", current_density_2d="2")
        assert bound2
        assert bound2.props["Objects"] == ["Coil"]
        assert bound2.props["Value"] == "2"
        assert bound2.props["CoordinateSystem"] == ""
        bound_group = sinusoidal.assign_current_density(["Coil", "Coil_1"], "CurrentDensityGroup_1")
        assert bound_group
        assert bound_group.props[bound_group.props["items"][0]]["Objects"] == ["Coil", "Coil_1"]
        assert bound_group.props[bound_group.props["items"][0]]["Value"] == "0"
        assert bound_group.props[bound_group.props["items"][0]]["CoordinateSystem"] == ""
        with pytest.raises(AEDTRuntimeError, match="Couldn't assign current density to desired list of objects."):
            sinusoidal.assign_current_density("Circle_inner", "CurrentDensity_1")

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
        example_project = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / (test_name + ".aedt")
        example_project_copy = Path(local_scratch.path) / (test_name + "_copy.aedt")
        shutil.copyfile(example_project, example_project_copy)
        assert example_project_copy.exists()
        aedtapp.create_setup(name="test_setup")
        assert aedtapp.setups[1].start_continue_from_previous_setup(
            design="Y_Connections", solution="Setup1 : Transient", project=example_project_copy
        )
        assert aedtapp.setups[1].props["PrevSoln"]["Project"] == str(example_project_copy)
        assert aedtapp.setups[1].props["PrevSoln"]["Design"] == "Y_Connections"
        assert aedtapp.setups[1].props["PrevSoln"]["Soln"] == "Setup1 : Transient"

    def test_design_excitations_by_type(self, aedtapp):
        coils = aedtapp.excitations_by_type["Coil"]
        assert coils
        assert len(coils) == len([bound for bound in aedtapp.design_excitations.values() if bound.type == "Coil"])
        currents = aedtapp.excitations_by_type["Current"]
        assert currents
        assert len(currents) == len([bound for bound in aedtapp.design_excitations.values() if bound.type == "Current"])
        wdg_group = aedtapp.excitations_by_type["Winding Group"]
        assert wdg_group
        assert len(wdg_group) == len(
            [bound for bound in aedtapp.design_excitations.values() if bound.type == "Winding Group"]
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
        output_file = Path(local_scratch.path) / "e_tang_field.fld"
        assert m2d_fields.post.export_field_file(
            quantity="E_Line", output_file=output_file, assignment="Poly1", objects_type="Line"
        )
        assert output_file.exists()

    def test_control_program(self, m2d_ctrl_prg):
        user_ctl_path = Path("user.ctl")
        ctrl_prg_path = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / ctrl_prg_file
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
        invalid_ctrl_prg_path = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "invalid.py"
        assert not m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=invalid_ctrl_prg_path)
        m2d_ctrl_prg.solution_type = SolutionsMaxwell2D.EddyCurrentXY
        assert not m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path)
        if user_ctl_path.exists():
            user_ctl_path.unlink()

    @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    def test_import_dxf(self, m2d_app):
        dxf_file = Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "DXF" / "dxf2.dxf"
        dxf_layers = m2d_app.get_dxf_layers(dxf_file)
        assert isinstance(dxf_layers, list)
        assert m2d_app.import_dxf(dxf_file, dxf_layers)
        dxf_layers = ["invalid", "invalid1"]
        assert not m2d_app.import_dxf(dxf_file, dxf_layers)

    def test_assign_floating(self, m2d_app):
        m2d_app.solution_type = SolutionsMaxwell2D.ElectroStaticXY
        rect = m2d_app.modeler.create_rectangle([0, 0, 0], [3, 1])
        floating = m2d_app.assign_floating(assignment=rect, charge_value=3, name="floating_test")
        assert floating
        assert floating.name == "floating_test"
        assert floating.props["Objects"][0] == rect.name
        assert floating.props["Value"] == "3"
        m2d_app.solution_type = SolutionsMaxwell2D.MagnetostaticXY
        with pytest.raises(
            AEDTRuntimeError,
            match="Assign floating excitation is only valid for electrostatic or electric transient solvers.",
        ):
            m2d_app.assign_floating(assignment=rect, charge_value=3, name="floating_test1")

    def test_matrix(self, m2d_app):
        m2d_app.solution_type = SolutionsMaxwell2D.MagnetostaticXY
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
        with pytest.raises(AEDTRuntimeError, match="Return path specified must not be included in sources"):
            m2d_app.assign_matrix(
                assignment=["Current1", "Current2"],
                matrix_name="Test3",
                turns=[2, 1],
                return_path=["Current1", "Current1"],
            )
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
        for val in matrix.props["MatrixEntry"]["MatrixEntry"]:
            assert val["ReturnPath"] == "infinite"

    def test_solution_types_setup(self, m2d_app):
        m2d_app.solution_type = SolutionsMaxwell2D.TransientXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.TransientZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.MagnetostaticXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.MagnetostaticZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.EddyCurrentXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.EddyCurrentZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.ElectroStaticXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.ElectroStaticZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.DCConductionXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.DCConductionZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.ACConductionXY
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()
        m2d_app.solution_type = SolutionsMaxwell2D.ACConductionZ
        setup = m2d_app.create_setup(setup_type=m2d_app.solution_type)
        assert setup
        setup.delete()

    def test_create_external_circuit(self, local_scratch, m2d_app):
        m2d_app.solution_type = SolutionsMaxwell2D.EddyCurrentXY
        m2d_app.modeler.create_circle([0, 0, 0], 10, name="Coil1")
        m2d_app.modeler.create_circle([20, 0, 0], 10, name="Coil2")

        m2d_app.assign_coil(assignment=["Coil1"])
        m2d_app.assign_coil(assignment=["Coil2"])

        m2d_app.assign_winding(assignment=["Coil1"])
        m2d_app.assign_winding(assignment=["Coil2"])

        assert m2d_app.create_external_circuit()
        assert m2d_app.create_external_circuit(circuit_design="test_cir")
        m2d_app.solution_type = SolutionsMaxwell2D.MagnetostaticXY
        with pytest.raises(AEDTRuntimeError):
            m2d_app.create_external_circuit()
        m2d_app.solution_type = SolutionsMaxwell2D.EddyCurrentXY
        for w in m2d_app.excitations_by_type["Winding"]:
            w.delete()
        m2d_app.save_project()
        with pytest.raises(
            AEDTRuntimeError,
            match="No windings in the Maxwell design.",
        ):
            m2d_app.create_external_circuit()

    def test_assign_voltage(self, local_scratch, m2d_app):
        m2d_app.solution_type = SolutionsMaxwell2D.ElectroStaticZ

        region_id = m2d_app.modeler.create_region(pad_value=[500, 50, 50])
        v1 = m2d_app.assign_voltage(assignment=region_id, amplitude=0, name="GRD1")
        assert v1.properties["Value"] == "0mV"
        assert len(m2d_app.boundaries) == 1
        assert m2d_app.assign_voltage(assignment=region_id.edges[0], amplitude=1, name="GRD2")
        assert m2d_app.assign_voltage(assignment=region_id.edges, amplitude=2, name="GRD3")
        rect = m2d_app.modeler.create_rectangle([32, 1.5, 0], [8, 3], is_covered=True)
        assert m2d_app.assign_voltage(assignment=[region_id.name, rect.name], amplitude=3, name="GRD4")
        assert len(m2d_app.boundaries) == 4

    def test_set_save_fields(self, m2d_setup):
        m2d_setup.set_active_design("setup_transient")

        setup = m2d_setup.setups[0]
        assert setup.set_save_fields(
            enable=True, range_type="Custom", subrange_type="LinearStep", start=0, stop=8, count=2, units="ms"
        )
        assert len(setup.props["SweepRanges"]["Subrange"]) == 2
        assert setup.props["SweepRanges"]["Subrange"][1]["RangeType"] == "LinearStep"
        assert setup.props["SweepRanges"]["Subrange"][1]["RangeStart"] == "0ms"
        assert setup.props["SweepRanges"]["Subrange"][1]["RangeEnd"] == "8ms"
        assert setup.props["SweepRanges"]["Subrange"][1]["RangeStep"] == "2ms"
        assert setup.set_save_fields(
            enable=True, range_type="Custom", subrange_type="LinearCount", start=0, stop=8, count=2, units="ms"
        )
        assert len(setup.props["SweepRanges"]["Subrange"]) == 3
        assert setup.props["SweepRanges"]["Subrange"][2]["RangeType"] == "LinearCount"
        assert setup.props["SweepRanges"]["Subrange"][2]["RangeStart"] == "0ms"
        assert setup.props["SweepRanges"]["Subrange"][2]["RangeEnd"] == "8ms"
        assert setup.props["SweepRanges"]["Subrange"][2]["RangeCount"] == 2
        assert setup.set_save_fields(
            enable=True, range_type="Custom", subrange_type="SinglePoints", start=3, units="ms"
        )
        assert len(setup.props["SweepRanges"]["Subrange"]) == 4
        assert setup.props["SweepRanges"]["Subrange"][3]["RangeType"] == "SinglePoints"
        assert setup.props["SweepRanges"]["Subrange"][3]["RangeStart"] == "3ms"
        assert setup.props["SweepRanges"]["Subrange"][3]["RangeEnd"] == "3ms"
        assert setup.set_save_fields(enable=True, range_type="Every N Steps", start=0, stop=10, count=1, units="ms")
        assert setup.props["SaveFieldsType"] == "Every N Steps"
        assert setup.props["Steps From"] == "0ms"
        assert setup.props["Steps To"] == "10ms"
        assert setup.props["N Steps"] == "1"
        assert setup.set_save_fields(
            enable=True, range_type="Custom", subrange_type="SinglePoints", start=3, units="ms"
        )
        assert len(setup.props["SweepRanges"]["Subrange"]) == 1
        assert setup.props["SweepRanges"]["Subrange"][0]["RangeType"] == "SinglePoints"
        assert setup.props["SweepRanges"]["Subrange"][0]["RangeStart"] == "3ms"
        assert setup.props["SweepRanges"]["Subrange"][0]["RangeEnd"] == "3ms"
        assert setup.set_save_fields(range_type="None")
        assert setup.set_save_fields(enable=False)
        assert not setup.set_save_fields(enable=True, range_type="invalid")

        m2d_setup.solution_type = SolutionsMaxwell2D.MagnetostaticXY

        setup = m2d_setup.create_setup()
        assert setup.set_save_fields(enable=True)
        assert setup.set_save_fields(enable=False)

    @pytest.mark.skipif(
        config["desktopVersion"] < "2025.1",
        reason="Not working in non-graphical in version lower than 2025.1",
    )
    def test_eddy_current_sweep(self, m2d_setup):
        m2d_setup.set_active_design("setup_ec")
        setup = m2d_setup.setups[0]
        setup.props["MaximumPasses"] = 12

        setup.props["MinimumPasses"] = 2
        setup.props["MinimumConvergedPasses"] = 1
        setup.props["PercentRefinement"] = 30
        setup.props["Frequency"] = "200Hz"
        dc_freq = 0.1
        stop_freq = 10
        count = 1
        sweep = setup.add_eddy_current_sweep(
            sweep_type="LinearStep", start_frequency=dc_freq, stop_frequency=stop_freq, step_size=count, clear=False
        )
        assert sweep.props["RangeType"] == "LinearStep"
        assert sweep.props["RangeStart"] == "0.1Hz"
        assert sweep.props["RangeEnd"] == "10Hz"
        assert sweep.props["RangeStep"] == "1Hz"
        assert isinstance(setup.props["SweepRanges"]["Subrange"], list)
        m2d_setup.save_project()
        assert len(setup.props["SweepRanges"]["Subrange"]) == 2
        assert len(setup.sweeps) == 2
        assert setup.props["SaveAllFields"]
        assert setup.delete_all_eddy_current_sweeps()
        assert "SweepRanges" not in setup.props
        assert len(setup.sweeps) == 0
        sweep = setup.add_eddy_current_sweep(
            sweep_type="LinearCount", start_frequency=dc_freq, stop_frequency=stop_freq, step_size=count, clear=False
        )
        assert sweep.props["RangeType"] == "LinearCount"
        assert sweep.props["RangeStart"] == "0.1Hz"
        assert sweep.props["RangeEnd"] == "10Hz"
        assert sweep.props["RangeCount"] == 1
        assert isinstance(setup.props["SweepRanges"]["Subrange"], list)
        m2d_setup.save_project()
        assert len(setup.props["SweepRanges"]["Subrange"]) == 1
        assert len(setup.sweeps) == 1
        sweep = setup.add_eddy_current_sweep(
            sweep_type="LogScale", start_frequency=dc_freq, stop_frequency=stop_freq, step_size=count, clear=True
        )
        assert sweep.props["RangeType"] == "LogScale"
        assert sweep.props["RangeStart"] == "0.1Hz"
        assert sweep.props["RangeEnd"] == "10Hz"
        assert sweep.props["RangeSamples"] == 1
        assert isinstance(setup.props["SweepRanges"]["Subrange"], list)
        m2d_setup.save_project()
        assert len(setup.props["SweepRanges"]["Subrange"]) == 1
        assert len(setup.sweeps) == 1
        sweep = setup.add_eddy_current_sweep(sweep_type="SinglePoints", start_frequency=0.01, clear=False)
        assert sweep.props["RangeType"] == "SinglePoints"
        assert sweep.props["RangeStart"] == "0.01Hz"
        assert sweep.props["RangeEnd"] == "0.01Hz"
        m2d_setup.save_project()
        assert len(setup.props["SweepRanges"]["Subrange"]) == 2
        assert len(setup.sweeps) == 2
        assert sweep.delete()
        m2d_setup.save_project()
        assert len(setup.props["SweepRanges"]["Subrange"]) == 1
        assert len(setup.sweeps) == 1
        assert setup.update()
        assert setup.enable_expression_cache(["CoreLoss"], "Fields", "Phase='0deg' ", True)
        assert setup.props["UseCacheFor"] == ["Pass", "Freq"]
        assert setup.disable()
        assert setup.enable()
        assert not sweep.is_solved
        assert isinstance(sweep.frequencies, list)

    def test_export_c_matrix(self, local_scratch, m2d_export_matrix):
        output_file = Path(local_scratch.path) / "c_matrix.txt"
        # invalid solution type
        m2d_export_matrix.set_active_design("export_rl_magneto")
        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.export_rl_matrix("Matrix1", output_file)
        # no matrix
        m2d_export_matrix.set_active_design("export_c_electrostatic_no_matrix")
        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.export_c_matrix(matrix_name="Matrix1", output_file=output_file)

        m2d_export_matrix.set_active_design("export_c_electrostatic")
        assert m2d_export_matrix.export_c_matrix(matrix_name="Matrix1", output_file=output_file)
        assert output_file.exists()

        assert m2d_export_matrix.setups[0].export_matrix(
            matrix_type="C", matrix_name="Matrix1", output_file=output_file
        )
        assert output_file.exists()

        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.export_c_matrix(matrix_name="invalid", output_file=output_file)

        m2d_export_matrix.set_active_design("export_c_electrostatic_param")

        assert m2d_export_matrix.export_c_matrix(matrix_name="Matrix1", output_file=output_file)
        assert output_file.exists()

        assert m2d_export_matrix.setups[0].export_matrix(
            matrix_type="C", matrix_name="Matrix1", output_file=output_file
        )
        assert output_file.exists()

        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.setups[0].export_matrix(
                matrix_type="invalid", matrix_name="Matrix1", output_file=output_file
            )

        output_file = Path(local_scratch.path) / "c_matrix.csv"
        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.export_c_matrix(matrix_name="Matrix1", output_file=output_file)

    def test_export_rl_matrix(self, local_scratch, m2d_export_matrix):
        # invalid path
        export_path = Path(local_scratch.path) / "export_rl_matrix.csv"
        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.export_rl_matrix("Matrix1", export_path)

        export_path = Path(local_scratch.path) / "export_rl_matrix.txt"
        # invalid solution type
        m2d_export_matrix.set_active_design("export_rl_magneto")
        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.export_rl_matrix("Matrix1", export_path)
        # no matrix
        m2d_export_matrix.set_active_design("export_rl_eddycurrent_no_matrix")
        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.export_rl_matrix("Matrix1", export_path)
        # no setup
        if config["desktopVersion"] < "2025.2":  # AEDT API not raising exception
            m2d_export_matrix.set_active_design("export_rl_eddycurrent_unsolved")
            with pytest.raises(AEDTRuntimeError):
                m2d_export_matrix.export_rl_matrix("Matrix1", export_path, False, 10, 3, True)
        # EC
        m2d_export_matrix.set_active_design("export_rl_eddycurrent")
        assert m2d_export_matrix.export_rl_matrix("Matrix1", export_path)
        assert export_path.exists()
        with pytest.raises(AEDTRuntimeError):
            m2d_export_matrix.export_rl_matrix("invalid", export_path)
        # EC param
        m2d_export_matrix.set_active_design("export_rl_eddycurrent_param")
        export_path_1 = Path(local_scratch.path) / "export_rl_matrix_1.txt"
        assert m2d_export_matrix.export_rl_matrix("Matrix1", export_path_1, False, 10, 3, True)
        assert export_path_1.exists()
        export_path_2 = Path(local_scratch.path) / "export_rl_matrix_2.txt"
        assert m2d_export_matrix.setups[0].export_matrix(
            matrix_type="RL", matrix_name="Matrix1", output_file=export_path_2
        )
        assert export_path_2.exists()

    def test_analyze_from_zero(self, m2d_app):
        m2d_app.solution_type = SolutionsMaxwell2D.TransientXY
        conductor = m2d_app.modeler.create_circle(origin=[0, 0, 0], radius=10, material="Copper")
        m2d_app.assign_winding(assignment=conductor.name, is_solid=False, current="5*cos(2*PI*50*time)")
        region = m2d_app.modeler.create_region(pad_percent=100)
        bound = m2d_app.assign_balloon(region.edges)
        setup1 = m2d_app.create_setup()
        setup1.props["StopTime"] = "2/50s"
        setup1.props["TimeStep"] = "1/500s"
        assert m2d_app.analyze_from_zero()
        bound.delete()
        m2d_app.assign_vector_potential(assignment=region.edges)
        assert m2d_app.analyze_from_zero()
        m2d_app.solution_type = SolutionsMaxwell2D.MagnetostaticXY
        m2d_app.create_setup()
        with pytest.raises(AEDTRuntimeError):
            m2d_app.analyze_from_zero()
