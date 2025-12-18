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
from ansys.aedt.core.generic.file_utils import get_dxf_layers
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION
from tests.conftest import NON_GRAPHICAL

TEST_SUBFOLDER = "TMaxwell"

TEST_NAME = "Maxwell_2D_Tests"
TEST_DESIGN_NAME = "Basis_Model_For_Test"

CTRL_PRG_PROJECT = "TimeStepCtrl"
CTRL_PRG_FILE = "timestep_only.py"

M2D_EXPORT_FIELD = "maxwell_e_line_export_field"
SINUSOIDAL_NAME = "Sinusoidal"

M2D_TRANSIENT_EC = "Setup_Transient_EC"

EXPORT_RLC_MATRIX = "export_matrix"


@pytest.fixture
def aedt_app(add_app_example):
    app = add_app_example(
        project=TEST_NAME,
        design=TEST_DESIGN_NAME,
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m2d_fields(add_app_example):
    app = add_app_example(application=ansys.aedt.core.Maxwell2d, project=M2D_EXPORT_FIELD, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def sinusoidal(add_app_example):
    app = add_app_example(application=ansys.aedt.core.Maxwell2d, project=SINUSOIDAL_NAME, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m2d_ctrl_prg(add_app_example):
    app = add_app_example(application=ansys.aedt.core.Maxwell2d, project=CTRL_PRG_PROJECT, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m2d_export_matrix(add_app_example):
    app = add_app_example(application=ansys.aedt.core.Maxwell2d, project=EXPORT_RLC_MATRIX, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m2d_app(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m2d_setup(add_app_example):
    app = add_app_example(application=ansys.aedt.core.Maxwell2d, project=M2D_TRANSIENT_EC, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def test_assign_initial_mesh_from_slider(aedt_app):
    assert aedt_app.mesh.assign_initial_mesh_from_slider(4)
    with pytest.raises(ValueError):
        aedt_app.mesh.assign_initial_mesh_from_slider(method="dummy")
    with pytest.raises(ValueError):
        aedt_app.mesh.assign_initial_mesh(method="dummy")


def test_assign_winding(aedt_app):
    bounds = aedt_app.assign_winding(assignment=["Coil"], current=20e-3)
    assert bounds
    o = aedt_app.modeler.create_rectangle([0, 0, 0], [3, 1], name="Rectangle", material="copper")
    bounds = aedt_app.assign_winding(assignment=o.id, current=20e-3)
    assert bounds
    bounds = aedt_app.assign_winding(assignment=["Coil"], current="20e-3A")
    assert bounds
    bounds = aedt_app.assign_winding(assignment=["Coil"], resistance="1ohm")
    assert bounds
    bounds = aedt_app.assign_winding(assignment=["Coil"], inductance="1H")
    assert bounds
    bounds = aedt_app.assign_winding(assignment=["Coil"], voltage="10V")
    assert bounds
    bounds_name = ansys.aedt.core.generate_unique_name("Coil")
    bounds = aedt_app.assign_winding(assignment=["Coil"], name=bounds_name)
    assert bounds_name == bounds.name


def test_assign_coil(aedt_app):
    bound = aedt_app.assign_coil(assignment=["Coil"])
    assert bound
    polarity = "Positive"
    bound = aedt_app.assign_coil(assignment=["Coil"], polarity=polarity)
    assert bound.props["PolarityType"] == polarity.lower()
    polarity = "Negative"
    bound = aedt_app.assign_coil(assignment=["Coil"], polarity=polarity)
    assert bound.props["PolarityType"] == polarity.lower()
    bound_name = ansys.aedt.core.generate_unique_name("Coil")
    bound = aedt_app.assign_coil(assignment=["Coil"], name=bound_name)
    assert bound_name == bound.name


def test_create_vector_potential(aedt_app):
    region = aedt_app.modeler["Region"]
    edge_object = region.edges[0]
    bounds = aedt_app.assign_vector_potential(edge_object.id, 3)
    assert bounds
    assert bounds.props["Value"] == "3"
    bounds["Value"] = "2"
    assert bounds.props["Value"] == "2"
    line = aedt_app.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="myline")
    bound2 = aedt_app.assign_vector_potential(line.id, 2)
    assert bound2
    assert bound2.props["Value"] == "2"
    assert bound2.update()


def test_create_setup(aedt_app):
    mysetup = aedt_app.create_setup()
    mysetup.props["SaveFields"] = True
    assert mysetup.update()


def test_assign_balloon(aedt_app):
    region = aedt_app.modeler["Region"]
    aedt_app.assign_balloon(region.edges)
    aedt_app.solution_type = "Electrostatic"
    aedt_app.assign_balloon(region.edges, is_voltage=True)


def test_generate_design_data(aedt_app):
    assert aedt_app.generate_design_data()
    assert aedt_app.read_design_data()


def test_assign_torque(aedt_app):
    torque = aedt_app.assign_torque("Rotor_Section1")
    assert torque.type == "Torque"
    assert torque.props["Objects"][0] == "Rotor_Section1"
    assert torque.props["Is Positive"]
    assert torque.delete()
    torque = aedt_app.assign_torque(assignment="Rotor_Section1", is_positive=False, torque_name="Torque_Test")
    assert torque.name == "Torque_Test"
    assert not torque.props["Is Positive"]
    assert torque.props["Objects"][0] == "Rotor_Section1"


def test_assign_force(aedt_app):
    force = aedt_app.assign_force("Magnet2_Section1")
    assert force.type == "Force"
    assert force.props["Objects"][0] == "Magnet2_Section1"
    assert force.props["Reference CS"] == "Global"
    assert force.delete()
    force = aedt_app.assign_force(assignment="Magnet2_Section1", force_name="Force_Test")
    assert force.name == "Force_Test"


def test_assign_current_source(m2d_app):
    coil = m2d_app.modeler.create_circle(
        origin=[0, 0, 0], radius=5, num_sides="8", is_covered=True, name="Coil", material="Copper"
    )
    assert m2d_app.assign_current([coil])
    m2d_app.solution_type = SolutionsMaxwell2D.EddyCurrentXY
    assert m2d_app.assign_current([coil], phase="-120deg")
    with pytest.raises(ValueError, match="Input must be a 2D object."):
        m2d_app.assign_current([coil.faces[0].id])


def test_assign_master_slave(aedt_app):
    aedt_app.modeler.create_rectangle([1, 1, 1], [3, 1], name="Rectangle1", material="copper")
    mas, slave = aedt_app.assign_master_slave(
        aedt_app.modeler["Rectangle1"].edges[0].id,
        aedt_app.modeler["Rectangle1"].edges[2].id,
    )
    assert mas.properties["Type"] == "Independent"
    assert slave.properties["Type"] == "Dependent"
    assert mas.props["Edges"][0] == aedt_app.modeler["Rectangle1"].edges[0].id
    assert slave.props["Edges"][0] == aedt_app.modeler["Rectangle1"].edges[2].id
    mas, slave = aedt_app.assign_master_slave(
        aedt_app.modeler["Rectangle1"].edges[0].id, aedt_app.modeler["Rectangle1"].edges[2].id, boundary="my_bound"
    )
    assert mas.name == "my_bound"
    assert slave.name == "my_bound_dep"
    with pytest.raises(AEDTRuntimeError, match=r"Failed to create boundary Dependent Dependent_[A-Za-z0-9]*$"):
        aedt_app.assign_master_slave(
            aedt_app.modeler["Rectangle1"].edges[0].id,
            aedt_app.modeler["Rectangle1"].edges[1].id,
        )


def test_check_design_preview_image(test_tmp_dir, aedt_app):
    jpg_file = test_tmp_dir / "file.jpg"
    assert aedt_app.export_design_preview_to_jpg(jpg_file)


def test_model_depth(aedt_app):
    assert aedt_app.change_design_settings({"ModelDepth": "3mm"})


def test_apply_skew(aedt_app):
    assert aedt_app.apply_skew()
    with pytest.raises(ValueError, match="Invalid skew type."):
        assert not aedt_app.apply_skew(skew_type="Invalid")
    with pytest.raises(ValueError, match="Invalid skew angle unit."):
        aedt_app.apply_skew(skew_type="Continuous", skew_part="Stator", skew_angle="0.5", skew_angle_unit="Invalid")
    with pytest.raises(ValueError, match="Please provide skew angles for each slice."):
        aedt_app.apply_skew(skew_type="User Defined", number_of_slices="4", custom_slices_skew_angles=["1", "2", "3"])
    assert aedt_app.apply_skew(
        skew_type="User Defined", number_of_slices="4", custom_slices_skew_angles=["1", "2", "3", "4"]
    )


def test_assign_movement(aedt_app):
    aedt_app.xy_plane = True
    aedt_app.modeler.create_circle([0, 0, 0], 10, name="Circle_inner")
    aedt_app.modeler.create_circle([0, 0, 0], 30, name="Circle_outer")
    bound = aedt_app.assign_rotate_motion("Circle_outer", positive_limit=300, mechanical_transient=True)
    assert bound
    assert bound.props["PositivePos"] == "300deg"
    assert bound.props["Objects"][0] == "Circle_outer"


def test_delete_motion_setup(aedt_app):
    aedt_app.xy_plane = True
    aedt_app.modeler.create_circle([0, 0, 0], 10, name="Circle_inner")
    aedt_app.modeler.create_circle([0, 0, 0], 30, name="Circle_outer")
    bound = aedt_app.assign_rotate_motion("Circle_outer", positive_limit=300, mechanical_transient=True)
    assert bound
    assert len(aedt_app.boundaries_by_type["Band"]) == 2
    bound.delete()
    assert len(aedt_app.boundaries_by_type["Band"]) == 1


def test_change_inductance_computation(aedt_app):
    assert aedt_app.change_inductance_computation()
    assert aedt_app.change_inductance_computation(True, False)
    assert aedt_app.change_inductance_computation(False, False)


def test_initial_mesh_settings(aedt_app):
    assert aedt_app.mesh.initial_mesh_settings
    assert aedt_app.mesh.initial_mesh_settings.props


def test_assign_end_connection(aedt_app):
    rect = aedt_app.modeler.create_rectangle([0, 0, 0], [5, 5], material="aluminum")
    rect2 = aedt_app.modeler.create_rectangle([15, 20, 0], [5, 5], material="aluminum")
    bound = aedt_app.assign_end_connection([rect, rect2])
    assert bound
    assert bound.props["ResistanceValue"] == "0ohm"
    bound.props["InductanceValue"] = "5H"
    assert bound.props["InductanceValue"] == "5H"
    with pytest.raises(AEDTRuntimeError, match="At least 2 objects are needed."):
        aedt_app.assign_end_connection([rect])
    aedt_app.solution_type = SolutionsMaxwell2D.MagnetostaticXY
    with pytest.raises(AEDTRuntimeError):
        aedt_app.assign_end_connection([rect, rect2])


def test_setup_y_connection(aedt_app):
    aedt_app.set_active_design("Y_Connections")
    assert aedt_app.setup_y_connection(["PhaseA", "PhaseB", "PhaseC"])
    assert aedt_app.setup_y_connection(["PhaseA", "PhaseB"])
    assert aedt_app.setup_y_connection()


def test_change_symmetry_multiplier(aedt_app):
    assert aedt_app.change_symmetry_multiplier(2)


def test_eddy_effects_on(aedt_app):
    assert aedt_app.eddy_effects_on(["Coil_1"], enable_eddy_effects=True)
    assert aedt_app.oboundary.GetEddyEffect("Coil_1")
    aedt_app.eddy_effects_on(["Coil_1"], enable_eddy_effects=False)
    assert not aedt_app.oboundary.GetEddyEffect("Coil_1")


def test_assign_symmetry(aedt_app):
    region = [x for x in aedt_app.modeler.object_list if x.name == "Region"]
    band = [x for x in aedt_app.modeler.object_list if x.name == "Band"]
    assert aedt_app.assign_symmetry([region[0].edges[0], band[0].edges[0]], "Symmetry_Test_IsOdd")
    assert aedt_app.assign_symmetry([region[0].edges[0], band[0].edges[0]])
    assert aedt_app.assign_symmetry([region[0].edges[0], band[0].edges[0]], "Symmetry_Test_IsEven", False)
    assert aedt_app.assign_symmetry([9556, 88656])
    with pytest.raises(ValueError, match="At least one edge must be provided."):
        aedt_app.assign_symmetry([])
    for bound in aedt_app.boundaries:
        if bound.name == "Symmetry_Test_IsOdd":
            assert bound.type == "Symmetry"
            assert bound.props["IsOdd"]
        if bound.name == "Symmetry_Test_IsEven":
            assert bound.type == "Symmetry"
            assert not bound.props["IsOdd"]


def test_assign_current_density(sinusoidal):
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


def test_set_variable(aedt_app):
    aedt_app.variable_manager.set_variable("var_test", expression="123")
    aedt_app["var_test"] = "234"
    assert "var_test" in aedt_app.variable_manager.design_variable_names
    assert aedt_app.variable_manager.design_variables["var_test"].expression == "234"


def test_cylindrical_gap(aedt_app):
    assert not aedt_app.mesh.assign_cylindrical_gap("Band")
    [
        x.delete()
        for x in aedt_app.mesh.meshoperations[:]
        if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    ]
    assert aedt_app.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test")
    assert not aedt_app.mesh.assign_cylindrical_gap(["Band", "Region"])
    assert not aedt_app.mesh.assign_cylindrical_gap("Band")
    [
        x.delete()
        for x in aedt_app.mesh.meshoperations[:]
        if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    ]
    assert aedt_app.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test", band_mapping_angle=2)


def test_skin_depth(aedt_app):
    edge = aedt_app.modeler["Rotor_Section1"].edges[0]
    mesh = aedt_app.mesh.assign_skin_depth(assignment=edge, skin_depth="0.3mm", layers_number=3)
    assert mesh
    assert mesh.type == "SkinDepthBased"
    assert mesh.props["Edges"][0] == edge.id
    assert mesh.props["SkinDepth"] == "0.3mm"
    assert mesh.props["NumLayers"] == 3
    edge1 = aedt_app.modeler["Rotor_Section1"].edges[1]
    mesh = aedt_app.mesh.assign_skin_depth(assignment=edge1.id, skin_depth="0.3mm", layers_number=3)
    assert mesh
    assert mesh.type == "SkinDepthBased"
    assert mesh.props["Edges"][0] == edge1.id
    assert mesh.props["SkinDepth"] == "0.3mm"
    assert mesh.props["NumLayers"] == 3


def test_start_continue_from_previous_setup(test_tmp_dir, aedt_app):
    assert aedt_app.setups[0].start_continue_from_previous_setup(design="Y_Connections", solution="Setup1 : Transient")
    assert aedt_app.setups[0].props["PrevSoln"]["Project"] == "This Project*"
    assert aedt_app.setups[0].props["PrevSoln"]["Design"] == "Y_Connections"
    assert aedt_app.setups[0].props["PrevSoln"]["Soln"] == "Setup1 : Transient"
    assert not aedt_app.setups[0].start_continue_from_previous_setup(design="", solution="Setup1 : Transient")
    assert not aedt_app.setups[0].start_continue_from_previous_setup(design="Y_Connections", solution="")
    assert not aedt_app.setups[0].start_continue_from_previous_setup(design="", solution="")
    example_project = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / (TEST_NAME + ".aedt")
    example_project_copy = test_tmp_dir / (TEST_NAME + "_copy.aedt")
    shutil.copy2(example_project, example_project_copy)
    assert example_project_copy.exists()
    aedt_app.create_setup(name="test_setup")
    assert aedt_app.setups[1].start_continue_from_previous_setup(
        design="Y_Connections", solution="Setup1 : Transient", project=example_project_copy
    )
    assert aedt_app.setups[1].props["PrevSoln"]["Project"] == str(example_project_copy)
    assert aedt_app.setups[1].props["PrevSoln"]["Design"] == "Y_Connections"
    assert aedt_app.setups[1].props["PrevSoln"]["Soln"] == "Setup1 : Transient"


def test_design_excitations_by_type(aedt_app):
    coils = aedt_app.excitations_by_type["Coil"]
    assert coils
    assert len(coils) == len([bound for bound in aedt_app.design_excitations.values() if bound.type == "Coil"])
    currents = aedt_app.excitations_by_type["Current"]
    assert currents
    assert len(currents) == len([bound for bound in aedt_app.design_excitations.values() if bound.type == "Current"])
    wdg_group = aedt_app.excitations_by_type["Winding Group"]
    assert wdg_group
    assert len(wdg_group) == len(
        [bound for bound in aedt_app.design_excitations.values() if bound.type == "Winding Group"]
    )


def test_boundaries_by_type(aedt_app):
    coils = aedt_app.boundaries_by_type["Coil"]
    assert coils
    assert len(coils) == len([bound for bound in aedt_app.boundaries if bound.type == "Coil"])
    currents = aedt_app.boundaries_by_type["Current"]
    assert currents
    assert len(currents) == len([bound for bound in aedt_app.boundaries if bound.type == "Current"])
    wdg_group = aedt_app.boundaries_by_type["Winding Group"]
    assert wdg_group
    assert len(wdg_group) == len([bound for bound in aedt_app.boundaries if bound.type == "Winding Group"])


def test_export_field_file(test_tmp_dir, m2d_fields):
    output_file = test_tmp_dir / "e_tang_field.fld"
    assert m2d_fields.post.export_field_file(
        quantity="E_Line", output_file=output_file, assignment="Poly1", objects_type="Line"
    )
    assert output_file.exists()


def test_control_program(m2d_ctrl_prg):
    user_ctl_path = Path("user.ctl")
    ctrl_prg_path = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / CTRL_PRG_FILE
    assert m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path)
    assert m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path, control_program_args="3")
    assert not m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path, control_program_args=3)
    assert m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path, call_after_last_step=True)
    invalid_ctrl_prg_path = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "invalid.py"
    assert not m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=invalid_ctrl_prg_path)
    m2d_ctrl_prg.solution_type = SolutionsMaxwell2D.EddyCurrentXY
    assert not m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path)
    if user_ctl_path.exists():
        user_ctl_path.unlink()


