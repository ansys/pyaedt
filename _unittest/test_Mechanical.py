import os
# Setup paths for module imports
from .conftest import scratch_path
import gc
# Import required modules
from pyaedt import Hfss, Mechanical
from pyaedt.generic.filesystem import Scratch

test_project_name = "coax_Mech"


class TestMechanical:
    def setup_class(self):
        #self.desktop = Desktop(desktopVersion, NonGraphical, NewThread)
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
        id1 = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                                     "MyCylinder", "brass")
        assert isinstance(id1, int)

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
        ids_faces=[i.id for i in hfss.modeler.primitives["MyCylinder"].faces]
        assert self.aedtapp.assign_em_losses(hfss.design_name, hfss.setups[0].name, "LastAdaptive", freq, )

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["Solver"] = "Direct"
        assert mysetup.update()








