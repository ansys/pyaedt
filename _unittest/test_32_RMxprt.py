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

    def test_06a_create_setup(self):
        mysetup = self.aedtapp.create_setup()
        mysetup.props["RatedOutputPower"] = "100W"
        assert mysetup.update()
