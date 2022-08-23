import os

from _unittest.conftest import BasisTest  # Setup paths for module imports
from _unittest.conftest import config  # Setup paths for module imports
from _unittest.conftest import desktop_version  # Setup paths for module imports
from pyaedt import Hfss
from pyaedt import Icepak
from pyaedt import Mechanical

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

test_project_name = "coax_Mech"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, application=Mechanical, solution_type="Thermal")

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_save(self):
        test_project = os.path.join(self.local_scratch.path, test_project_name + ".aedt")
        self.aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        o = self.aedtapp.modeler.create_cylinder(
            self.aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass"
        )
        assert isinstance(o.id, int)

    def test_03_assign_convection(self):
        face = self.aedtapp.modeler["MyCylinder"].faces[0].id
        assert self.aedtapp.assign_uniform_convection(face, 3)

    def test_04_assign_temperature(self):
        face = self.aedtapp.modeler["MyCylinder"].faces[1].id
        bound = self.aedtapp.assign_uniform_temperature(face, "35deg")
        assert bound.props["Temperature"] == "35deg"

    def test_05_assign_load(self):
        hfss = Hfss(specified_version=desktop_version)
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        id1 = hfss.modeler.create_cylinder(self.aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        setup = hfss.create_setup()
        freq = "1GHz"
        setup.props["Frequency"] = freq
        ids_faces = [i.id for i in hfss.modeler["MyCylinder"].faces]
        assert self.aedtapp.assign_em_losses(
            hfss.design_name,
            hfss.setups[0].name,
            "LastAdaptive",
            freq,
        )

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["Solver"] = "Direct"
        assert mysetup.update()

    @pytest.mark.skipif(config["desktopVersion"] < "2021.2", reason="Skipped on versions lower than 2021.2")
    def test_07_assign_thermal_loss(self):
        ipk = Icepak(
            solution_type=self.aedtapp.SOLUTIONS.Icepak.SteadyTemperatureAndFlow, specified_version=desktop_version
        )
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        id1 = ipk.modeler.create_cylinder(ipk.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        setup = ipk.create_setup()
        mech = Mechanical(solution_type=self.aedtapp.SOLUTIONS.Mechanical.Structural, specified_version=desktop_version)
        mech.modeler.create_cylinder(mech.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        assert mech.assign_thermal_map("MyCylinder", ipk.design_name)

    def test_07_assign_mechanical_boundaries(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        mech = Mechanical(solution_type=self.aedtapp.SOLUTIONS.Mechanical.Modal, specified_version=desktop_version)
        mech.modeler.create_cylinder(mech.PLANE.XY, udp, 3, coax_dimension, 0, "MyCylinder", "brass")
        assert mech.assign_fixed_support(mech.modeler["MyCylinder"].faces[0].id)
        assert mech.assign_frictionless_support(mech.modeler["MyCylinder"].faces[1].id)

        mech = Mechanical(solution_type=self.aedtapp.SOLUTIONS.Mechanical.Thermal)
        assert not mech.assign_fixed_support(mech.modeler["MyCylinder"].faces[0].id)
        assert not mech.assign_frictionless_support(mech.modeler["MyCylinder"].faces[0].id)

    def test_08_mesh_settings(self):
        assert self.aedtapp.mesh.initial_mesh_settings
        assert self.aedtapp.mesh.initial_mesh_settings.props
