#!/ekm/software/anaconda3/bin/python

# Standard imports
import filecmp
import os

# Import required modules
from pyaedt import Maxwell2d
from pyaedt.generic.constants import SOLUTIONS
from _unittest.conftest import BasisTest, local_path, pyaedt_unittest_check_desktop_error

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


class TestClass(BasisTest):
    def setup_class(self):
        BasisTest.setup_class(
            self, project_name="Motor_EM_R2019R3", design_name="Basis_Model_For_Test", application=Maxwell2d
        )

    @pyaedt_unittest_check_desktop_error
    def test_03_assign_initial_mesh_from_slider(self):
        assert self.aedtapp.mesh.assign_initial_mesh_from_slider(4)

    @pyaedt_unittest_check_desktop_error
    def test_04_create_winding(self):

        bounds = self.aedtapp.assign_winding(current_value=20e-3, coil_terminals=["Coil"])
        assert bounds
        o = self.aedtapp.modeler.primitives.create_rectangle([0, 0, 0], [3, 1], name="Rectangle2", matname="copper")
        bounds = self.aedtapp.assign_winding(current_value=20e-3, coil_terminals=o.id)
        assert bounds

    @pyaedt_unittest_check_desktop_error
    def test_05_create_vector_potential(self):
        region = self.aedtapp.modeler.primitives["Region"]
        edge_object = region.edges[0]
        bounds = self.aedtapp.assign_vector_potential(edge_object.id, 3)
        assert bounds
        assert bounds.props["Value"] == "3"
        line = self.aedtapp.modeler.primitives.create_polyline([[0, 0, 0], [1, 0, 1]], name="myline")
        bound2 = self.aedtapp.assign_vector_potential(line.id, 2)
        assert bound2
        assert bound2.props["Value"] == "2"
        assert bound2.update()

    @pyaedt_unittest_check_desktop_error
    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["SaveFields"] = True
        assert mysetup.update()

    @pyaedt_unittest_check_desktop_error
    def test_08_generate_design_data(self):
        assert self.aedtapp.generate_design_data()

    @pyaedt_unittest_check_desktop_error
    def test_09_read_design_data(self):
        assert self.aedtapp.read_design_data()

    @pyaedt_unittest_check_desktop_error
    def test_10_assign_torque(self):
        assert self.aedtapp.assign_torque("Rotor_Section1")

    @pyaedt_unittest_check_desktop_error
    def test_11_assign_force(self):
        assert self.aedtapp.assign_force("Magnet2_Section1")

    @pyaedt_unittest_check_desktop_error
    def test_12_assign_current_source(self):
        coil = self.aedtapp.modeler.primitives.create_circle(
            position=[0, 0, 0], radius="5", num_sides="8", is_covered=True, name="Coil", matname="Copper"
        )
        assert self.aedtapp.assign_current([coil])
        assert not self.aedtapp.assign_current([coil.faces[0].id])

    @pyaedt_unittest_check_desktop_error
    def test_13_assign_master_slave(self):
        mas, slave = self.aedtapp.assign_master_slave(
            self.aedtapp.modeler.primitives["Rectangle2"].edges[0].id,
            self.aedtapp.modeler.primitives["Rectangle2"].edges[2].id,
        )
        assert "Independent" in mas.name
        assert "Dependent" in slave.name

    @pyaedt_unittest_check_desktop_error
    def test_14_check_design_preview_image(self):
        jpg_file = os.path.join(self.local_scratch.path, "file.jpg")
        self.aedtapp.export_design_preview_to_jpg(jpg_file)
        assert filecmp.cmp(jpg_file, os.path.join(local_path, "example_models", "Motor_EM_R2019R3.jpg"))

    @pyaedt_unittest_check_desktop_error
    def test_15_assign_movement(self):
        self.aedtapp.insert_design("Motion")
        self.aedtapp.solution_type = SOLUTIONS.Maxwell2d.TransientXY
        self.aedtapp.modeler.primitives.create_circle([0, 0, 0], 10, name="Circle_inner")
        self.aedtapp.modeler.primitives.create_circle([0, 0, 0], 30, name="Circle_outer")
        bound = self.aedtapp.assign_rotate_motion("Circle_outer", positive_limit=300, mechanical_transient=True)
        assert bound
        assert bound.props["PositivePos"] == "300deg"

    @pyaedt_unittest_check_desktop_error
    def test_16_enable_inductance_computation(self):
        assert self.aedtapp.change_inductance_computation()
        assert self.aedtapp.change_inductance_computation(True, False)
        assert self.aedtapp.change_inductance_computation(False, False)
