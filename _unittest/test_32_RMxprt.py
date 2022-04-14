import os

from _unittest.conftest import BasisTest
from pyaedt import Rmxprt

test_project_name = "motor"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, application=Rmxprt)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_save(self):
        test_project = os.path.join(self.local_scratch.path, test_project_name + ".aedt")
        self.aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_02_changeesolution(self):
        assert self.aedtapp.disable_modelcreation("ORIM")
        assert self.aedtapp.disable_modelcreation("AFIM")
        assert self.aedtapp.disable_modelcreation("HM")
        assert self.aedtapp.disable_modelcreation("LSSM")
        assert self.aedtapp.disable_modelcreation("UNIM")
        assert self.aedtapp.disable_modelcreation("LSSM")
        assert self.aedtapp.enable_modelcreation("WRIM")

    def test_03_getchangeproperty(self):
        # test increment statorOD by 1mm
        self.aedtapp.disable_modelcreation("ASSM")
        statorOD = self.aedtapp.stator["Outer Diameter"]
        assert statorOD
        self.aedtapp.stator["Outer Diameter"] = statorOD + "+1mm"

    def test_04_create_setup(self):
        # first test GRM (use Inner-Rotor Induction Machine)
        assert self.aedtapp.enable_modelcreation("IRIM")
        mysetup = self.aedtapp.create_setup()
        assert mysetup.props["RatedOutputPower"]
        mysetup.props["RatedOutputPower"] = "100W"
        assert mysetup.update()  # update only needed for assertion
        # second test ASSM setup
        self.aedtapp.delete_setup(mysetup.name)
        assert self.aedtapp.disable_modelcreation("ASSM")
        mysetup = self.aedtapp.create_setup()
        assert mysetup.props["RatedSpeed"]
        mysetup.props["RatedSpeed"] = "3600rpm"
        assert mysetup.update()  # update only needed for assertion
        # third test TPSM/SYNM setup
        self.aedtapp.delete_setup(mysetup.name)
        assert self.aedtapp.disable_modelcreation("TPSM")
        mysetup = self.aedtapp.create_setup()
        assert mysetup.props["RatedVoltage"]
        mysetup.props["RatedVoltage"] = "208V"
        assert mysetup.update()  # update only needed for assertion
