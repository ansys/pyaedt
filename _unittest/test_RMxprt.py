import os
# Setup paths for module imports
from .conftest import scratch_path, desktop_version
import gc
# Import required modules
from pyaedt import Rmxprt
from pyaedt.generic.filesystem import Scratch

test_project_name = "motor"


class TestRmxprt:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Rmxprt(specified_version=desktop_version)

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

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
        mysetup.props["Rated Output Power"] = "100W"
        assert mysetup.update()






