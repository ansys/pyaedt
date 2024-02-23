#!/ekm/software/anaconda3/bin/python
from collections import OrderedDict
import os
import shutil

from _unittest.conftest import config
from _unittest.conftest import local_path
import pytest

from pyaedt import Maxwell2d
from pyaedt.generic.constants import SOLUTIONS
from pyaedt.generic.general_methods import generate_unique_name

test_subfolder = "TMaxwell"
if config["desktopVersion"] > "2022.2":
    test_name = "Motor_EM_R2019R3_231"
else:
    test_name = "Motor_EM_R2019R3"

ctrl_prg = "TimeStepCtrl"
ctrl_prg_file = "timestep_only.py"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(
        project_name=test_name, design_name="Basis_Model_For_Test", application=Maxwell2d, subfolder=test_subfolder
    )
    if config["desktopVersion"] < "2023.1":
        app.duplicate_design("design_for_test")
        app.set_active_design("Basis_Model_For_Test")
    return app


@pytest.fixture(scope="class")
def m2d_ctrl_prg(add_app):
    app = add_app(application=Maxwell2d, project_name=ctrl_prg, subfolder=test_subfolder)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, m2d_ctrl_prg, local_scratch):
        self.aedtapp = aedtapp
        self.m2d_ctrl_prg = m2d_ctrl_prg
        self.local_scratch = local_scratch

    def test_03_assign_initial_mesh_from_slider(self):
        assert self.aedtapp.mesh.assign_initial_mesh_from_slider(4)

    def test_04_create_winding(self):
        bounds = self.aedtapp.assign_winding(current_value=20e-3, coil_terminals=["Coil"])
        assert bounds
        o = self.aedtapp.modeler.create_rectangle([0, 0, 0], [3, 1], name="Rectangle2", matname="copper")
        bounds = self.aedtapp.assign_winding(current_value=20e-3, coil_terminals=o.id)
        assert bounds
        bounds = self.aedtapp.assign_winding(current_value="20e-3A", coil_terminals=["Coil"])
        assert bounds
        bounds = self.aedtapp.assign_winding(res="1ohm", coil_terminals=["Coil"])
        assert bounds
        bounds = self.aedtapp.assign_winding(ind="1H", coil_terminals=["Coil"])
        assert bounds
        bounds = self.aedtapp.assign_winding(voltage="10V", coil_terminals=["Coil"])
        assert bounds
        bounds_name = generate_unique_name("Coil")
        bounds = self.aedtapp.assign_winding(coil_terminals=["Coil"], name=bounds_name)
        assert bounds_name == bounds.name

    def test_04a_assign_coil(self):
        bound = self.aedtapp.assign_coil(input_object=["Coil"])
        assert bound
        polarity = "Positive"
        bound = self.aedtapp.assign_coil(input_object=["Coil"], polarity=polarity)
        assert bound.props["PolarityType"] == polarity.lower()
        polarity = "Negative"
        bound = self.aedtapp.assign_coil(input_object=["Coil"], polarity=polarity)
        assert bound.props["PolarityType"] == polarity.lower()
        bound_name = generate_unique_name("Coil")
        bound = self.aedtapp.assign_coil(input_object=["Coil"], name=bound_name)
        assert bound_name == bound.name

    def test_05_create_vector_potential(self):
        region = self.aedtapp.modeler["Region"]
        edge_object = region.edges[0]
        bounds = self.aedtapp.assign_vector_potential(edge_object.id, 3)
        assert bounds
        assert bounds.props["Value"] == "3"
        bounds["Value"] = "2"
        assert bounds.props["Value"] == "2"
        line = self.aedtapp.modeler.create_polyline([[0, 0, 0], [1, 0, 1]], name="myline")
        bound2 = self.aedtapp.assign_vector_potential(line.id, 2)
        assert bound2
        assert bound2.props["Value"] == "2"
        assert bound2.update()

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()

    def test_07_create_vector_potential(self):
        region = self.aedtapp.modeler["Region"]
        self.aedtapp.assign_balloon(region.edges)

    def test_08_generate_design_data(self):
        assert self.aedtapp.generate_design_data()

    def test_09_read_design_data(self):
        assert self.aedtapp.read_design_data()

    def test_10_assign_torque(self):
        T = self.aedtapp.assign_torque("Rotor_Section1")
        assert T.type == "Torque"
        assert T.props["Objects"][0] == "Rotor_Section1"
        assert T.props["Is Positive"]
        assert T.delete()
        T = self.aedtapp.assign_torque(input_object="Rotor_Section1", is_positive=False, torque_name="Torque_Test")
        assert T.name == "Torque_Test"
        assert not T.props["Is Positive"]
        assert T.props["Objects"][0] == "Rotor_Section1"

    def test_11_assign_force(self):
        F = self.aedtapp.assign_force("Magnet2_Section1")
        assert F.type == "Force"
        assert F.props["Objects"][0] == "Magnet2_Section1"
        assert F.props["Reference CS"] == "Global"
        assert F.delete()
        F = self.aedtapp.assign_force(input_object="Magnet2_Section1", force_name="Force_Test")
        assert F.name == "Force_Test"

    def test_12_assign_current_source(self):
        coil = self.aedtapp.modeler.create_circle(
            position=[0, 0, 0], radius=5, num_sides="8", is_covered=True, name="Coil", matname="Copper"
        )
        assert self.aedtapp.assign_current([coil])
        assert not self.aedtapp.assign_current([coil.faces[0].id])

    def test_13_assign_master_slave(self):
        mas, slave = self.aedtapp.assign_master_slave(
            self.aedtapp.modeler["Rectangle2"].edges[0].id,
            self.aedtapp.modeler["Rectangle2"].edges[2].id,
        )
        assert "Independent" in mas.name
        assert "Dependent" in slave.name

    def test_14_check_design_preview_image(self):
        jpg_file = os.path.join(self.local_scratch.path, "file.jpg")
        assert self.aedtapp.export_design_preview_to_jpg(jpg_file)

    def test_14a_model_depth(self):
        self.aedtapp.model_depth = 2.0
        assert self.aedtapp.change_design_settings({"ModelDepth": "3mm"})

    def test_14b_skew_model(self):
        self.aedtapp.set_active_design("Basis_Model_For_Test")
        assert self.aedtapp.apply_skew()
        assert not self.aedtapp.apply_skew(skew_type="Invalid")
        assert not self.aedtapp.apply_skew(skew_part="Invalid")
        assert not self.aedtapp.apply_skew(
            skew_type="Continuous", skew_part="Stator", skew_angle="0.5", skew_angle_unit="Invalid"
        )
        assert not self.aedtapp.apply_skew(
            skew_type="User Defined", number_of_slices="4", custom_slices_skew_angles=["1", "2", "3"]
        )
        assert self.aedtapp.apply_skew(
            skew_type="User Defined", number_of_slices="4", custom_slices_skew_angles=["1", "2", "3", "4"]
        )

    def test_15_assign_movement(self):
        self.aedtapp.set_active_design("Y_Connections")
        self.aedtapp.insert_design("Motion")
        self.aedtapp.solution_type = SOLUTIONS.Maxwell2d.TransientZ
        self.aedtapp.xy_plane = True
        self.aedtapp.modeler.create_circle([0, 0, 0], 10, name="Circle_inner")
        self.aedtapp.modeler.create_circle([0, 0, 0], 30, name="Circle_outer")
        bound = self.aedtapp.assign_rotate_motion("Circle_outer", positive_limit=300, mechanical_transient=True)
        assert bound
        assert bound.props["PositivePos"] == "300deg"

    def test_16_enable_inductance_computation(self):
        assert self.aedtapp.change_inductance_computation()
        assert self.aedtapp.change_inductance_computation(True, False)
        assert self.aedtapp.change_inductance_computation(False, False)

    def test_17_mesh_settings(self):
        assert self.aedtapp.mesh.initial_mesh_settings
        assert self.aedtapp.mesh.initial_mesh_settings.props

    def test_18_end_connection(self):
        self.aedtapp.insert_design("EndConnection")
        self.aedtapp.solution_type = SOLUTIONS.Maxwell2d.TransientXY
        rect = self.aedtapp.modeler.create_rectangle([0, 0, 0], [5, 5], matname="aluminum")
        rect2 = self.aedtapp.modeler.create_rectangle([15, 20, 0], [5, 5], matname="aluminum")
        bound = self.aedtapp.assign_end_connection([rect, rect2])
        assert bound
        assert bound.props["ResistanceValue"] == "0ohm"
        bound.props["InductanceValue"] = "5H"
        assert bound.props["InductanceValue"] == "5H"
        assert not self.aedtapp.assign_end_connection([rect])
        self.aedtapp.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticXY
        assert not self.aedtapp.assign_end_connection([rect, rect2])

    def test_19_matrix(self):
        self.aedtapp.insert_design("Matrix")
        self.aedtapp.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticXY
        self.aedtapp.modeler.create_rectangle([0, 1.5, 0], [8, 3], is_covered=True, name="Coil_1", matname="vacuum")
        self.aedtapp.modeler.create_rectangle([8.5, 1.5, 0], [8, 3], is_covered=True, name="Coil_2", matname="vacuum")
        self.aedtapp.modeler.create_rectangle([16, 1.5, 0], [8, 3], is_covered=True, name="Coil_3", matname="vacuum")
        self.aedtapp.modeler.create_rectangle([32, 1.5, 0], [8, 3], is_covered=True, name="Coil_4", matname="vacuum")
        self.aedtapp.assign_current("Coil_1", amplitude=1, swap_direction=False, name="Current1")
        self.aedtapp.assign_current("Coil_2", amplitude=1, swap_direction=True, name="Current2")
        self.aedtapp.assign_current("Coil_3", amplitude=1, swap_direction=True, name="Current3")
        self.aedtapp.assign_current("Coil_4", amplitude=1, swap_direction=True, name="Current4")
        L = self.aedtapp.assign_matrix(sources="Current1")
        assert L.props["MatrixEntry"]["MatrixEntry"][0]["Source"] == "Current1"
        assert L.delete()
        L = self.aedtapp.assign_matrix(
            sources=["Current1", "Current2"], matrix_name="Test1", turns=2, return_path="Current3"
        )
        assert len(L.props["MatrixEntry"]["MatrixEntry"]) == 2
        L = self.aedtapp.assign_matrix(
            sources=["Current1", "Current2"], matrix_name="Test2", turns=[2, 1], return_path=["Current3", "Current4"]
        )
        assert L.props["MatrixEntry"]["MatrixEntry"][1]["ReturnPath"] == "Current4"
        L = self.aedtapp.assign_matrix(
            sources=["Current1", "Current2"], matrix_name="Test3", turns=[2, 1], return_path=["Current1", "Current1"]
        )
        assert not L
        group_sources = {"Group1_Test": ["Current3", "Current2"]}
        L = self.aedtapp.assign_matrix(
            sources=["Current3", "Current2"],
            matrix_name="Test4",
            turns=[2, 1],
            return_path=["Current4", "Current1"],
            group_sources=group_sources,
        )
        assert L.name == "Test4"
        group_sources = {"Group1_Test": ["Current3", "Current2"], "Group2_Test": ["Current1", "Current2"]}
        L = self.aedtapp.assign_matrix(
            sources=["Current1", "Current2"],
            matrix_name="Test5",
            turns=[2, 1],
            return_path="infinite",
            group_sources=group_sources,
        )
        assert L.props["MatrixGroup"]["MatrixGroup"]
        group_sources = OrderedDict()
        group_sources["Group1_Test"] = ["Current1", "Current3"]
        group_sources["Group2_Test"] = ["Current2", "Current4"]
        L = self.aedtapp.assign_matrix(
            sources=["Current1", "Current2", "Current3", "Current4"],
            matrix_name="Test6",
            turns=2,
            group_sources=group_sources,
            branches=3,
        )
        assert L.props["MatrixGroup"]["MatrixGroup"][0]["GroupName"] == "Group1_Test"
        group_sources = {"Group1_Test": ["Current1", "Current3"], "Group2_Test": ["Current2", "Current4"]}
        L = self.aedtapp.assign_matrix(
            sources=["Current1", "Current2", "Current3", "Current4"],
            matrix_name="Test7",
            turns=[5, 1],
            group_sources=group_sources,
            branches=[3, 2, 1],
        )
        assert len(L.props["MatrixGroup"]["MatrixGroup"]) == 2
        group_sources = {"Group1_Test": ["Current1", "Current3", "Current2"], "Group2_Test": ["Current2", "Current4"]}
        L = self.aedtapp.assign_matrix(
            sources=["Current1", "Current2", "Current3"],
            matrix_name="Test8",
            turns=[2, 1, 2, 3],
            return_path=["infinite", "infinite", "Current4"],
            group_sources=group_sources,
            branches=[3, 2],
        )
        assert L.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] == 2
        L.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] = 3
        assert L.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] == 3
        group_sources = {"Group1_Test": ["Current1", "Current3"], "Group2_Test": ["Current2", "Current4"]}
        L = self.aedtapp.assign_matrix(
            sources=["Current1", "Current2", "Current3", "Current4"],
            matrix_name="Test9",
            turns=[5, 1, 2, 3],
            group_sources=group_sources,
            branches=[3, 2],
        )
        for l in L.props["MatrixEntry"]["MatrixEntry"]:
            assert l["ReturnPath"] == "infinite"

    def test_20_setup_y_connection(self):
        self.aedtapp.set_active_design("Y_Connections")
        assert self.aedtapp.setup_y_connection(["PhaseA", "PhaseB", "PhaseC"])
        assert self.aedtapp.setup_y_connection(["PhaseA", "PhaseB"])  # Remove one phase from the Y connection.
        assert self.aedtapp.setup_y_connection()  # Remove the Y connection.

    def test_21_symmetry_multiplier(self):
        assert self.aedtapp.change_symmetry_multiplier(2)

    def test_22_eddycurrent(self):
        self.aedtapp.set_active_design("Basis_Model_For_Test")
        assert self.aedtapp.eddy_effects_on(["Coil_1"], activate_eddy_effects=True)
        oModule = self.aedtapp.odesign.GetModule("BoundarySetup")
        assert oModule.GetEddyEffect("Coil_1")
        self.aedtapp.eddy_effects_on(["Coil_1"], activate_eddy_effects=False)
        assert not oModule.GetEddyEffect("Coil_1")

    def test_23_read_motion_boundary(self):
        assert self.aedtapp.boundaries
        for bound in self.aedtapp.boundaries:
            if bound.name == "MotionSetup1":
                assert bound.props["MotionType"] == "Band"
                assert bound.props["InitPos"] == "Init_Pos"
                bound.props["InitPos"] = "10deg"
                assert bound.props["InitPos"] == "10deg"
                assert bound.type == "Band"

    def test_24_assign_symmetry(self):
        self.aedtapp.set_active_design("Basis_Model_For_Test")
        region = [x for x in self.aedtapp.modeler.object_list if x.name == "Region"]
        band = [x for x in self.aedtapp.modeler.object_list if x.name == "Band"]
        assert self.aedtapp.assign_symmetry([region[0].edges[0], band[0].edges[0]], "Symmetry_Test_IsOdd")
        assert self.aedtapp.assign_symmetry([region[0].edges[0], band[0].edges[0]])
        assert self.aedtapp.assign_symmetry([region[0].edges[0], band[0].edges[0]], "Symmetry_Test_IsEven", False)
        assert self.aedtapp.assign_symmetry([9556, 88656])
        assert not self.aedtapp.assign_symmetry([])
        for bound in self.aedtapp.boundaries:
            if bound.name == "Symmetry_Test_IsOdd":
                assert bound.type == "Symmetry"
                assert bound.props["IsOdd"]
            if bound.name == "Symmetry_Test_IsEven":
                assert bound.type == "Symmetry"
                assert not bound.props["IsOdd"]

    def test_25_export_rl_matrix(self):
        self.aedtapp.set_active_design("Sinusoidal")
        assert not self.aedtapp.export_rl_matrix("Test1", " ")
        self.aedtapp.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        self.aedtapp.assign_matrix(sources=["PM_I1_1_I0", "PM_I1_I0"], matrix_name="Test1")
        self.aedtapp.assign_matrix(sources=["Phase_A", "Phase_B", "Phase_C"], matrix_name="Test2")
        setup_name = "setupTestMatrixRL"
        setup = self.aedtapp.create_setup(setupname=setup_name)
        setup.props["MaximumPasses"] = 2
        export_path_1 = os.path.join(self.local_scratch.path, "export_rl_matrix_Test1.txt")
        assert not self.aedtapp.export_rl_matrix("Test1", export_path_1)
        assert not self.aedtapp.export_rl_matrix("Test2", export_path_1, False, 10, 3, True)
        self.aedtapp.validate_simple()
        self.aedtapp.analyze_setup(setup_name)
        assert self.aedtapp.export_rl_matrix("Test1", export_path_1)
        assert not self.aedtapp.export_rl_matrix("abcabc", export_path_1)
        assert os.path.exists(export_path_1)
        export_path_2 = os.path.join(self.local_scratch.path, "export_rl_matrix_Test2.txt")
        assert self.aedtapp.export_rl_matrix("Test2", export_path_2, False, 10, 3, True)
        assert os.path.exists(export_path_2)

    def test_26_assign_current_density(self):
        self.aedtapp.set_active_design("Sinusoidal")
        assert self.aedtapp.assign_current_density("Coil", "CurrentDensity_1")
        assert self.aedtapp.assign_current_density("Coil", "CurrentDensity_2", "40deg", current_density_2d="2")
        assert self.aedtapp.assign_current_density(["Coil", "Coil_1"])
        assert self.aedtapp.assign_current_density(["Coil", "Coil_1"], "CurrentDensityGroup_1")
        for bound in self.aedtapp.boundaries:
            if bound.type == "CurrentDensity":
                if bound.name == "CurrentDensity_1":
                    assert bound.props["Objects"] == ["Coil"]
                    assert bound.props["Phase"] == "0deg"
                    assert bound.props["Value"] == "0"
                    assert bound.props["CoordinateSystem"] == ""
                if bound.name == "CurrentDensity_2":
                    assert bound.props["Objects"] == ["Coil"]
                    assert bound.props["Phase"] == "40deg"
                    assert bound.props["Value"] == "2"
                    assert bound.props["CoordinateSystem"] == ""
            if bound.type == "CurrentDensityGroup":
                if bound.name == "CurrentDensityGroup_1":
                    assert bound.props["Objects"] == ["Coil", "Coil_1"]
                    assert bound.props["Phase"] == "0deg"
                    assert bound.props["Value"] == "0"
                    assert bound.props["CoordinateSystem"] == ""
        self.aedtapp.set_active_design("Motion")
        assert not self.aedtapp.assign_current_density("Circle_inner", "CurrentDensity_1")

    def test_27_add_mesh_link(self):
        self.aedtapp.save_project(self.aedtapp.project_file)
        self.aedtapp.set_active_design("Sinusoidal")
        assert self.aedtapp.setups[0].add_mesh_link(design_name="Y_Connections")
        meshlink_props = self.aedtapp.setups[0].props["MeshLink"]
        assert meshlink_props["Project"] == "This Project*"
        assert meshlink_props["PathRelativeTo"] == "TargetProject"
        assert meshlink_props["Design"] == "Y_Connections"
        assert meshlink_props["Soln"] == "Setup1 : LastAdaptive"
        assert sorted(list(meshlink_props["Params"].keys())) == sorted(self.aedtapp.available_variations.variables)
        assert sorted(list(meshlink_props["Params"].values())) == sorted(self.aedtapp.available_variations.variables)
        assert not self.aedtapp.setups[0].add_mesh_link(design_name="")
        assert self.aedtapp.setups[0].add_mesh_link(design_name="Y_Connections", solution_name="Setup1 : LastAdaptive")
        assert not self.aedtapp.setups[0].add_mesh_link(
            design_name="Y_Connections", solution_name="Setup_Test : LastAdaptive"
        )
        assert self.aedtapp.setups[0].add_mesh_link(
            design_name="Y_Connections",
            parameters_dict=self.aedtapp.available_variations.nominal_w_values_dict,
        )
        example_project = os.path.join(local_path, "example_models", test_subfolder, test_name + ".aedt")
        example_project_copy = os.path.join(self.local_scratch.path, test_name + "_copy.aedt")
        shutil.copyfile(example_project, example_project_copy)
        assert os.path.exists(example_project_copy)
        assert self.aedtapp.setups[0].add_mesh_link(
            design_name="Basis_Model_For_Test", project_name=example_project_copy
        )

    def test_28_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_31_cylindrical_gap(self):
        assert not self.aedtapp.mesh.assign_cylindrical_gap("Band")
        [
            x.delete()
            for x in self.aedtapp.mesh.meshoperations[:]
            if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
        ]
        assert self.aedtapp.mesh.assign_cylindrical_gap("Band", meshop_name="cyl_gap_test")
        assert not self.aedtapp.mesh.assign_cylindrical_gap(["Band", "Region"])
        assert not self.aedtapp.mesh.assign_cylindrical_gap("Band")
        [
            x.delete()
            for x in self.aedtapp.mesh.meshoperations[:]
            if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
        ]
        assert self.aedtapp.mesh.assign_cylindrical_gap("Band", meshop_name="cyl_gap_test", band_mapping_angle=2)

    def test_32_control_program(self):
        user_ctl_path = "user.ctl"
        ctrl_prg_path = os.path.join(local_path, "example_models", test_subfolder, ctrl_prg_file)
        assert self.m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path)
        assert self.m2d_ctrl_prg.setups[0].enable_control_program(
            control_program_path=ctrl_prg_path, control_program_args="3"
        )
        assert not self.m2d_ctrl_prg.setups[0].enable_control_program(
            control_program_path=ctrl_prg_path, control_program_args=3
        )
        assert self.m2d_ctrl_prg.setups[0].enable_control_program(
            control_program_path=ctrl_prg_path, call_after_last_step=True
        )
        invalid_ctrl_prg_path = os.path.join(local_path, "example_models", test_subfolder, "invalid.py")
        assert not self.m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=invalid_ctrl_prg_path)
        self.m2d_ctrl_prg.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        assert not self.m2d_ctrl_prg.setups[0].enable_control_program(control_program_path=ctrl_prg_path)
        if os.path.exists(user_ctl_path):
            os.unlink(user_ctl_path)

    @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    def test_33_import_dxf(self):
        self.aedtapp.insert_design("dxf")
        dxf_file = os.path.join(local_path, "example_models", "cad", "DXF", "dxf2.dxf")
        dxf_layers = self.aedtapp.get_dxf_layers(dxf_file)
        assert isinstance(dxf_layers, list)
        assert self.aedtapp.import_dxf(dxf_file, dxf_layers)

    def test_34_start_continue_from_previous_setup(self):
        self.aedtapp.set_active_design("Basis_Model_For_Test")

        assert self.aedtapp.setups[0].start_continue_from_previous_setup(
            design_name="design_for_test", solution_name="Setup1 : Transient"
        )
        assert self.aedtapp.setups[0].props["PrevSoln"]["Project"] == "This Project*"
        assert self.aedtapp.setups[0].props["PrevSoln"]["Design"] == "design_for_test"
        assert self.aedtapp.setups[0].props["PrevSoln"]["Soln"] == "Setup1 : Transient"
        assert self.aedtapp.setups[1].start_continue_from_previous_setup(
            design_name="design_for_test", solution_name="Setup1 : Transient", map_variables_by_name=False
        )
        assert self.aedtapp.setups[1].props["PrevSoln"]["Project"] == "This Project*"
        assert self.aedtapp.setups[1].props["PrevSoln"]["Design"] == "design_for_test"
        assert self.aedtapp.setups[1].props["PrevSoln"]["Soln"] == "Setup1 : Transient"
        assert not self.aedtapp.setups[0].start_continue_from_previous_setup(
            design_name="", solution_name="Setup1 : Transient"
        )
        assert not self.aedtapp.setups[0].start_continue_from_previous_setup(
            design_name="design_for_test", solution_name=""
        )
        assert not self.aedtapp.setups[0].start_continue_from_previous_setup(design_name="", solution_name="")

        example_project_copy = os.path.join(self.local_scratch.path, test_name + "_copy.aedt")
        assert os.path.exists(example_project_copy)
        self.aedtapp.create_setup(setupname="test_setup")
        assert self.aedtapp.setups[2].start_continue_from_previous_setup(
            design_name="design_for_test", solution_name="Setup1 : Transient", project_name=example_project_copy
        )
        assert self.aedtapp.setups[2].props["PrevSoln"]["Project"] == example_project_copy
        assert self.aedtapp.setups[2].props["PrevSoln"]["Design"] == "design_for_test"
        assert self.aedtapp.setups[2].props["PrevSoln"]["Soln"] == "Setup1 : Transient"

    def test_35_solution_types_setup(self, add_app):
        m2d = add_app(application=Maxwell2d, design_name="test_setups")
        m2d.solution_type = SOLUTIONS.Maxwell2d.TransientXY
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.TransientZ
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticXY
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.MagnetostaticZ
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentZ
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.ElectroStaticXY
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.ElectroStaticZ
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.DCConductionXY
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.DCConductionZ
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.ACConductionXY
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()
        m2d.solution_type = SOLUTIONS.Maxwell2d.ACConductionZ
        setup = m2d.create_setup(setuptype=m2d.solution_type)
        assert setup
        setup.delete()

    def test_36_design_excitations_by_type(self):
        coils = self.aedtapp.excitations_by_type["Coil"]
        assert coils
        assert len(coils) == len([bound for bound in self.aedtapp.design_excitations if bound.type == "Coil"])
        currents = self.aedtapp.excitations_by_type["Current"]
        assert currents
        assert len(currents) == len([bound for bound in self.aedtapp.design_excitations if bound.type == "Current"])
        wdg_group = self.aedtapp.excitations_by_type["Winding Group"]
        assert wdg_group
        assert len(wdg_group) == len(
            [bound for bound in self.aedtapp.design_excitations if bound.type == "Winding Group"]
        )

    def test_37_boundaries_by_type(self):
        coils = self.aedtapp.boundaries_by_type["Coil"]
        assert coils
        assert len(coils) == len([bound for bound in self.aedtapp.boundaries if bound.type == "Coil"])
        currents = self.aedtapp.boundaries_by_type["Current"]
        assert currents
        assert len(currents) == len([bound for bound in self.aedtapp.boundaries if bound.type == "Current"])
        wdg_group = self.aedtapp.boundaries_by_type["Winding Group"]
        assert wdg_group
        assert len(wdg_group) == len([bound for bound in self.aedtapp.boundaries if bound.type == "Winding Group"])
