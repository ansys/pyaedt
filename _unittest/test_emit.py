# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path

# Import required modules
from pyaedt import Emit
from pyaedt.generic.filesystem import Scratch
import gc
import os


class TestClass:

    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Emit()

    def teardown_class(self):
        assert self.aedtapp.close_project()
        self.local_scratch.remove()
        gc.collect()

    def test_objects(self):
        assert self.aedtapp.solution_type
        assert isinstance(self.aedtapp.existing_analysis_setups, list)
        assert isinstance(self.aedtapp.setup_names, list)
        assert self.aedtapp.modeler
        assert self.aedtapp.oanalysis is None