@pytest.mark.skipif(NON_GRAPHICAL, reason="Test fails on build machine")
def test_import_dxf(m2d_app):
    dxf_file = Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "DXF" / "dxf2.dxf"
    dxf_layers = get_dxf_layers(dxf_file)
    assert isinstance(dxf_layers, list)
    assert m2d_app.import_dxf(dxf_file, dxf_layers)
    dxf_layers = ["invalid", "invalid1"]
    assert not m2d_app.import_dxf(dxf_file, dxf_layers)


def test_assign_floating(m2d_app):
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


def test_matrix(m2d_app):
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


def test_solution_types_setup(m2d_app):
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


def test_create_external_circuit(m2d_app):
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


def test_assign_voltage(m2d_app):
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


def test_set_save_fields(m2d_setup):
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
    assert setup.set_save_fields(enable=True, range_type="Custom", subrange_type="SinglePoints", start=3, units="ms")
    assert len(setup.props["SweepRanges"]["Subrange"]) == 4
    assert setup.props["SweepRanges"]["Subrange"][3]["RangeType"] == "SinglePoints"
    assert setup.props["SweepRanges"]["Subrange"][3]["RangeStart"] == "3ms"
    assert setup.props["SweepRanges"]["Subrange"][3]["RangeEnd"] == "3ms"
    assert setup.set_save_fields(enable=True, range_type="Every N Steps", start=0, stop=10, count=1, units="ms")
    assert setup.props["SaveFieldsType"] == "Every N Steps"
    assert setup.props["Steps From"] == "0ms"
    assert setup.props["Steps To"] == "10ms"
    assert setup.props["N Steps"] == "1"
    assert setup.set_save_fields(enable=True, range_type="Custom", subrange_type="SinglePoints", start=3, units="ms")
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
    DESKTOP_VERSION < "2025.1",
    reason="Not working in non-graphical in version lower than 2025.1",
)
def test_eddy_current_sweep(m2d_setup):
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


