# Import required modules
from _unittest.conftest import BasisTest

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name="Test44")

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_create_rectangular_patch_w_probe(self):
        patch = self.aedtapp.antennas.rectangular_patch_probe()
        assert patch.frequency == 10.0
        patch.position = [10, 20, 0]
        assert patch.position == [10, 20, 0]

        patch2 = self.aedtapp.antennas.rectangular_patch_probe(
            material="Duroid (tm)",
            huygens_box=True,
            outer_boundary="Radiation",
            position=[10, 20, 30],
            antenna_name="Antenna_new",
        )
        assert len(patch2.boundaries) == 3
        # Change CS
        cs1 = self.aedtapp.modeler.create_coordinate_system(origin=[200, 100, 0], name="CS1")
        patch.coordinate_system = cs1.name
        assert len(patch2.object_list) == 9
        # New Patch
        patch3 = self.aedtapp.antennas.rectangular_patch_probe(
            frequency=20.0,
            frequency_unit="GHz",
            material="Duroid (tm)",
            outer_boundary=None,
            huygens_box=True,
            substrate_height=0.16,
            length_unit="cm",
            coordinate_system="CS1",
            antenna_name="Antenna_new",
            position=[1, 100, 50],
        )
        patch3.coordinate_system = cs1.name
        patch3.antenna_name = "Patch_new"
        patch3.frequency = 18.0
        patch3.frequency_unit = "MHz"
        patch3.frequency_unit = "GHz"

        patches = patch.duplicate_along_line([50, 0, 0], 3)
        assert len(patches) == 2

        assert patch2.create_3dcomponent()
        assert patch3.create_3dcomponent(replace=True)
