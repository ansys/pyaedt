import os
# Setup paths for module imports
from _unittest.conftest import scratch_path, config
import gc
# Import required modules
from pyaedt import Hfss, Mechanical, Icepak
from pyaedt.generic.filesystem import Scratch
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

test_project_name = "coax_Mech"


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Mechanical(solution_type="Thermal")

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_save(self):
        test_project = os.path.join(self.local_scratch.path, test_project_name + ".aedt")
        self.aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        o = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                                     "MyCylinder", "brass")
        assert isinstance(o.id, int)

    def test_03_assign_convection(self):
        face = self.aedtapp.modeler.primitives["MyCylinder"].faces[0].id
        assert self.aedtapp.assign_uniform_convection(face, 3)

    def test_04_assign_temperature(self):
        face = self.aedtapp.modeler.primitives["MyCylinder"].faces[1].id
        bound= self.aedtapp.assign_uniform_temperature(face, "35deg")
        assert bound.props["Temperature"] == "35deg"

    def test_05_assign_load(self):
        hfss = Hfss()
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        id1 = hfss.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                                     "MyCylinder", "brass")
        setup=hfss.create_setup()
        freq="1GHz"
        setup.props["Frequency"]=freq
        ids_faces = [i.id for i in hfss.modeler.primitives["MyCylinder"].faces]
        assert self.aedtapp.assign_em_losses(
            hfss.design_name, hfss.setups[0].name, "LastAdaptive", freq, )

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["Solver"] = "Direct"
        assert mysetup.update()

    @pytest.mark.skipif(config["desktopVersion"] < "2021.2", reason="Skipped on versions lower than 2021.2")
    def test_07_assign_thermal_loss(self):
        ipk = Icepak(solution_type=self.aedtapp.SolutionTypes.Icepak.SteadyTemperatureAndFlow)
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        id1 = ipk.modeler.primitives.create_cylinder(ipk.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                                     "MyCylinder", "brass")
        setup = ipk.create_setup()
        mech = Mechanical(solution_type=self.aedtapp.SolutionTypes.Mechanical.Structural)
        mech.modeler.primitives.create_cylinder(mech.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                               "MyCylinder", "brass")
        assert mech.assign_thermal_map("MyCylinder", ipk.design_name)

    def test_07_assign_mechanical_boundaries(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 30
        mech = Mechanical(solution_type=self.aedtapp.SolutionTypes.Mechanical.Modal)
        mech.modeler.primitives.create_cylinder(mech.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                               "MyCylinder", "brass")
        assert mech.assign_fixed_support(mech.modeler.primitives["MyCylinder"].faces[0].id)
        assert mech.assign_frictionless_support(mech.modeler.primitives["MyCylinder"].faces[1].id)