def test_export_c_matrix(test_tmp_dir, m2d_export_matrix):
    output_file = test_tmp_dir / "c_matrix.txt"
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

    assert m2d_export_matrix.setups[0].export_matrix(matrix_type="C", matrix_name="Matrix1", output_file=output_file)
    assert output_file.exists()

    with pytest.raises(AEDTRuntimeError):
        m2d_export_matrix.export_c_matrix(matrix_name="invalid", output_file=output_file)

    m2d_export_matrix.set_active_design("export_c_electrostatic_param")

    assert m2d_export_matrix.export_c_matrix(matrix_name="Matrix1", output_file=output_file)
    assert output_file.exists()

    assert m2d_export_matrix.setups[0].export_matrix(matrix_type="C", matrix_name="Matrix1", output_file=output_file)
    assert output_file.exists()

    with pytest.raises(AEDTRuntimeError):
        m2d_export_matrix.setups[0].export_matrix(matrix_type="invalid", matrix_name="Matrix1", output_file=output_file)

    output_file = test_tmp_dir / "c_matrix.csv"
    with pytest.raises(AEDTRuntimeError):
        m2d_export_matrix.export_c_matrix(matrix_name="Matrix1", output_file=output_file)


def test_export_rl_matrix(test_tmp_dir, m2d_export_matrix):
    # invalid path
    export_path = test_tmp_dir / "export_rl_matrix.csv"
    with pytest.raises(AEDTRuntimeError):
        m2d_export_matrix.export_rl_matrix("Matrix1", export_path)

    export_path = test_tmp_dir / "export_rl_matrix.txt"
    # invalid solution type
    m2d_export_matrix.set_active_design("export_rl_magneto")
    with pytest.raises(AEDTRuntimeError):
        m2d_export_matrix.export_rl_matrix("Matrix1", export_path)
    # no matrix
    m2d_export_matrix.set_active_design("export_rl_eddycurrent_no_matrix")
    with pytest.raises(AEDTRuntimeError):
        m2d_export_matrix.export_rl_matrix("Matrix1", export_path)
    # no setup
    if DESKTOP_VERSION < "2025.2":  # AEDT API not raising exception
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
    export_path_1 = test_tmp_dir / "export_rl_matrix_1.txt"
    assert m2d_export_matrix.export_rl_matrix("Matrix1", export_path_1, False, 10, 3, True)
    assert export_path_1.exists()
    export_path_2 = test_tmp_dir / "export_rl_matrix_2.txt"
    assert m2d_export_matrix.setups[0].export_matrix(matrix_type="RL", matrix_name="Matrix1", output_file=export_path_2)
    assert export_path_2.exists()


def test_analyze_from_zero(m2d_app):
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
