#!/ekm/software/anaconda3/bin/python
# Standard imports
import filecmp
import os
from collections import OrderedDict

from _unittest.conftest import BasisTest
from _unittest.conftest import local_path
from pyaedt import Maxwell2d
from pyaedt.generic.constants import SOLUTIONS
from pyaedt.generic.general_methods import generate_unique_name

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(
            self, project_name="Motor_EM_R2019R3", design_name="Basis_Model_For_Test", application=Maxwell2d
        )

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_03_assign_initial_mesh_from_slider(self):
        assert self.aedtapp.mesh.assign_initial_mesh_from_slider(4)
        self.aedtapp.set_active_design("Basis_Model_For_Test")

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
        self.aedtapp.export_design_preview_to_jpg(jpg_file)
        assert filecmp.cmp(jpg_file, os.path.join(local_path, "example_models", "Motor_EM_R2019R3.jpg"))

    def test_14a_model_depth(self):
        self.aedtapp.model_depth = 2.0
        assert self.aedtapp.change_design_settings({"ModelDepth": "3mm"})

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
        self.aedtapp.set_active_design("Y_Connections")
        assert not self.aedtapp.export_rl_matrix("Test1", " ")
        self.aedtapp.solution_type = SOLUTIONS.Maxwell2d.EddyCurrentXY
        self.aedtapp.assign_matrix(sources=["Current_1", "Current_2"], matrix_name="Test1")
        self.aedtapp.assign_matrix(sources=["PhaseA", "PhaseB", "PhaseC"], matrix_name="Test2")
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
